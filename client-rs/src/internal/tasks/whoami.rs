use crate::internal::intel;
use crate::internal::listener::{TaskHandler};

pub static COMMAND: &str = "whoami";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 0 {
            return Ok("Invalid number of arguments received. Usage: 'whoami'.".to_string());
        }

        Ok(intel::username())
    }
}