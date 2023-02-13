use crate::internal::listener::{TaskHandler};
use std::path::Path;
use std::fs;

pub static COMMAND: &str = "cat";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 1 {
            return Ok("Invalid number of arguments received. Usage: 'cat [file]'.".to_string());
        }

        let path = args.first().unwrap();
        let target = Path::new(path);

        if (! target.exists()) | target.is_dir() {
            return Ok(format!("[ERROR] File does not exist: {}", target.display()));
        }

        return match fs::read_to_string(target) {
            Ok(v) => Ok(v),
            Err(_) => Ok(format!("[ERROR] Could not read file: {}", target.display()))
        }
    }
}