from os import dirExists, removeDir, removeFile
from strutils import join

# Remove a system file or folder
proc rm*(args : varargs[string]) : string =
    var path = args.join(obf(" "))

    if path == "":
        result = obf("Invalid number of arguments received. Usage: 'rm [path]'.")
    else:
        if dirExists(path):
            removeDir(path)
        else:
            removeFile(path)
        result = obf("Removed '") & path & obf("'.")