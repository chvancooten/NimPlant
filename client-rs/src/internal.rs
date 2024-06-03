pub(crate) mod client;
pub(crate) mod commands;
pub(crate) mod config;
pub(crate) mod crypto;
pub(crate) mod debug;
pub(crate) mod http;
pub(crate) mod win_utils;

#[cfg(feature = "risky")]
pub(crate) mod coff_loader;

#[cfg(feature = "risky")]
pub(crate) mod dinvoke;

#[cfg(feature = "risky")]
pub(crate) mod patches;
