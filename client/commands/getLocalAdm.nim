import winim/com
import strutils

# Get local administrators on the machine via WMI
proc getLocalAdm*() : string =
    let wmi = GetObject(obf(r"winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2"))
    for groupMems in wmi.execQuery(obf("SELECT GroupComponent,PartComponent FROM Win32_GroupUser\n")):
        if obf("Administrators") in $groupMems.GroupComponent:
            var admin = $groupMems.PartComponent.split("\"")[^2]
            result.add(admin & "\n")
    result = result.strip(trailing = true)