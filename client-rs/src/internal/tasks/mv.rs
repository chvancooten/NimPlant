use crate::internal::listener::{TaskHandler};
use std::path::Path;
use std::fs;

pub static COMMAND: &str = "mv";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 2 {
            return Ok("Invalid number of arguments received. Usage: 'mv [source] [destination]'.".to_string());
        }

        let source_path = args.first().unwrap();
        let source = Path::new(source_path);

        let destination_path = args.get(1).unwrap();
        let destination = Path::new(destination_path);

        if ! source.exists() {
            return Ok(format!("[ERROR] `{}` does not exist.", source.canonicalize().unwrap().display()));
        }

        if source.canonicalize().unwrap_or_default() == destination.canonicalize().unwrap_or_default() {
            return Ok("[ERROR] Paths cannot be the same.".to_string())
        }

        return match move_target(source, destination) {
            true => Ok(format!("Moved '{}' to '{}'", source.display(), destination.display())),
            false => Ok(format!("[ERROR] Could not move '{}' to '{}'", source.display(), destination.display())),
        };
    }
}

fn move_target(source: &Path, destination: &Path) -> bool {
    return match destination.exists() {
        true => fs::rename(source, destination.join(source.file_name().unwrap_or_default()).as_path()).is_ok(),
        false => fs::rename(source, destination).is_ok()
    }
}