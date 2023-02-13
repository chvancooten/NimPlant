use crate::internal::listener::{TaskHandler};
use std::path::Path;
use std::fs;

pub static COMMAND: &str = "mkdir";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 1 {
            return Ok("Invalid number of arguments received. Usage: 'mkdir [path]'.".to_string());
        }

        let path = args.first().unwrap();
        let root = Path::new(path);

        if root.exists() {
            return Ok(format!("[ERROR] `{}` already exists.", root.display()));
        }

        fs::create_dir_all(root)?;

        let normalized_root = root.clone().canonicalize().unwrap_or_default();

        return Ok(format!("Created directory '{}'.", normalized_root.display()));
    }
}