import osproc

# Execute a binary as a subprocess and return output
proc run*(args : varargs[string]) : string =

    var 
        target : string
        arguments : seq[string]

    if args.len >= 1 and args[0] != "":
        target = args[0]
        arguments = args[1 .. ^1]
    else:
        result = obf("Invalid number of arguments received. Usage: 'run [binary] <optional: arguments>'.")
        return

    result = execProcess(target, args=arguments, options={poUsePath, poStdErrToStdOut, poDaemon})