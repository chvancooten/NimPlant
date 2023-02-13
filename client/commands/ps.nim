from winim/lean import MAX_PATH, WCHAR, DWORD, WINBOOL, HANDLE
from winim/extra import PROCESSENTRY32, PROCESSENTRY32W, CreateToolhelp32Snapshot, Process32First, Process32Next
from strutils import parseInt, repeat, strip
from os import getCurrentProcessId

# Overload $ proc to allow string conversion of szExeFile

proc `$`(a: array[MAX_PATH, WCHAR]): string = $cast[WideCString](unsafeAddr a[0])

# Get list of running processes
# https://forum.nim-lang.org/t/580
proc ps*(): string =
    var 
        output: string
        processSeq: seq[PROCESSENTRY32W]
        processSingle: PROCESSENTRY32
    
    let 
        hProcessSnap  = CreateToolhelp32Snapshot(0x00000002, 0)

    processSingle.dwSize = sizeof(PROCESSENTRY32).DWORD
    
    if Process32First(hProcessSnap, processSingle.addr):
        while Process32Next(hProcessSnap, processSingle.addr):
            processSeq.add(processSingle)
    CloseHandle(hProcessSnap) 

    output = obf("PID\tNAME\t\t\t\tPPID\n")
    for processSingle in processSeq:
        var 
            procName : string = $processSingle.szExeFile
            procNamePadded : string

        try:
            procNamePadded = procName & obf(" ").repeat(30-procname.len)
        except:
            procNamePadded = procName

        output.add($processSingle.th32ProcessID & obf("\t") & procNamePadded & obf("\t") & $processSingle.th32ParentProcessID)

        # Add an indicator to the current process
        if parseInt($processSingle.th32ProcessID) == getCurrentProcessId():
            output.add(obf("\t<-- YOU ARE HERE"))

        output.add("\n")
    result = output.strip(trailing = true)