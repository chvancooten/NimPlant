use fmtools::format; // using obfstr to obfuscate
use serde::Deserialize;
use wmi::{COMLibrary, WMIConnection};

#[derive(Deserialize, Debug)]
#[allow(non_camel_case_types, non_snake_case)]
struct Win32_GroupUser {
    GroupComponent: String,
    PartComponent: String,
}

pub(crate) fn get_local_admins() -> String {
    let com_con = match COMLibrary::new() {
        Ok(con) => con,
        Err(e) => return format!("Failed to initialize COM library: "{e}),
    };

    let wmi_con = match WMIConnection::new(com_con) {
        // WMIConnection::new uses ROOT\CIMv2 by default
        Ok(con) => con,
        Err(e) => return format!("Failed to connect to WMI: "{e}),
    };

    let res = match wmi_con.raw_query::<Win32_GroupUser>(&format!(
        "SELECT GroupComponent, PartComponent FROM Win32_GroupUser"
    )) {
        Ok(res) => res,
        Err(e) => return format!("Failed to query WMI: "{e}),
    };

    // Loop over the results and build a string of the local admins
    let mut admins = Vec::<String>::new();
    for group_user in res {
        // Get the group name from GroupComponent
        let group = group_user.GroupComponent.split('"').collect::<Vec<&str>>()[3];
        if group == format!("Administrators") {
            // Get the username from the PartComponent
            let user = group_user.PartComponent.split('"').collect::<Vec<&str>>()[3];
            admins.push(user.to_string());
        }
    }

    if admins.is_empty() {
        format!("No local administrators found.")
    } else {
        format!("Local administrators: "{admins.join(", ")})
    }
}
