use fmtools::format; // using obfstr to obfuscate
use std::ffi::OsString;
use std::os::windows::ffi::OsStringExt;
use windows_sys::core::PWSTR;
use windows_sys::Win32::System::SystemInformation::GetComputerNameExW;
use windows_sys::Win32::System::SystemInformation::COMPUTER_NAME_FORMAT;

pub(crate) fn get_domain() -> String {
    let mut buf: [u16; 257] = [0; 257];
    let lp_buf: PWSTR = buf.as_mut_ptr();
    let mut pcb_buf: u32 = buf.len() as u32;
    let format: COMPUTER_NAME_FORMAT = 2; // ComputerNameDnsDomain

    let success = unsafe { GetComputerNameExW(format, lp_buf, &mut pcb_buf) != 0 };

    if success {
        let domain = OsString::from_wide(&buf).to_string_lossy().into_owned();
        let domain = domain.trim_end_matches('\0').to_string();
        if domain.is_empty() {
            format!("Computer is not domain joined.")
        } else {
            domain
        }
    } else {
        format!("Failed to get domain name.")
    }
}
