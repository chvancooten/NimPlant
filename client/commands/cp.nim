from os import copyDir, copyFile, copyFileToDir, dirExists, splitPath, `/`
from strutils import join

# Copy files or directories
proc cp*(args : varargs[string]) : string =
    var
        source : string
        destination : string

    if args.len >= 2:
        source = args[0]
        destination = args[1 .. ^1].join(obf(" "))
    else:
        result = obf("Invalid number of arguments received. Usage: 'cp [source] [destination]'.")
        return

    # Copying a directory
    if dirExists(source):
        if dirExists(destination):
            copyDir(source, destination/splitPath(source).tail)
        else:
            copyDir(source, destination)

    # Copying a file
    elif dirExists(destination):
        copyFileToDir(source, destination)
    else:
        copyFile(source, destination)
    
    result = obf("Copied '") & source & obf("' to '") & destination & obf("'.")