from winim/lean import GetUserName, CloseHandle, GetCurrentProcess, GetLastError, GetTokenInformation, OpenProcessToken, tokenElevation,
    TOKEN_ELEVATION, TOKEN_INFORMATION_CLASS, TOKEN_QUERY, HANDLE, PHANDLE, DWORD, PDWORD, LPVOID, LPWSTR, TCHAR
from winim/utils import `&`
import strutils
import ../util/strenc

# Determine if the user is elevated (running in high-integrity context)
proc isUserElevated(): bool =
  var
    tokenHandle: HANDLE
    elevation = TOKEN_ELEVATION()
    cbsize: DWORD = 0
  
  if OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, cast[PHANDLE](addr(tokenHandle))) == 0:
    when defined verbose:
      echo obf("DEBUG: Cannot query tokens: ") & $GetLastError()
    return false
  
  if GetTokenInformation(tokenHandle, tokenElevation, cast[LPVOID](addr(elevation)), cast[DWORD](sizeOf(elevation)), cast[PDWORD](addr(cbsize))) == 0:
    when defined verbose:
      echo obf("DEBUG: Cannot retrieve token information: ") & $GetLastError()
    discard CloseHandle(tokenHandle)
    return false
  
  result = elevation.TokenIsElevated != 0

# Get the current username via the GetUserName API
proc whoami*() : string =
    var 
        buf : array[257, TCHAR] # 257 is UNLEN+1 (max username length plus null terminator)
        lpBuf : LPWSTR = addr buf[0]
        pcbBuf : DWORD = int32(len(buf))

    discard GetUserName(lpBuf, &pcbBuf)
    for character in buf:
        if character == 0: break
        result.add(char(character))
    if isUserElevated():
        result.add(obf("*"))