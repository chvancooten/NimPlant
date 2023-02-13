use crate::internal::listener;

pub async fn run() -> Result<(), Box<dyn std::error::Error>> {
    setup()?;

    let mut listener = listener::Listener::new().await?;

    while listener.can_run() {
        if !listener.ready() {
            listener.register().await?
        }

        listener.work().await?;
        listener.sleep().await?;
    }

    Ok(())
}

fn setup() -> Result<(), Box<dyn std::error::Error>> {
    #[cfg(any(feature = "debug_assertions", feature = "debug"))]
    {
        if std::env::var("RUST_BACKTRACE").is_err() {
            std::env::set_var("RUST_BACKTRACE", "full")
        }

        if std::env::var("RUST_LIB_BACKTRACE").is_err() {
            std::env::set_var("RUST_LIB_BACKTRACE", "1")
        }

        if std::env::var("RUST_LOG").is_err() {
            std::env::set_var("RUST_LOG", "info")
        }
    }

    Ok(())
}
