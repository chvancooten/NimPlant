// Base code adapted from RustRedOps by joaoviictorti under MIT License
// https://github.com/joaoviictorti/RustRedOps/tree/main/Self_Deletion

use std::{
    ffi::c_void,
    mem::{size_of, size_of_val},
};
use windows::core::PCWSTR;
use windows::Win32::{
    Foundation::CloseHandle,
    Storage::FileSystem::{CreateFileW, SetFileInformationByHandle, FILE_RENAME_INFO},
    Storage::FileSystem::{
        FileDispositionInfo, FileRenameInfo, DELETE, FILE_DISPOSITION_INFO,
        FILE_FLAGS_AND_ATTRIBUTES, FILE_SHARE_READ, OPEN_EXISTING, SYNCHRONIZE,
    },
    System::Memory::{GetProcessHeap, HeapAlloc, HeapFree, HEAP_ZERO_MEMORY},
};

pub(crate) fn perform() -> Result<(), Box<dyn std::error::Error>> {
    let stream = ":nimpln";
    let stream_wide: Vec<u16> = stream.encode_utf16().chain(std::iter::once(0)).collect();

    unsafe {
        let mut delete_file = FILE_DISPOSITION_INFO::default();
        let lenght = size_of::<FILE_RENAME_INFO>() + (stream_wide.len() * size_of::<u16>());
        let rename_info =
            HeapAlloc(GetProcessHeap()?, HEAP_ZERO_MEMORY, lenght).cast::<FILE_RENAME_INFO>();

        delete_file.DeleteFile = true.into();
        (*rename_info).FileNameLength = (stream_wide.len() * size_of::<u16>()) as u32 - 2;

        std::ptr::copy_nonoverlapping(
            stream_wide.as_ptr(),
            (*rename_info).FileName.as_mut_ptr(),
            stream_wide.len(),
        );

        let path = std::env::current_exe()?;
        let path_str = path.to_str().unwrap_or("");
        let mut full_path: Vec<u16> = path_str.encode_utf16().collect();
        full_path.push(0);

        let mut h_file = CreateFileW(
            PCWSTR(full_path.as_ptr()),
            DELETE.0 | SYNCHRONIZE.0,
            FILE_SHARE_READ,
            None,
            OPEN_EXISTING,
            FILE_FLAGS_AND_ATTRIBUTES(0),
            None,
        )?;

        SetFileInformationByHandle(
            h_file,
            FileRenameInfo,
            rename_info as *const c_void,
            lenght as u32,
        )?;

        CloseHandle(h_file)?;

        h_file = CreateFileW(
            PCWSTR(full_path.as_ptr()),
            DELETE.0 | SYNCHRONIZE.0,
            FILE_SHARE_READ,
            None,
            OPEN_EXISTING,
            FILE_FLAGS_AND_ATTRIBUTES(0),
            None,
        )?;

        SetFileInformationByHandle(
            h_file,
            FileDispositionInfo,
            std::ptr::from_ref::<FILE_DISPOSITION_INFO>(&delete_file).cast(),
            size_of_val(&delete_file) as u32,
        )?;

        CloseHandle(h_file)?;

        HeapFree(
            GetProcessHeap()?,
            HEAP_ZERO_MEMORY,
            Some(rename_info as *const c_void),
        )?;

        Ok(())
    }
}
