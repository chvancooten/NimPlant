#![windows_subsystem = "windows"]

#[cfg(target_os = "windows")]
#[cfg(any(feature = "debug_assertions", feature = "debug"))]
use winapi::um::consoleapi;

#[cfg(all(target_os = "windows", feature = "disappear"))]
use houdini;

mod internal;
mod runner;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    #[cfg(target_os = "windows")]
    #[cfg(any(feature = "debug_assertions", feature = "debug"))]
    {
        unsafe { consoleapi::AllocConsole() };

        println!("[+] Debug Mode: Enabled");
    }

    #[cfg(feature = "disappear")]
    match houdini::disappear() {
        Ok(_) => runner::run().await?,
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        Err(e) => println!("Encountered an error: {:?}", e),
        #[cfg(not(any(feature = "debug_assertions", feature = "debug")))]
        Err(_) => (),
    };

    #[cfg(not(feature = "disappear"))]
    runner::run().await?;

    Ok(())
}