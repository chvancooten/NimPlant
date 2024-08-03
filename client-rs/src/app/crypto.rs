use aes::cipher::{KeyIvInit, StreamCipher};
use base64::{engine::general_purpose::STANDARD, Engine as _};
use rand::distributions::Alphanumeric;
use rand::Rng;
use std::str;

type Aes128Ctr64BE = ctr::Ctr64BE<aes::Aes128>;

pub(crate) fn random_string(n: usize) -> String {
    rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(n)
        .map(char::from)
        .collect()
}

pub(crate) fn xor_bytes(s: &[u8], key: i64) -> Vec<u8> {
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

pub(crate) fn encrypt_data(s: &[u8], key: &[u8]) -> String {
    let mut data: Vec<u8> = s.to_vec();

    let random_string = random_string(16);
    let iv = random_string.as_bytes();
    let mut ciphertext = iv.to_vec();

    let mut cipher = Aes128Ctr64BE::new(key.into(), iv.into());
    cipher.apply_keystream(&mut data);

    ciphertext.append(&mut data);

    STANDARD.encode(ciphertext)
}

pub(crate) fn decrypt_data(s: String, key: &[u8]) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    if s.is_empty() {
        return Ok(vec![]);
    }

    let data: Vec<u8> = STANDARD.decode(s)?;

    let iv = &data[..16];
    let encrypted = &data[16..];
    let mut plaintext = encrypted.to_vec().clone();

    let mut cipher = Aes128Ctr64BE::new(key.into(), iv.into());
    cipher.apply_keystream(&mut plaintext);

    Ok(plaintext)
}

pub(crate) fn decrypt_string(s: String, key: &[u8]) -> Result<String, Box<dyn std::error::Error>> {
    let plaintext = decrypt_data(s, key)?;
    Ok(str::from_utf8(&plaintext)?.to_string())
}
