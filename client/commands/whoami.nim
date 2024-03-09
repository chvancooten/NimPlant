from winim/lean import GetUserNameW, CloseHandle, GetCurrentProcess, GetLastError, GetTokenInformation, OpenProcessToken, tokenElevation,
    TOKEN_ELEVATION, TOKEN_INFORMATION_CLASS, TOKEN_QUERY, HANDLE, PHANDLE, DWORD, PDWORD, LPVOID, LPWSTR, WCHAR
from winim/utils import `&`
from winim/inc/lm import UNLEN
import winim/winstr
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
      buf = newWString(UNLEN + 1)
      cb = DWORD buf.len

    discard GetUserNameW(&buf, &cb)
    buf.setLen(cb - 1)
    result.add($buf)

    if isUserElevated():
        result.add(obf("*"))