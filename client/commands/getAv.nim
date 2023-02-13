import winim/com
from strutils import strip

# Get antivirus products on the machine via WMI
proc getAv*() : string =
    let wmisec = GetObject(obf(r"winmgmts:{impersonationLevel=impersonate}!\\.\root\securitycenter2"))
    for avprod in wmisec.execQuery(obf("SELECT displayName FROM AntiVirusProduct\n")):
        result.add($avprod.displayName & "\n")
    result = result.strip(trailing = true)