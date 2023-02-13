use std::fs;
use crate::internal::listener::{TaskHandler};
use std::path::Path;

pub static COMMAND: &str = "rm";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 1 {
            return Ok("Invalid number of arguments received. Usage: 'rm [path]'.".to_string());
        }

        let path = args.first().unwrap();
        let target = Path::new(path);

        if ! target.exists() {
            return Ok(format!("[ERROR] Path does not exist: {}", target.display()));
        }

        if target.is_dir() {
            return match fs::remove_dir(target) {
                Ok(_) => Ok(format!("Removed directory: {}", target.display())),
                Err(_) => Ok(format!("[ERROR] Could not remove directory: {}", target.display()))
            }
        }

        return match fs::remove_file(target) {
            Ok(_) => Ok(format!("Removed file: {}", target.display())),
            Err(_) => Ok(format!("[ERROR] Could not remove file: {}", target.display()))
        }
    }
}