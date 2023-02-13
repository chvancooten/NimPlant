use crate::internal::listener::{TaskHandler};
use std::{env, fs};
use std::path::Path;
use chrono::{DateTime, Local};
use std::fs::FileType;
use std::cmp;

pub static COMMAND: &str = "ls";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() > 1 {
            return Ok("Invalid number of arguments received. Usage: 'ls <path>'.".to_string());
        }

        let current_path = env::current_dir().unwrap_or_default();

        let root = match args.len() {
            1 => Path::new(args.first().unwrap()),
            _ => current_path.as_path(),
        };

        let normalized_root = root.canonicalize().unwrap_or_default();

        if ! root.is_dir() {
            return match root.exists() {
                true => Ok(format!("`{}` is a file.", normalized_root.display())),
                false => Ok(format!("[ERROR] `{}` does not exist.", root.display()))
            }
        }

        let mut output = format!("Directory listing of directory '{}'.\n\n", normalized_root.display());
        output.push_str(format!("{:<8}  {:<36}  {:<10}  {:<20}  {:<20}\n", "TYPE", "NAME", "SIZE", "CREATED", "LAST WRITE").as_str());
        output.push_str(format!("{:-<8}  {:-<36}  {:-<10}  {:-<20}  {:-<20}\n", "", "", "", "", "").as_str());


        for entry in fs::read_dir(root)? {
            let entry = entry?;
            let metadata = entry.metadata()?;
            let file_name = entry
                .file_name()
                .into_string()
                .unwrap_or("".to_string());

            if file_name.is_empty() {
                continue;
            }

            let file_type = entry.file_type()?;
            let size = metadata.len();
            let created: DateTime<Local> = DateTime::from(metadata.created()?);
            let modified: DateTime<Local> = DateTime::from(metadata.modified()?);

            output.push_str(format!(
                "{:<8}  {:<36}  {:<10}  {:<20}  {:<20}\n",
                format_file_type(file_type),
                file_name,
                format_size(size as f64),
                modified.format("%d-%m-%Y %H:%M:%S").to_string(),
                created.format("%d-%m-%Y %H:%M:%S").to_string(),
            ).as_str());
        }

        Ok(output)
    }
}

fn format_file_type(f: FileType) -> String {
    return if f.is_dir() {
        "[DIR]".to_string()
    } else if f.is_file() {
        "[FILE]".to_string()
    } else {
        "[LINK]".to_string()
    }
}

pub fn format_size(file_size: f64) -> String {
  let negative = if file_size.is_sign_positive() { "" } else { "-" };
  let num = file_size.abs();
  let units = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  if num < 1_f64 {
      return format!("{}{} {}", negative, num, "B");
  }
  let delimiter = 1000_f64;
  let exponent = cmp::min((num.ln() / delimiter.ln()).floor() as i32, (units.len() - 1) as i32);
  let pretty_bytes = format!("{:.2}", num / delimiter.powi(exponent)).parse::<f64>().unwrap() * 1_f64;
  let unit = units[exponent as usize];
  format!("{}{} {}", negative, pretty_bytes, unit)
}
