use crate::internal::client::Client;
use fmtools::format; // using obfstr to obfuscate

pub(crate) fn curl(url: &str, client: &Client) -> String {
    if url.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'curl [URL]'.");
    }

    let response = ureq::get(url).set("User-Agent", &client.user_agent).call();

    match response {
        Ok(res) => match res.into_string() {
            Ok(body) => body,
            Err(e) => e.to_string(),
        },
        Err(e) => e.to_string(),
    }
}
