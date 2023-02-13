use crate::internal::listener::{TaskHandler};
use crate::internal::http;

pub static COMMAND: &str = "curl";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() == 0 {
            return Ok("Invalid number of arguments received. Usage: 'curl [URL]'.".into());
        }

        let url = args.join(" ");

        if url.is_empty() {
            return Ok("Invalid number of arguments received. Usage: 'curl [URL]'.".into());
        }

        let contents_future = http::get_content(url.clone());

        return match futures::executor::block_on(contents_future) {
            Ok(contents) => Ok(contents),
            Err(_) => Ok("No response received. Ensure you format the url correctly and that the target server exists. Example: 'curl https://google.com'".into())
        };
    }
}