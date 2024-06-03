use fmtools::format; // using obfstr to obfuscate
use std::io::ErrorKind;

pub(crate) fn cat(path: &str) -> String {
    if path.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'cat [file]'.");
    }

    match std::fs::read_to_string(path) {
        Ok(contents) => contents,
        Err(e) => {
            if e.kind() == ErrorKind::NotFound {
                format!("File not found.")
            } else {
                format!("Error reading file.")
            }
        }
    }
}
