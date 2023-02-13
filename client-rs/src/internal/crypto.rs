use aes::Aes128;
use base64::encode;
use ctr::cipher::stream::{NewStreamCipher, SyncStreamCipher};
use ctr::Ctr128;
use std::str;

use crate::internal::helpers::random_string;
use base64::decode;

type Aes128Ctr = Ctr128<Aes128>;

pub(crate) fn encrypt_data(s: Vec<u8>, key: &[u8]) -> String {
    let mut data: Vec<u8> = s.clone();

    let random_string = random_string(16);
    let iv = random_string.as_bytes();
    let mut ciphertext = iv.to_vec();

    let mut cipher = Aes128Ctr::new(key.into(), iv.into());
    cipher.apply_keystream(&mut data);

    ciphertext.append(&mut data);

    let result = encode(ciphertext);

    return result;
}

pub(crate) fn decrypt_data(s: String, key: &[u8]) -> String {
    if s.is_empty() {
        return s
    }

    let data: Vec<u8> = decode(s).unwrap();

    let iv = &data[..16];
    let encrypted = &data[16..];
    let mut ciphertext = encrypted.to_vec().clone();

    let mut cipher = Aes128Ctr::new(key.into(), iv.into());
    cipher.apply_keystream( &mut ciphertext);

    return match str::from_utf8(&ciphertext) {
        Ok(v) => v.to_string(),
        Err(_) => "".to_string(),
    };
}

pub(crate) fn xor_bytes_to_string(s: &[u8], key: i64) -> String {
    let result = xor_bytes(s, key);


    let s = match str::from_utf8(&result[..]) {
        Ok(v) => v,
        Err(e) => panic!("Invalid UTF-8 sequence: {}", e),
    };

    return s.to_string()
}

pub(crate) fn xor_bytes(s: &[u8], key: i64) -> Vec<u8> {
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
