use tokio::sync::{mpsc};
use tokio::time::{sleep, Duration};
use futures::future::join_all;
use chrono::Utc;
use futures::FutureExt;

use indicatif::{ProgressBar, ProgressStyle};

use crate::fetcher::app::{APPLICATION};
use crate::fetcher::client::new_client;
use crate::fetcher::runtime::new_runtime;
use crate::fetcher::{login, step};


pub fn new_progress(count :usize, jobs: usize, path: &str) -> Result<(), Box<dyn std::error::Error>>{

    APPLICATION.jobs_store(jobs);
    APPLICATION.set_local_path(path);

    let rt = new_runtime(count);
    let client = new_client();
    
    rt.block_on(async move {
        let _ = login::try_login().await;
    });

    let pb = ProgressBar::new(0);
    let sty = ProgressStyle::with_template(
        "[{elapsed_precise}] {bar:100.cyan/blue} {pos:>7}/{len:7} {msg}",
    )
        .unwrap()
        .progress_chars("##-");
    pb.set_style(sty);

    let status_handle= rt.spawn(step::run_status());

    let (tx, mut rx) = mpsc::channel::<String>(jobs);
    rt.spawn(step::run_progress(client.clone(), tx.clone())); // 下载文件
    drop(tx);

    let pb1 = pb.clone();
    let progress_handle= rt.spawn(async move {
        while let Some(name) = rx.recv().await {
            APPLICATION.download_count_add(1);

            pb1.set_length(APPLICATION.count_get());
            pb1.set_message(format!("download_size: {} download_count: {}", APPLICATION.download_size_get(),  APPLICATION.download_count_get()));
            pb1.inc(1);
     
            tracing::debug!("download_complete: {}", name);
        }
    });


    let (tx_watch, mut rx_watch) = mpsc::channel::<i64>(jobs);
    rt.spawn(async move {
        loop {
            if let Some(_) = rx_watch.recv().now_or_never() {
                println!("收到退出信号，退出循环");
                break;
            }
            sleep(Duration::from_millis(500)).await;
        }
    });

    // 等待所以任务处理完成
    rt.block_on(async move {
        #[cfg(unix)]
        let signal_future = async {
            let mut sigint = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::interrupt()).expect("");
            let mut sigterm = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate()).expect("");

            tokio::select! {
            _ = sigint.recv() => {
                println!("\n收到中断信号 (Ctrl+C)，正在退出...");
            },
            _ = sigterm.recv() => {
                println!("\n收到终止信号，正在退出...");
            }
        }
        };

        #[cfg(windows)]
        let signal_future = async {
            tokio::signal::ctrl_c().await.expect("Failed to install Ctrl+C handler");
            println!("\n收到 Ctrl+C 信号，正在退出...");
        };

        tokio::select! {
            _ = join_all(vec![progress_handle, status_handle]) => {}
            _ = signal_future => {
                drop(tx_watch);
            }
        }

        sleep(Duration::from_millis(500)).await;
        tracing::debug!("{:?}", APPLICATION.chunk_size);
    });

    let start_timestamp = APPLICATION.start_timestamp.try_read().unwrap().clone();
    let stop_timestamp = Utc::now().timestamp_millis();
    // pb.finish_and_clear();
    pb.set_message(format!("download_size: {} download_count: {}", APPLICATION.download_size_get(),  APPLICATION.download_count_get()));
    println!("\ndownload, use: {} ms, download_size: {} ", stop_timestamp-start_timestamp, APPLICATION.download_size_get());

    Ok(())
}
