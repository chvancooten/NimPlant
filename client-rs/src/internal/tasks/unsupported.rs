#[cfg(not(target_os = "windows"))]
pub fn reply(task: &str) -> String {
    return format!("`{}` is not supported on this platform.", task);
}