from os import getCurrentDir, getFileInfo, FileInfo, splitPath, walkDir
from times import format
from strutils import strip, repeat, join
from math import round

# List files in the target directory
proc ls*(args : varargs[string]) : string =
    var 
        lsPath = args.join(obf(" "))
        path : string
        output : string
        output_files : string
        dateTimeFormat : string = obf("dd-MM-yyyy H:mm:ss")

    # List the current directory if no argument is given
    if lsPath == "":
        path = getCurrentDir()
    else:
        path = lsPath

    output = obf("Directory listing of directory '") & path & obf("'.\n\n")
    output.add(obf("TYPE\tNAME\t\t\t\tSIZE\t\tCREATED\t\t\tLAST WRITE\n"))

    for kind, itemPath in walkDir(path):
        var 
            info : FileInfo
            name : string = splitPath(itemPath).tail
            namePadded : string
        
        # Get file info, if readable to us
        try:
            namePadded = name & obf(" ").repeat(30-name.len)
            info = getFileInfo(itemPath)
        except:
            namePadded = name
            continue

        # Print directories first, then append files
        if $info.kind == obf("pcDir"):
            output.add(obf("[DIR] \t") & name & "\n")
        else:
            output_files.add(obf("[FILE] \t") & namePadded & obf("\t") & $(round(cast[int](info.size)/1024).toInt) & obf("KB\t\t") & $(info.creationTime).format(dateTimeFormat) &
                obf("\t") & $(info.lastWriteTime).format(dateTimeFormat) & "\n")

    output.add(output_files)
    result = output.strip(trailing = true)