use std::sync::Arc;
use tokio::sync::{mpsc, Semaphore};
use tokio::fs::File;
use tokio::io::{BufReader, AsyncBufReadExt};
use reqwest::Client;
use chrono::Utc;
use crate::fetcher::app::{APPLICATION};
use crate::fetcher::download::{download_sign, download_size, download_part, download_merge, check_file};
use crate::fetcher::{login, meta};

pub async fn run_status(){
    let metadata_path = APPLICATION.metadata_path_get();
    let file = File::open(metadata_path).await.expect("无法打开文件");
    let reader = BufReader::new(file);
    let mut lines = reader.lines();
    while let Some(_line) = lines.next_line().await.expect("无法读取行") {
        APPLICATION.count_add(1);
    }
}

pub async fn run_progress(client:  Arc<Client>, tx: mpsc::Sender<String>) {
    let metadata_path = APPLICATION.metadata_path_get();

    let file = File::open(metadata_path).await;
    let mut lines = match file {
        Ok(file) => {
            let reader = BufReader::new(file);
            let lines = reader.lines();
            lines
        },
        Err(_error) => return,
    };
    
    // 并行分片下载
    let jobs = APPLICATION.jobs();
    let semaphore = Arc::new(Semaphore::new(jobs));
    loop {
        let  Some(line) = lines.next_line().await.ok() else {
            break
        };
        if line.is_none(){
            break
        }
        let line = line.unwrap();
        let video_metadata: meta::VideoMetadata = serde_json::from_str(&line).unwrap();
        let line = video_metadata.get_storage_path(); // TODO: 读取用户角色

        let _  = login::try_login().await.ok();
        let Some(sign_endpoint) = download_sign(client.as_ref(), line.as_str()).await.ok() else {
            break
        };

        let Some(size) = download_size(client.as_ref(), sign_endpoint.as_str()).await.ok() else {
            break
        };
        APPLICATION.size_add(size);

        // TODO: 并发检查
        if check_file(line.as_str()).unwrap_or(0) == size{
            tx.send(line.as_str().parse().unwrap()).await.unwrap();
            continue
        }

        // 监控所有分片下载完成
        let chunk_size = APPLICATION.chunk_size();
        let total_parts =  (size + chunk_size - 1) / chunk_size;

        // 每个文件都创建一下分片下载的最大检查队列
        let (tx_part, mut rx_part) = mpsc::channel::<(u64, i64)>(100);
        let watch_target = line.clone();
        let watch_tx = tx.clone();
        let watch_parts = total_parts - 1;
        tokio::spawn(async move {
            while let Some((idx_part,  start_timestamp)) = rx_part.recv().await {
                let stop_timestamp = Utc::now().timestamp_millis();
                tracing::debug!("download_part, {} part: {}/{} use: {} ms", watch_target, idx_part, watch_parts, stop_timestamp-start_timestamp);
            }
            // 下载完毕后合并分片
            let _ = download_merge(watch_target.as_str(), watch_parts+1).await;
            watch_tx.send(watch_target).await.unwrap()
        });

        for idx_part  in 0..total_parts {
            let download_target = line.clone();
            let download_idx = idx_part.clone();
            let download_chunk_size = chunk_size.clone();
            let download_semaphore = semaphore.clone();
            let download_tx = tx_part.clone();
            let download_client = client.clone();

            tokio::spawn(async move {
                let _permit = download_semaphore.acquire().await.unwrap();
                let timestamp = Utc::now().timestamp_millis();
                let start_pos = download_idx * download_chunk_size;
                let end_pos = std::cmp::min(start_pos + download_chunk_size, size) - 1;
                let download_result= download_part(download_client.as_ref(), download_target.as_str(), start_pos, end_pos).await.ok();
                if download_result.is_none(){
                    return
                }
                APPLICATION.download_size_add(download_result.unwrap());
                download_tx.send((download_idx,  timestamp)).await.unwrap();
            });
        }
        drop(tx_part); // 文件分片下载提交完毕
    }

    drop(tx)
}