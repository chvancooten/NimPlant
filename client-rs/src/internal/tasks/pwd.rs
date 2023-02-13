use std::env;
use crate::internal::listener::{TaskHandler};

pub static COMMAND: &str = "pwd";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 0 {
            return Ok("Invalid number of arguments received. Usage: 'pwd'.".to_string());
        }

        return match env::current_dir() {
            Ok(p) => Ok(p.display().to_string()),
            Err(_) => Ok("[ERROR] Could not retrieve working directory.".to_string())
        }
    }
}