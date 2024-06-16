// Enable features for COFF loading
#![allow(internal_features)]
#![feature(c_variadic)]
#![feature(core_intrinsics)]

mod app;

use app::debug::allocate_console_debug_only;

#[no_mangle]
pub extern "C" fn Update() {
    // Allocate a console if we're in debug mode
    allocate_console_debug_only();

    app::main();
}
