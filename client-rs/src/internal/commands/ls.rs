use chrono::{DateTime, Local};
use fmtools::format;
use std::time::SystemTime; // using obfstr to obfuscate

// Helper function to format time from metadata
fn format_time(time: &std::io::Result<SystemTime>, datetime_format: &str) -> String {
    match time {
        Ok(t) => DateTime::<Local>::from(*t)
            .format(datetime_format)
            .to_string(),
        Err(_) => "Unknown".to_string(),
    }
}

pub(crate) fn ls(path: &str) -> String {
    let datetime_format = "%Y-%m-%d %H:%M";

    // If path is not provided, list the current directory
    let path = if path.is_empty() {
        std::env::current_dir().unwrap_or_else(|_| std::path::PathBuf::from("."))
    } else {
        std::path::PathBuf::from(path)
    };

    if let Ok(entries) = std::fs::read_dir(&path) {
        let mut result = String::new();
        let mut directories = Vec::new();
        let mut files = Vec::new();

        // Print header
        result.push_str(&format!("Directory listing for directory '"{path.display()}"'.\n\n"));
        result.push_str(&format!(
            {"TYPE":<10}
            {"NAME":<50.50}
            {"SIZE":<10}
            {"CREATED":<20}
            {"MODIFIED":<20}
            "\n"
        ));

        for entry in entries {
            match entry {
                Ok(entry) => {
                    // Get the file information
                    let Ok(metadata) = entry.metadata() else {
                        continue;
                    };
                    let file_type = if metadata.is_dir() { "[DIR]" } else { "[FILE]" };
                    let file_size = if metadata.is_dir() {
                        String::new()
                    } else {
                        // Get the file size in human readable format
                        let size = metadata.len();
                        if size < 1024 {
                            format!({size}"B")
                        } else if size < 1024 * 1024 {
                            format!({size / 1024}"KB")
                        } else if size < 1024 * 1024 * 1024 {
                            format!({size / 1024 / 1024}"MB")
                        } else {
                            format!({size / 1024 / 1024 / 1024}"GB")
                        }
                    };

                    let created_time_formatted = format_time(&metadata.created(), datetime_format);
                    let last_write_time_formatted =
                        format_time(&metadata.modified(), datetime_format);

                    // Add the entry to the result
                    let formatted_entry = &format!(
                        {file_type:<10}
                        {&entry.file_name().to_string_lossy():<50.50}
                        {file_size:<10}
                        {created_time_formatted:<20}
                        {last_write_time_formatted:<20}
                        "\n"
                    );

                    if metadata.is_dir() {
                        directories.push(formatted_entry.to_string());
                    } else {
                        files.push(formatted_entry.to_string());
                    }
                }
                Err(_) => {
                    result.push_str(&format!("Error listing directory item.\n"));
                }
            }
        }
        result.push_str(&directories.join(""));
        result.push_str(&files.join(""));

        result
    } else {
        format!("Error listing directory.")
    }
}
