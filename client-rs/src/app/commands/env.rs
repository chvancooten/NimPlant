use fmtools::format; // using obfstr to obfuscate

pub(crate) fn env() -> String {
    let mut result = String::new();
    result.push_str(&format!("Environment variables:\n"));
    for (key, value) in std::env::vars() {
        result.push_str(&format!({key:<30}{value:<50}"\n"));
    }
    result
}
