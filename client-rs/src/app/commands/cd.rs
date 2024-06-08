use fmtools::format; // using obfstr to obfuscate
use std::env;

pub(crate) fn cd(path: &str) -> String {
    if path.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'cd [directory]'.");
    }

    if let Ok(()) = env::set_current_dir(path) {
        format!("Successfully changed working directory to '"{path}"'.")
    } else {
        format!("Error changing working directory.")
    }
}
