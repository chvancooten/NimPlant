<div align="center">
  <a href="https://github.com/chvancooten/NimPlant">
    <img src="ui/src/assets/nimplant-logomark.svg" height="150">
  </a>

  <h1>NimPlant - A light stage-one payload written in Nim, with a supporting C2 server based on Python</h1>
</div>


_By Cas van Cooten ([@chvancooten](https://twitter.com/chvancooten)), with special thanks to contributors:_
- _Kadir Yamamoto ([@yamakadi](https://github.com/yamakadi)) for the front-end and rusty nimplant_
- _snovvcrash ([@snovvcrash](https://github.com/snovvcrash)) for adding execute-assembly & self-delete_
- _Fabian Mosch ([@S3cur3Th1sSh1t](https://twitter.com/ShitSecure)) for sharing dynamic invocation implementation in Nim_

# Instructions

## Installation

- Install Nim and Python3 on your OS of choice (installation via `choosenim` is recommended, as `apt` doesn't always have the latest version).
- Install required packages using the Nimble package manager (`nimble install nimcrypto parsetoml puppy ptr_math winim`).
- Install `requirements.txt` from the server folder (`pip3 install -r server/requirements.txt`).
- If you're on Linux or MacOS, install the `mingw` toolchain for your platform (`brew install mingw-w64` or `apt install mingw-w64`).

If you'd like to use the Rust implant, `client-rs`:
- Install rust using `rustup`.
- Run `rustup default nightly` to switch to nightly.
- Run `rustup target add x86_64-pc-windows-gnu` to add the windows toolchain.
- Run `rustup target add x86_64-apple-darwin` to add the MacOS toolchain.

## Getting Started

### Configuration

Before using NimPlant, create the configuration file `config.toml`. It is recommended to copy `config.toml.example` and work from there.

An overview of settings is provided below.

| Category | Setting            | Description                                                                                                                                                                          |
|----------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| server   | ip                 | The IP that the C2 web server (including API) will listen on. Recommended to use 127.0.0.1, only use 0.0.0.0 when you have setup proper firewall or routing rules to protect the C2. |
| server   | port               | The port that the C2 web server (including API) will listen on.                                                                                                                      |
| listener | type               | The listener type, either HTTP or HTTPS. Make sure any HTTPS certificate is valid or NimPlant won't connect. When managing HTTPS via a redirector, configure HTTP for NimPlant.      |
| listener | sslCertPath        | The local path to a VALID HTTPS certificate file (e.g. requested via LetsEncrypt CertBot). Ignored when listener type is 'HTTP'.                                                     |
| listener | sslKeyPath         | The local path to a VALID HTTPS certificate private key file (e.g. requested via LetsEncrypt CertBot). Ignored when listener type is 'HTTP'.                                         |
| listener | hostname           | The listener hostname. If not empty (""), NimPlant will use this hostname to connect. Make sure you are properly routing traffic from this host to the NimPlant listener port.       |
| listener | ip                 | The listener IP. Required even if 'hostname' is set, as it is used by the server to register on this IP.                                                                             |
| listener | port               | The listener port. Required even if 'hostname' is set, as it is used by the server to register on this port.                                                                         |
| listener | registerPath       | The URI path that new NimPlants will register with.                                                                                                                                  |
| listener | taskPath           | The URI path that NimPlants will get tasks from.                                                                                                                                     |
| listener | resultPath         | The URI path that NimPlants will submit results to.                                                                                                                                  |
| nimplant | riskyMode          | Compile NimPlant with support for risky commands. Operator discretion advised. Disabling will remove support for `execute-assembly`, `powershell`, `shell` and `shinject`.           |
| nimplant | sleepTimeSeconds   | The default sleep time in seconds for new NimPlants.                                                                                                                                 |
| nimplant | sleepJitterPercent | The default jitter in percent for new NimPlants.                                                                                                                                     |
| nimplant | killTimeHours      | The kill time for NimPlants in hours. NimPlants will auto-exit when this time has passed from their first launch.                                                                    |
| nimplant | userAgent          | The user-agent used by NimPlants. The server also uses this to validate NimPlant traffic, so it is recommended to choose a UA that is inconspicuous, but not too prevalent.          |

### Compilation

Once the configuration is to your liking, you can generate NimPlant binaries to deploy on your target. Currently, NimPlant supports `.exe`, `.dll`, and `.bin` binaries for (self-deleting) executables, libraries, and position-independent shellcode (through sRDI), respectively. To generate, run `python NimPlant.py compile` followed by your preferred binaries (`exe`, `exe-selfdelete`, `dll`, `raw`, or `all`) and, optionally, the implant type (`nim`, `rust`, or `rust-debug`). Files will be written to `./client/bin/NimPlant.*` for `nim` and `./client-rs/bin/rusty_nimplant.*` for `rust` and `rust-debug`.

**Notes**:
- NimPlant only supports x64 at this time!
- The entrypoint for DLL files is `Update`, which is triggered by DllMain for all entrypoints. This means you can use e.g. `rundll32 .\NimPlant.dll,Update` to trigger, or use your LOLBIN of choice to sideload it
- You have to quote any path arguments or escape backslashes if you are using Rusty NimPlant on Windows (`ls "C:\Users"` or `ls C:\\Users` instead of `ls C:\Users`)

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

        A light-weight stage 1 implant and C2 based on Nim and Python
        By Cas van Cooten (@chvancooten)

Compiling .exe → NimPlant
Compiling self-deleting .exe → NimPlant
Compiling .dll → NimPlant
Compiling .bin → NimPlant

Done compiling! You can find compiled binaries in 'client/bin/'.
```

### Compilation with Docker

The Docker image [chvancooten/nimbuild](https://hub.docker.com/r/chvancooten/nimbuild) can be used to compile NimPlant binaries. Using Docker is easy and avoids dependency issues, as all required dependencies are pre-installed in this container.

To use it, install Docker for your OS and start the compilation in a container as follows.

```bash
docker run --rm -v `pwd`:/usr/src/np -w /usr/src/np chvancooten/nimbuild python3 NimPlant.py compile all
```

### Usage

Once you have your binaries ready, you can spin up your NimPlant server! No additional configuration is necessary as it reads from the same `config.toml` file. To launch a server, simply run `python NimPlant.py server`.

**Notes**:
- If you are running your NimPlant server externally from the machine where binaries are compiled, make sure that both `config.toml` and `.xorkey` match. If not, NimPlant will not connect.
- If NimPlant cannot connect to a server or loses connection, it will retry 5 times with an exponential backoff time before giving up and killing itself. The backoff is based on the initial sleep time, if the sleep time is 10 seconds, it will wait 10, then 20, then 40, then 80, then 160 seconds before dying.
- Logs are stored in the `server/.logs` directory.

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

        A light-weight stage 1 implant and C2 based on Nim and Python
        By Cas van Cooten (@chvancooten)

[11/07/2021 16:32:22] Started management server on 127.0.0.1:31337.
[11/07/2021 16:32:22] Started NimPlant listener on 0.0.0.0:443. CTRL-C to cancel waiting for NimPlants.
```

This will start both the C2 API and management web server (in the example above at `127.0.0.1:31337`) and the NimPlant listener (in the example above at `0.0.0.0:443`). Once a NimPlant checks in, you can use both the web interface and the console to send commands to NimPlant. 

Available commands are as follows.

```
Argument quoting is supported. Arguments shown as [required] <optional>.

NimPlant Commands:
    cat: [filename] Print a file's contents to the screen.
    cd: [directory] Change the working directory.
    cp: [source] [destination] Copy a file or directory.
    curl: [url] Get a webpage remotely and print results to stdout.
    download: [remotefilepath] <localfilepath> Download a file from NimPlant's disk to the C2 server.
    env: Get environment variables.
    execute-assembly: <BYPASSAMSI=0> <BLOCKETW=0> [localfilepath] <arguments> Execute .NET assembly from memory. AMSI/ETW patched by default. Loads the CLR.
    getAv: List Antivirus / EDR products on target using WMI.
    getDom: Get the domain the target is joined to.
    getLocalAdm: List local administrators on the target using WMI.
    kill: Kill the currently selected NimPlant.
    ls: <path> List files and folders in a certain directory. Lists current directory by default.
    mkdir: [directory] Create a directory (and its parent directories, if required).
    mv: [source] [destination] Move a file or directory.
    powershell: <BYPASSAMSI=0> <BLOCKETW=0> [command] Execute a PowerShell command in an unmanaged runspace. Loads the CLR.
    ps: List running processes on the target. Indicates current process.
    pwd: Get the current working directory.
    reg: [query|add] [path] <key> <value> Query or modify the registry. New values will be added as REG_SZ.
    rm: [file] Remove a file or directory.
    run: [binary] <arguments> Run a binary from disk. Returns output, but blocks NimPlant while running.
    shell: [command] Execute a shell command.
    shinject: [targetpid] [localfilepath] Load raw shellcode from a file and inject it into the specified process's memory space using dynamic invocation.
    sleep: [sleeptime] <jitter%> Change the sleep time of the current NimPlant.
    upload: [localfilepath] <remotefilepath> Upload a file from the C2 server to NimPlant's disk.
    wget: [url] <outfile> Download a file to disk remotely.
    whoami: Get the user ID that NimPlant is running as.

Server Commands:
    clear: Clear the screen.
    exit: Exit the server, killing all NimPlants.
    getpid: Show process ID of the currently selected NimPlant.
    help: <command> Show this help menu, or command-specific help.
    hostname: Show hostname of the currently selected NimPlant.
    ipconfig: List adapter information of the currently selected NimPlant.
    list: Show list of active NimPlants.
    nimplant: Show info about the currently selected NimPlant.
    osbuild: Show operating system build information for the currently selected NimPlant.
    select: [id] Select another NimPlant.
```

#### Push Notifications
By default, NimPlant support push notifications via the code defined in `/server/util/notify.py`. It requires the `TELEGRAM_CHAT_ID` and `TELEGRAM_BOT_TOKEN` environment variables to be set before it will fire. Of course, the `notify.py` file can be easily extended with one's own push notification functionality. The `notify_user()` function is always called and receives an object with the checked-in NimPlant, which can then be pushed to the user if certain conditions are met.