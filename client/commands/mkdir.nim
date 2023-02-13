from os import createDir
from strutils import join

# Create a new system directory, including subdirectories
proc mkdir*(args : varargs[string]) : string =
    var path = args.join(obf(" "))
    if path == "":
        result = obf("Invalid number of arguments received. Usage: 'mkdir [path]'.")
    else:
        createDir(path)
        result = obf("Created directory '") & path & obf("'.")