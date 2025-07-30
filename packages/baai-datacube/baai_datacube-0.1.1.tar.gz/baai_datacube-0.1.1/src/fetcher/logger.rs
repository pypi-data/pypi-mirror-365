use tracing_subscriber::fmt;
use tracing_subscriber::fmt::format::Writer;
use tracing_subscriber::fmt::time::FormatTime;
use tracing_subscriber::filter::LevelFilter;

struct LocalTimer;
impl FormatTime for LocalTimer {
    fn format_time(&self, w: &mut Writer<'_>) -> std::fmt::Result {
        write!(w, "{}", chrono::Local::now().format("%FT%T%.3f"))
    }
}


pub fn init_logger() {
    fmt().with_timer(LocalTimer).with_max_level(LevelFilter::INFO) .init();
}

