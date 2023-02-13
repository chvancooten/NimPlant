import winim/lean

type
  PS_ATTR_UNION* {.pure, union.} = object
    Value*: ULONG
    ValuePtr*: PVOID
  PS_ATTRIBUTE* {.pure.} = object
    Attribute*: ULONG 
    Size*: SIZE_T
    u1*: PS_ATTR_UNION
    ReturnLength*: PSIZE_T
  PPS_ATTRIBUTE* = ptr PS_ATTRIBUTE
  PS_ATTRIBUTE_LIST* {.pure.} = object
    TotalLength*: SIZE_T
    Attributes*: array[2, PS_ATTRIBUTE]
  PPS_ATTRIBUTE_LIST* = ptr PS_ATTRIBUTE_LIST
  KNORMAL_ROUTINE* {.pure.} = object
    NormalContext*: PVOID
    SystemArgument1*: PVOID
    SystemArgument2*: PVOID
  PKNORMAL_ROUTINE* = ptr KNORMAL_ROUTINE

type NtOpenProcess* = proc(
    ProcessHandle: PHANDLE,
    DesiredAccess: ACCESS_MASK,
    ObjectAttributes: POBJECT_ATTRIBUTES,
    ClientId: PCLIENT_ID): NTSTATUS {.stdcall.}

type NtAllocateVirtualMemory* = proc(
    ProcessHandle: HANDLE,
    BaseAddress: PVOID,
    ZeroBits: ULONG,
    RegionSize: PSIZE_T,
    AllocationType: ULONG,
    Protect: ULONG): NTSTATUS {.stdcall.}

type NtWriteVirtualMemory* = proc(
    ProcessHandle: HANDLE,
    BaseAddress: PVOID,
    Buffer: PVOID,
    NumberOfBytesToWrite: SIZE_T,
    NumberOfBytesWritten: PSIZE_T): NTSTATUS {.stdcall.}

type NtProtectVirtualMemory* = proc(
    ProcessHandle: HANDLE,
    BaseAddress: PVOID,
    NumberOfBytesToProtect: PSIZE_T,
    NewAccessProtection: ULONG,
    OldAccessProtection: PULONG): NTSTATUS {.stdcall.}

type NtCreateThreadEx* = proc(
    ThreadHandle: PHANDLE,
    DesiredAccess: ACCESS_MASK,
    ObjectAttributes: POBJECT_ATTRIBUTES,
    ProcessHandle: HANDLE,
    StartRoutine: PVOID,
    Argument: PVOID,
    CreateFlags: ULONG,
    ZeroBits: SIZE_T,
    StackSize: SIZE_T,
    MaximumStackSize: SIZE_T,
    AttributeList: PPS_ATTRIBUTE_LIST): NTSTATUS {.stdcall.} 