use crate::internal::listener::{TaskHandler};
use std::process;

pub static COMMAND: &str = "execute";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() == 0  {
            return Ok("Invalid number of arguments received. Usage: 'execute [binary] <optional: arguments>'.".to_string());
        }

        let target = args.first().unwrap();

        if target.is_empty() {
            return Ok("[ERROR] Please provide a binary to execute.".to_string());
        }

        let target_args: &[std::string::String] = match args.len() {
            0 => &[],
            _ => &args[1..],
        };

        return match process::Command::new(target).args(target_args).spawn() {
            Ok(_) => Ok(format!("Successfully ran `{} {:?}`", target.clone(), target_args.clone())),
            Err(e) => Ok(format!("[ERROR] Unexpected error: {}.", e))
        }
    }
}