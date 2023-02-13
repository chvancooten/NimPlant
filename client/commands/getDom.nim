from winim/lean import GetComputerNameEx
from winim/utils import `&`
import winim/inc/[windef, winbase]

# Get the current domain of the computer via the GetComputerNameEx API
proc getDom*() : string =
    var 
        buf : array[257, TCHAR]
        lpBuf :  LPWSTR = addr buf[0]
        pcbBuf : DWORD = int32(len(buf))
        format : COMPUTER_NAME_FORMAT = 2 # ComputerNameDnsDomain
        domainJoined : bool = false

    discard GetComputerNameEx(format, lpBuf, &pcbBuf)
    for character in buf:
        if character == 0: break
        domainJoined = true
        result.add(char(character))

    if not domainJoined:
        result = obf("Computer is not domain joined")