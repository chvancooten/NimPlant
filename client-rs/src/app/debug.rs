#[cfg(debug_assertions)]
use windows_sys::Win32::System::Console::AllocConsole;

// A simple macro to only print when compiled in debug mode
// The debug version
#[cfg(debug_assertions)]
macro_rules! debug_println {
    ($( $args:expr ),*) => { println!( $( $args ),* ); }
}

// Non-debug version
#[cfg(not(debug_assertions))]
macro_rules! debug_println {
    ($( $args:expr ),*) => {}
}

pub(crate) use debug_println;

// Function to allocate a console in debug mode only
#[cfg(debug_assertions)]
pub(crate) fn allocate_console_debug_only() {
    unsafe {AllocConsole();}
}

#[cfg(not(debug_assertions))]
pub(crate) fn allocate_console_debug_only() {}