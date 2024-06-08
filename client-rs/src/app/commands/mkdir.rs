use fmtools::format; // using obfstr to obfuscate
use std::fs;

pub(crate) fn mkdir(path: &str) -> String {
    if path.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'mkdir [path]'.");
    }

    if let Err(e) = fs::create_dir_all(path) {
        format!("Failed to create directory: "{e})
    } else {
        format!("Directory '"{path}"' created successfully.")
    }
}