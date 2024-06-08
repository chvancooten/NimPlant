use fmtools::format;

fn parse_sleep_time(arg: &str, client: &mut crate::app::client::Client) -> Result<(), String> {
    match arg.parse::<u32>() {
        Ok(n) => {
            client.sleep_time = n;
            Ok(())
        }
        Err(_) => Err(format!("Invalid sleep time.")),
    }
}

fn parse_jitter(arg: &str, client: &mut crate::app::client::Client) -> Result<(), String> {
    match arg.parse::<f64>() {
        Ok(n) => {
            client.sleep_jitter = match n {
                n if n < 0.0 => 0.0,
                n if n > 100.0 => 1.0,
                _ => n / 100.0,
            };
            Ok(())
        }
        Err(_) => Err(format!("Invalid jitter time.")),
    }
}

pub(crate) fn sleep(args: &[String], client: &mut crate::app::client::Client) -> String {
    match args.len() {
        1 => {
            if let Err(e) = parse_sleep_time(&args[0], client) {
                return e;
            }
        }
        2 => {
            if let Err(e) = parse_sleep_time(&args[0], client) {
                return e;
            }
            if let Err(e) = parse_jitter(&args[1], client) {
                return e;
            }
        }
        _ => return format!("Invalid number of arguments."),
    }

    format!("Sleep time changed to "{client.sleep_time}" seconds ("{client.sleep_jitter*100.0}"% jitter).")
}
