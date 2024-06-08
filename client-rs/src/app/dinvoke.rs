use dinvoke_rs::{data::PsAttributeList, dinvoke};
use std::os::raw::{c_ulong, c_void};
use windows_sys::{
    Wdk::Foundation::OBJECT_ATTRIBUTES,
    Win32::{Foundation::HANDLE, System::WindowsProgramming::CLIENT_ID},
};

// Function prototypes
// We cannot use the ones from dinvoke_rs::data, as this results in type conflicts
// https://github.com/Kudaes/rust_tips_and_tricks#function-signatures
pub type NtOpenProcess = unsafe extern "system" fn(
    ProcessHandle: *mut HANDLE,
    DesiredAccess: u32,
    ObjectAttributes: *mut OBJECT_ATTRIBUTES,
    ClientId: *mut CLIENT_ID,
) -> i32;

pub type NtAllocateVirtualMemory = unsafe extern "system" fn(
    ProcessHandle: HANDLE,
    BaseAddress: *mut *mut c_void,
    ZeroBits: usize,
    RegionSize: *mut usize,
    AllocationType: c_ulong,
    Protect: c_ulong,
) -> i32;

pub type NtWriteVirtualMemory = unsafe extern "system" fn(
    ProcessHandle: HANDLE,
    BaseAddress: *mut c_void,
    Buffer: *mut c_void,
    BufferSize: usize,
    NumberOfBytesWritten: *mut usize,
) -> i32;

pub type NtProtectVirtualMemory = unsafe extern "system" fn(
    ProcessHandle: HANDLE,
    BaseAddress: *mut *mut c_void,
    RegionSize: *mut usize,
    NewProtect: c_ulong,
    OldProtect: *mut c_ulong,
) -> i32;

pub type NtCreateThreadEx = unsafe extern "system" fn(
    ThreadHandle: *mut HANDLE,
    DesiredAccess: c_ulong,
    ObjectAttributes: *mut OBJECT_ATTRIBUTES,
    ProcessHandle: HANDLE,
    StartRoutine: *mut c_void,
    Argument: *mut c_void,
    CreateFlags: c_ulong,
    ZeroBits: usize,
    StackSize: usize,
    MaximumStackSize: usize,
    AttributeList: *mut PsAttributeList,
) -> i32;

// Dynamic function definitions
pub fn nt_open_process(
    process_handle: *mut isize,
    desired_access: u32,
    object_attributes: *mut OBJECT_ATTRIBUTES,
    client_id: *mut CLIENT_ID,
) -> i32 {
    unsafe {
        let ret: Option<i32>;
        let func_ptr: NtOpenProcess;
        let ntdll = dinvoke::get_module_base_address("ntdll.dll");
        dinvoke::dynamic_invoke!(
            ntdll,
            "NtOpenProcess",
            func_ptr,
            ret,
            process_handle,
            desired_access,
            object_attributes,
            client_id
        );

        ret.unwrap_or(-1)
    }
}

pub fn nt_allocate_virtual_memory(
    handle: HANDLE,
    base_address: *mut *mut c_void,
    zero_bits: usize,
    size: *mut usize,
    allocation_type: u32,
    protection: u32,
) -> i32 {
    unsafe {
        let ret: Option<i32>;
        let func_ptr: NtAllocateVirtualMemory;
        let ntdll = dinvoke::get_module_base_address("ntdll.dll");
        dinvoke::dynamic_invoke!(
            ntdll,
            "NtAllocateVirtualMemory",
            func_ptr,
            ret,
            handle,
            base_address,
            zero_bits,
            size,
            allocation_type,
            protection
        );

        ret.unwrap_or(-1)
    }
}

pub fn nt_write_virtual_memory(
    handle: HANDLE,
    base_address: *mut c_void,
    buffer: *mut c_void,
    buffer_size: usize,
    number_of_bytes_written: *mut usize,
) -> i32 {
    unsafe {
        let ret: Option<i32>;
        let func_ptr: NtWriteVirtualMemory;
        let ntdll = dinvoke::get_module_base_address("ntdll.dll");
        dinvoke::dynamic_invoke!(
            ntdll,
            "NtWriteVirtualMemory",
            func_ptr,
            ret,
            handle,
            base_address,
            buffer,
            buffer_size,
            number_of_bytes_written
        );

        ret.unwrap_or(-1)
    }
}

pub fn nt_protect_virtual_memory(
    handle: HANDLE,
    base_address: *mut *mut c_void,
    region_size: *mut usize,
    new_protect: u32,
    old_protect: *mut u32,
) -> i32 {
    unsafe {
        let ret: Option<i32>;
        let func_ptr: NtProtectVirtualMemory;
        let ntdll = dinvoke::get_module_base_address("ntdll.dll");
        dinvoke::dynamic_invoke!(
            ntdll,
            "NtProtectVirtualMemory",
            func_ptr,
            ret,
            handle,
            base_address,
            region_size,
            new_protect,
            old_protect
        );

        ret.unwrap_or(-1)
    }
}

#[allow(clippy::too_many_arguments)]
pub fn nt_create_thread_ex(
    thread_handle: *mut HANDLE,
    desired_access: u32,
    object_attributes: *mut OBJECT_ATTRIBUTES,
    process_handle: HANDLE,
    start_routine: *mut c_void,
    argument: *mut c_void,
    create_flags: u32,
    zero_bits: usize,
    stack_size: usize,
    maximum_stack_size: usize,
    attribute_list: *mut PsAttributeList,
) -> i32 {
    unsafe {
        let ret: Option<i32>;
        let func_ptr: NtCreateThreadEx;
        let ntdll = dinvoke::get_module_base_address("ntdll.dll");
        dinvoke::dynamic_invoke!(
            ntdll,
            "NtCreateThreadEx",
            func_ptr,
            ret,
            thread_handle,
            desired_access,
            object_attributes,
            process_handle,
            start_routine,
            argument,
            create_flags,
            zero_bits,
            stack_size,
            maximum_stack_size,
            attribute_list
        );

        ret.unwrap_or(-1)
    }
}
