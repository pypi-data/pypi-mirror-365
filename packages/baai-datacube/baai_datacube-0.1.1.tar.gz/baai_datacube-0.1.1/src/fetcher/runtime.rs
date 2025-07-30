use tokio::runtime::Builder;

pub fn new_runtime(count: usize) -> tokio::runtime::Runtime{
    let rt = Builder::new_multi_thread()
        .worker_threads(count)
        .enable_all()
        .build()
        .unwrap();
    rt
}