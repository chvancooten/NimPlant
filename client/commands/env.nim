from os import envPairs
from strutils import strip, repeat

# List environment variables
proc env*() : string =
    var output: string

    for key, value in envPairs():
        var keyPadded : string

        try:
            keyPadded = key & obf(" ").repeat(30-key.len)
        except:
            keyPadded = key
            
        output.add(keyPadded & obf("\t") & value & "\n")

    result = output.strip(trailing = true)