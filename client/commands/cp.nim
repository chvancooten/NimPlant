from ../util/winUtils import copyDir
from os import dirExists, splitPath, `/`
from strutils import join
from winim/lean import CopyFileA, LPCSTR, FALSE, winstrConverterStringToPtrChar

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
        CopyFileA(source, destination/splitPath(source).tail, FALSE)
    else:
        CopyFileA(source, destination, FALSE)
    
    result = obf("Copied '") & source & obf("' to '") & destination & obf("'.")