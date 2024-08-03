use fmtools::format; // using obfstr to obfuscate
use std::ffi::{c_void, OsString};
use std::mem;
use std::os::windows::ffi::OsStringExt;
use windows_sys::Win32::Foundation::HANDLE;
use windows_sys::Win32::Security::{
    GetTokenInformation, TokenElevation, TOKEN_ELEVATION, TOKEN_QUERY,
};
use windows_sys::Win32::System::Threading::{GetCurrentProcess, OpenProcessToken};
use windows_sys::Win32::System::WindowsProgramming::GetUserNameW;

fn get_username() -> String {
    let mut buffer: [u16; 256] = [0; 256];
    let mut size: u32 = buffer.len() as u32;

    unsafe {
        if GetUserNameW(buffer.as_mut_ptr(), &mut size) != 0 {
            let os_string = OsString::from_wide(&buffer[..(size as usize - 1)]);
            return os_string.into_string().unwrap_or_else(|_| "unknown".into());
        }
    }

    "unknown".into()
}

pub(crate) fn whoami() -> String {
    let username = get_username();

    unsafe {
        let mut token: HANDLE = mem::zeroed();
        if OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &mut token) != 0 {
            let mut token_elevation: TOKEN_ELEVATION = mem::zeroed();
            let mut size: u32 = 0;
            if GetTokenInformation(
                token,
                TokenElevation,
                std::ptr::addr_of_mut!(token_elevation).cast::<c_void>(),
                mem::size_of::<TOKEN_ELEVATION>() as u32,
                &mut size,
            ) != 0 && token_elevation.TokenIsElevated != 0 {
                return format!({username}"*");
            }

        }
    }

    username
}
