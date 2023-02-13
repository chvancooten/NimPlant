from os import setCurrentDir, normalizePath
from strutils import join

# Change the current working directory
proc cd*(args : varargs[string]) : string =
    var newDir = args.join(obf(" "))
    if newDir == "":
        result = obf("Invalid number of arguments received. Usage: 'cd [directory]'.")
    else:
        newDir.normalizePath()
        setCurrentDir(newDir)
        result = obf("Changed working directory to '") & newDir & obf("'.")