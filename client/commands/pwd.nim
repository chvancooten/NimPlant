from os import getCurrentDir

# Get the current working directory
proc pwd*() : string =
    result = getCurrentDir()