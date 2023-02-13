from strutils import join
import ../util/strenc

# Print a file to stdout
proc cat*(args : varargs[string]) : string =
    var file = args.join(obf(" "))
    if file == "":
        result = obf("Invalid number of arguments received. Usage: 'cat [file]'.")
    else:
        result = readFile(file)