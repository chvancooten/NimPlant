// Enable features for COFF loading
#![allow(internal_features)]
#![feature(c_variadic)]
#![feature(core_intrinsics)]

mod app;

#[no_mangle]
pub extern "C" fn Update() {
    app::main();
}
