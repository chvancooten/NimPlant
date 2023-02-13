use std::env;
use crate::internal::listener::{TaskHandler};

pub static COMMAND: &str = "env";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 0 {
            return Ok("Invalid number of arguments received. Usage: 'env'.".to_string());
        }

        let mut output = String::from("\n");

        let s = format!("{:<40}\t{}\n", "KEY", "VALUE");
        output.push_str(s.as_str());

        for (key, value) in env::vars_os() {
            let s = format!("{:<40}\t{}\n", key.to_str().unwrap_or_default(), value.to_str().unwrap_or_default());

            output.push_str(s.as_str())
        }

        Ok(output)
    }
}

