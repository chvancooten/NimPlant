use fmtools::format; // using obfstr to obfuscate

pub(crate) fn pwd() -> String {
    match std::env::current_dir() {
        Ok(pwd) => format!(
            "Current working directory: '"{pwd.to_string_lossy()}"'."
        ),
        Err(e) => format!("Failed to get current working directory: "{e}),
    }
}
