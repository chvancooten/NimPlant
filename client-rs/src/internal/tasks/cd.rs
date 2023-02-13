use std::env;
use std::path::Path;
use crate::internal::listener::{TaskHandler};

pub static COMMAND: &str = "cd";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 1 {
            return Ok("Invalid number of arguments received. Usage: 'cd [directory]'.".to_string());
        }

        let path = args.first().unwrap();
        let root = Path::new(path);
        let normalized_root = root.clone().canonicalize().unwrap_or_default();

        return match env::set_current_dir(&root) {
            Ok(_) => Ok(format!("Changed working directory to '{}'.", normalized_root.display())),
            Err(_) => Ok("[ERROR] Could not change working directory.".to_string())
        }
    }
}