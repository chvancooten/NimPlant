# https://github.com/nim-lang/Nim/issues/20007#issue-1300915309

import std/strutils
import std/sequtils

# remove -fstack-clash-protection
switch("gcc.options.always", replace(get("gcc.options.always"), "-fstack-clash-protection", ""))

# disable _FORTIFY_SOURCE
switch("gcc.options.always", replace(get("gcc.options.always"), "-D_FORTIFY_SOURCE=2", "-D_FORTIFY_SOURCE=0"))

proc dropZ(f: string): string =
    let flags = f.split(",")
    var result: seq[string] = @[]
    var drop = false
    for f in flags:
        if f == "-z":
            drop = true
        elif not drop:
            result.add(f)
        else:
            drop = false
    return result.join(",")

# remove all instance of -z flags and their parameters
let new_flags = get("gcc.options.linker").split(" ").map(dropZ).join(" ")

switch("gcc.options.linker", new_flags)
