import os

# Command history and command / path completion on Linux
if os.name == "posix":
    import readline
    from .commands import getCommandList

    commands = getCommandList()

    def list_folder(path):
        if path.startswith(os.path.sep):
            # absolute path
            basedir = os.path.dirname(path)
            contents = os.listdir(basedir)
            # add back the parent
            contents = [os.path.join(basedir, d) for d in contents]
        else:
            # relative path
            contents = os.listdir(os.curdir)
        return contents

    # Dynamically complete commands
    def complete(text, state):
        line = readline.get_line_buffer()
        if line == text:
            results = [x for x in commands if x.startswith(text)] + [None]
        else:
            results = [x for x in list_folder(text) if x.startswith(text)] + [None]

        return results[state]

    readline.set_completer(complete)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(" \t\n`~!@#$%^&*()-=+[{]}\\|;:'\",<>?")
    inputFunction = input

# Command history and command / path completion on Windows
else:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import NestedCompleter
    from prompt_toolkit.contrib.completers.system import SystemCompleter
    from prompt_toolkit.shortcuts import CompleteStyle

    from .commands import getCommandList

    commands = getCommandList()

    # Complete system commands and paths
    systemCompleter = SystemCompleter()

    # Use a nested dict for each command to prevent arguments from being auto-completed before a command is entered and vice versa
    dict = {}
    for c in commands:
        dict[c] = systemCompleter
    nestedCompleter = NestedCompleter.from_nested_dict(dict)

    session = PromptSession()

# User prompt
def promptUserForCommand():
    from .nimplant import np_server
    from .commands import handleCommand

    np = np_server.getActiveNimplant()

    if os.name == "posix":
        command = input(f"NimPlant {np.id} $ > ")
    else:
        command = session.prompt(
            f"NimPlant {np.id} $ > ",
            completer=nestedCompleter,
            complete_style=CompleteStyle.READLINE_LIKE,
            auto_suggest=AutoSuggestFromHistory(),
        )

    handleCommand(command)
