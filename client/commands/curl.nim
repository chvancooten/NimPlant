import puppy
from strutils import join
from ../util/webClient import Listener

# Curl an HTTP webpage to stdout
proc curl*(li : Listener, args : varargs[string]) : string =
    var 
        output : string
        url = args.join(obf(" "))
    if url == "":
        result = obf("Invalid number of arguments received. Usage: 'curl [URL]'.")
    else:
        output = fetch(
                    url,
                    headers = @[Header(key: obf("User-Agent"), value: li.userAgent)]
                    )

        if output == "":
            result = obf("No response received. Ensure you format the url correctly and that the target server exists. Example: 'curl https://google.com'.")
        else:
            result = output