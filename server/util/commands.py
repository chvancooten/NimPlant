import shlex
import yaml
from yaml.loader import FullLoader
import server.util.func as func
from server.util.nimplant import np_server, NimPlant


def get_commands():
    with open("server/util/commands.yaml", "r", encoding="UTF-8") as f:
        return sorted(yaml.load(f, Loader=FullLoader), key=lambda c: c["command"])


def get_command_list():
    return [c["command"] for c in get_commands()]


def get_risky_command_list():
    return [c["command"] for c in get_commands() if c["risky_command"]]


def handle_command(raw_command, np: NimPlant = None):
    if np is None:
        np = np_server.get_active_nimplant()

    func.log(f"NimPlant {np.id} $ > {raw_command}", np.guid)

    try:
        cmd = raw_command.lower().split(" ")[0]
        args = shlex.split(raw_command.replace("\\", "\\\\"))[1:]
        nimplant_cmds = [cmd.lower() for cmd in get_command_list()]

        # Handle commands
        if cmd == "":
            pass

        elif cmd in get_risky_command_list() and not np.risky_mode:
            msg = (
                f"Uh oh, you compiled this Nimplant in safe mode and '{cmd}' is considered to be a risky command.\n"
                "Please enable 'riskyMode' in 'config.toml' and re-compile Nimplant!"
            )
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "cancel":
            np.cancel_all_tasks()
            func.nimplant_print(
                f"All tasks cancelled for Nimplant {np.id}.", np.guid, raw_command
            )

        elif cmd == "clear":
            func.cls()

        elif cmd == "getpid":
            msg = f"NimPlant PID is {np.pid}"
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "getprocname":
            msg = f"NimPlant is running inside of {np.pname}"
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "help":
            if len(args) >= 1:
                msg = func.get_command_help(args[0])
            else:
                msg = func.get_help_menu()

            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "hostname":
            msg = f"NimPlant hostname is: {np.hostname}"
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "ipconfig":
            msg = f"NimPlant external IP address is: {np.ip_external}\n"
            msg += f"NimPlant internal IP address is: {np.ip_internal}"
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "list":
            msg = np_server.get_nimplant_info()
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "listall":
            msg = np_server.get_nimplant_info(include_all=True)
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "nimplant":
            msg = np.get_info_pretty()
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "osbuild":
            msg = f"NimPlant OS build is: {np.os_build}"
            func.nimplant_print(msg, np.guid, raw_command)

        elif cmd == "select":
            if len(args) == 1:
                np_server.select_nimplant(args[0])
            else:
                func.nimplant_print(
                    "Invalid argument length. Usage: 'select [NimPlant ID]'.",
                    np.guid,
                    raw_command,
                )

        elif cmd == "exit":
            func.exit_server_console()

        elif cmd == "upload":
            func.upload_file(np, args, raw_command)

        elif cmd == "download":
            func.download_file(np, args, raw_command)

        elif cmd == "execute-assembly":
            func.execute_assembly(np, args, raw_command)

        elif cmd == "inline-execute":
            func.inline_execute(np, args, raw_command)

        elif cmd == "shinject":
            func.shinject(np, args, raw_command)

        elif cmd == "powershell":
            func.powershell(np, args, raw_command)

        # Handle commands that do not need any server-side handling
        elif cmd in nimplant_cmds:
            guid = np.add_task(" ".join(shlex.quote(arg) for arg in [cmd, *args]))
            func.nimplant_print(
                f"Staged command '{raw_command}'.", np.guid, task_guid=guid
            )
        else:
            func.nimplant_print(
                "Unknown command. Enter 'help' to get a list of commands.",
                np.guid,
                raw_command,
            )

    except Exception as e:
        func.nimplant_print(
            f"An unexpected exception occurred when handling command: {repr(e)}",
            np.guid,
            raw_command,
        )
