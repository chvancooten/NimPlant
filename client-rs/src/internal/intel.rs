use serde::{Serialize, Deserialize};
use whoami;
use std::net::{ToSocketAddrs};

#[derive(Serialize, Deserialize, PartialEq, Debug)]
pub struct InitialData {
    #[serde(rename = "i")]
    ip_address: String,
    #[serde(rename = "u")]
    username: String,
    #[serde(rename = "h")]
    hostname: String,
    #[serde(rename = "o")]
    os: String,
    #[serde(rename = "p")]
    pid: String,
}

impl InitialData {
    pub fn new() -> InitialData {
        return InitialData {
            ip_address: local_ip_address(),
            username: whoami::username(),
            hostname: whoami::hostname(),
            os: whoami::distro(),
            pid: std::process::id().to_string()
        };
    }
}

pub fn initial_data() -> InitialData {
    return InitialData::new()
}

pub fn local_ip_address() -> String {
    let local = "127.0.0.1".to_string();

    let hostname = whoami::hostname();

    let mut addrs_iter = format!("{}:0", hostname).to_socket_addrs().unwrap();

    return match addrs_iter.next() {
        Some(address) => address.to_string(),
        None => local,
    };
}

pub fn username() -> String {
    return whoami::username();
}

