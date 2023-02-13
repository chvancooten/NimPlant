#[cfg(target_os = "windows")]
use winapi::shared::{
    minwindef,
    minwindef::{BOOL, DWORD, HINSTANCE, LPVOID}
};
#[cfg(feature = "debug_assertions")]
#[cfg(target_os = "windows")]
use winapi::um::consoleapi;

mod internal;
mod runner;

#[no_mangle]
#[allow(non_snake_case, unused_variables)]
#[cfg(target_os = "windows")]
extern "system" fn DllMain(dll_module: HINSTANCE, call_reason: DWORD, reserved: LPVOID) -> BOOL {
    const DLL_PROCESS_ATTACH: DWORD = 1;
    const DLL_PROCESS_DETACH: DWORD = 0;

    match call_reason {
        DLL_PROCESS_ATTACH => (),
        DLL_PROCESS_DETACH => (),
        _ => (),
    }
    minwindef::TRUE
}

#[no_mangle]
#[cfg(target_os = "windows")]
pub extern "C" fn Update() {
    #[cfg(feature = "debug_assertions")]
    {
        unsafe { consoleapi::AllocConsole() };

        println!("[+] Debug Mode: Enabled");
    }

    tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .unwrap()
        .block_on(async {
            match runner::run().await {
                Ok(_) => (),
                #[cfg(feature = "debug_assertions")]
                Err(e) => println!("An error occurred: {:?}", e),
                #[cfg(not(feature = "debug_assertions"))]
                Err(_) => ()
            };
        });

}
