from os import dirExists, moveFile, moveDir, splitPath, `/`
from strutils import join

# Move a file or directory
proc mv*(args : varargs[string]) : string =
    var
        source : string
        destination : string

    if args.len == 2:
        source = args[0]
        destination = args[1 .. ^1].join(obf(" "))
    else:
        result = obf("Invalid number of arguments received. Usage: 'mv [source] [destination]'.")
        return

    # Moving a directory
    if dirExists(source):
        if dirExists(destination):
            moveDir(source, destination/splitPath(source).tail)
        else:
            moveDir(source, destination)

    # Moving a file
    elif dirExists(destination):
        moveFile(source, destination/splitPath(source).tail)
    else:
        moveFile(source, destination)

    result = obf("Moved '") & source & obf("' to '") & destination & obf("'.")