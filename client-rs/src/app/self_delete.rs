use fmtools::format; // using obfstr to obfuscate
use std::ffi::c_void;
use std::mem::{size_of, zeroed};
use std::ptr::null_mut;
use widestring::u16cstr;
use windows_sys::Win32::Foundation::{CloseHandle, HANDLE, INVALID_HANDLE_VALUE};
use windows_sys::Win32::Storage::FileSystem::{
    CreateFileW, SetFileInformationByHandle, FILE_ATTRIBUTE_NORMAL, FILE_DISPOSITION_FLAG_DELETE,
    FILE_DISPOSITION_INFO, FILE_RENAME_INFO, OPEN_EXISTING,
};
use windows_sys::Win32::System::LibraryLoader::GetModuleFileNameW;

unsafe fn open_handle(path: &[u16]) -> HANDLE {
    CreateFileW(
        path.as_ptr(),
        0x00010000, // DELETE
        0,
        null_mut(),
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        null_mut() as isize,
    )
}

unsafe fn rename_handle(handle: HANDLE) -> bool {
    let stream_rename = format!(":nimpln");
    let ds_stream_rename = u16cstr!(&stream_rename).unwrap().as_ptr();
    let mut rename_info: FILE_RENAME_INFO = zeroed();
    rename_info.FileNameLength = (size_of_val(&ds_stream_rename) - size_of::<u16>()) as u32; // Exclude null terminator
    rename_info.FileName.copy_from(
        ds_stream_rename,
        rename_info.FileNameLength as usize / size_of::<u16>(),
    );
    SetFileInformationByHandle(
        handle,
        10, /* FileRenameInfo */
        &mut rename_info as *mut _ as *mut c_void,
        size_of::<FILE_RENAME_INFO>() as u32 + rename_info.FileNameLength,
    ) != 0
}

unsafe fn mark_for_deletion(handle: HANDLE) -> bool {
    let mut delete_info: FILE_DISPOSITION_INFO = zeroed();
    delete_info.DeleteFile = FILE_DISPOSITION_FLAG_DELETE as u32;
    SetFileInformationByHandle(
        handle,
        4, /* FileDispositionInfo */
        &mut delete_info as *mut _ as *mut c_void,
        size_of::<FILE_DISPOSITION_INFO>() as u32,
    ) != 0
}

pub fn perform_self_delete() -> Result<(), Box<dyn std::error::Error>> {
    let mut path: [u16; 261] = [0; 261]; // MAX_PATH + 1
    unsafe {
        if GetModuleFileNameW(null_mut(), path.as_mut_ptr(), path.len() as u32) == 0 {
            return Err(format!("Failed to get the current module file name").into());
        }
    }

    let handle = unsafe { open_handle(&path) };
    if handle == INVALID_HANDLE_VALUE {
        return Err(format!("Failed to acquire handle to current running process").into());
    }

    if !unsafe { rename_handle(handle) } {
        unsafe { CloseHandle(handle) };
        return Err(format!("Failed to rename the file").into());
    }

    unsafe { CloseHandle(handle) };

    let handle = unsafe { open_handle(&path) };
    if handle == INVALID_HANDLE_VALUE {
        return Err(format!("Failed to reopen current module").into());
    }

    if !unsafe { mark_for_deletion(handle) } {
        unsafe { CloseHandle(handle) };
        return Err(format!("Failed to mark the file for deletion").into());
    }

    unsafe { CloseHandle(handle) };
    Ok(())
}
