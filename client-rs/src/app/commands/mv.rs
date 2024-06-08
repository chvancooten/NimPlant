use crate::app::win_utils::transfer_dir_to;
use fmtools::format; // using obfstr to obfuscate
use std::ffi::OsStr;
use std::fs;
use std::path::Path;

pub(crate) fn mv(args: &[String]) -> String {
    let source: String;
    let destination: String;

    if args.len() >= 2 {
        source = args[0].clone();
        let destination_str = args[1..].join(" ");
        destination = destination_str;
    } else {
        return format!(
            "Invalid number of arguments received. Usage: 'mv [source] [destination]'."
        );
    }

    let source_path = Path::new(&source);
    let destination_path = Path::new(&destination);
    let mut new_destination_path = destination_path.to_path_buf();

    if !&source_path.exists() {
        return format!("Failed to move, '"{source_path.to_string_lossy()}"' does not exist.");
    }

    if !&source_path.is_dir() && !&source_path.is_file() {
        return format!("Failed to move, '"{source_path.to_string_lossy()}"' is not a file or directory.");
    }

    if source_path.is_dir() {
        // Moving a directory

        if !destination_path.exists() {
            // Destination does not exist, move the source directory as a new directory with the destination name
            if let Err(e) = transfer_dir_to(source_path, destination_path, true) {
                return e;
            }
        } else if destination_path.is_dir() {
            // Destination exists as directory, move the directory as a subdirectory of the destination, preserving its name
            new_destination_path = Path::new(&destination)
                .join(source_path.file_name().unwrap_or_else(|| OsStr::new("")));
            if let Err(e) = transfer_dir_to(source_path, &new_destination_path, true) {
                return e;
            }
        } else {
            // Destination exists as file, return an error message
            return format!("Failed to move, '"{new_destination_path.to_string_lossy()}"' exists as a file.");
        }
    } else {
        // Moving a file

        if !destination_path.exists() {
            // Destination does not exist, move the file as the destination path
            if let Err(e) = fs::rename(source_path, destination_path) {
                return format!("Failed to move file: "{e});
            }
        } else if destination_path.is_dir() {
            // Destination exists as directory, move the file into the destination directory
            new_destination_path = Path::new(&destination)
                .join(source_path.file_name().unwrap_or_else(|| OsStr::new("")));
            if let Err(e) = fs::rename(source_path, &new_destination_path) {
                return format!("Failed to move file: "{e});
            }
        } else {
            // Destination exists as file, return an error message
            return format!("Failed to move, '"{new_destination_path.to_string_lossy()}"' already exists.");
        }
    }

    format!("Successfully moved '"{source_path.to_string_lossy()}"' to '"{new_destination_path.to_string_lossy()}"'.")
}
