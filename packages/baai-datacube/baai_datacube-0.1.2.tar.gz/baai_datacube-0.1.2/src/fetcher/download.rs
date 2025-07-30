use std::path::Path;
use chrono::{Local, Utc};
use tokio::fs;
use tokio::io::AsyncWriteExt;

use reqwest::Client;
use reqwest::header::{RANGE};
use serde_json::json;
use serde::{Deserialize, Serialize};

use crate::fetcher::app::APPLICATION;
use crate::fetcher::hashlib::md5_compute;
use crate::fetcher::login;
use crate::fetcher::response::JSONResp;
use crate::helper::down;

#[derive(Serialize, Deserialize)]
pub struct SignResponseCreate {
    /// 文件信息
    pub path: String,

    /// 签名地址
    pub endpoint: String,
}

pub async fn download_sign(client: &Client, sign_path: &str) -> Result<String, Box<dyn std::error::Error>>{
    let authorization = format!("Bearer {}", login::try_login().await.ok().unwrap());
    let host=  APPLICATION.api_host_get();

    let resp = client
        .post( host + "/storage/sign-generate")
        .header("Content-Type", "application/json")
        .header("Authorization", authorization)
        .json(&json!({
            "paths": vec!(sign_path)
        }))
        .send()
        .await;

    match resp {
        Ok(resp) => {
            let json_resp: JSONResp<Vec<SignResponseCreate>> = resp.json().await?;

            if json_resp.code != 0 {
                return Err("sign errr".into());
            }

            match json_resp.data {
                Some(data_list) => Ok(data_list[0].endpoint.clone()),
                None => Err("Missing data in response".into()),
            }

        },
        Err(e) => {
            Err(e.into())
        }
    }


}

pub async fn download_size(client: &Client, endpoint: &str) -> Result<u64, Box<dyn std::error::Error>> {
    let length = client.get(endpoint).send().await?.content_length();
    length.ok_or("Content-Length header missing".into())
}

/// 检查分块是否已经下载
pub async fn check_chunk(file_path: &str) -> Result<u64, Box<dyn std::error::Error>>{
    let metadata = std::fs::metadata(file_path)?;
    Ok(metadata.len())
}

/// 检查文件是否已经下载
pub fn check_file(file_path: &str) -> Result<u64, Box<dyn std::error::Error>>{
    let save_path= APPLICATION.local_path_get();
    let ext = Path::new(file_path).extension().and_then(|s| s.to_str()).unwrap();
    let dir_path =  md5_compute(file_path);
    let check_path = format!("{}/{}.{}", save_path, dir_path, ext);
    let metadata = std::fs::metadata(check_path)?;
    Ok(metadata.len())
}

pub async fn download_part(client: &Client, file_path: &str, start_pos: u64, end_pos: u64) -> Result<u64, Box<dyn std::error::Error>> {
    let now = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();

    let download_name= down::get_path(file_path).unwrap_or("2".parse().unwrap());
    tracing::debug!("download_part: download_name: {}, start_pos: {}, end_pos: {}", download_name, start_pos, end_pos);

    let part_hash =  md5_compute(file_path);
    let chunk_size = APPLICATION.chunk_size();

    let sign_path = download_sign(client, file_path).await.ok();
    if sign_path.is_none(){
        return Err("sign_path is none".into());
    }

    let save_path= APPLICATION.local_path_get();
    let part_name = format!("{}/{part_hash}_part_{}.bin", save_path, start_pos / chunk_size);


    let size = check_chunk(&part_name).await.ok().unwrap_or(0); // 检查是否需要下载
    if size == end_pos - start_pos + 1 {
        tracing::debug!("download_part: skip {} {} start_pos {} ============", now, part_name, start_pos);
        return Ok(0);
    }

    if size > 0 {
        tracing::debug!(
            "download_retry: {} start_pos: {}, end_pos: {}, require_size: {}, chunk_size: {:?}",
            part_name, start_pos, end_pos, end_pos - start_pos + 1, size
        );
    }


    let range = format!("bytes={}-{}", start_pos, end_pos);

    let resp_part = client.get(sign_path.clone().unwrap()).header(RANGE, range).send().await.ok();
    if resp_part.is_none(){
        tracing::debug!("download_part: {:?}  {} start_pos {}", now, part_name, start_pos);
        return Err("download_part response err".into());
    }

    let resp_part = resp_part.unwrap();
    if !resp_part.status().is_success(){
        return Err(format!("download_part: {:?}  {} {}", now, part_name, resp_part.status()).into());
    }
    
    let resp_bytes = resp_part.bytes().await.ok();
    if resp_bytes.is_none(){
        tracing::debug!("download_part: {:?}  {} start_pos {}", now, part_name, start_pos);
        return Err("download_part bytes err".into());
    }
    let bytes = resp_bytes.unwrap();

    let mut file = fs::File::create(part_name).await?;
    file.write_all(&bytes).await.unwrap();
    Ok(bytes.len() as u64)
}

pub async  fn download_merge(file_path: &str, chunk_nums: u64) -> Result<i64, Box<dyn std::error::Error>> {
    let start_timestamp = Utc::now().timestamp_millis();
    let save_path= APPLICATION.local_path_get();

    let ext = Path::new(file_path).extension().and_then(|s| s.to_str()).unwrap();
    let part_hash =  md5_compute(file_path);

    let merge_path = format!("{}/{}.{}", save_path, part_hash, ext);
    let _ = tokio::fs::remove_file(merge_path.clone()).await.unwrap_or( ());

    let mut dest_file = fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(merge_path.clone())
        .await?;

    for idx_part in 0..chunk_nums {
        tracing::debug!("download_merge: {} {}/{}",  file_path, idx_part, chunk_nums-1);
        let part_name = format!("{}/{part_hash}_part_{}.bin", save_path, idx_part);
        let mut part_file = fs::File::open(part_name).await?;
        tokio::io::copy(&mut part_file, &mut dest_file).await?;
    }
    for idx_part in 0..chunk_nums {
        let part_name = format!("{}/{part_hash}_part_{}.bin", save_path, idx_part);
        let _ = tokio::fs::remove_file(part_name).await.unwrap_or( ());
    }

    let stop_timestamp = Utc::now().timestamp_millis();

    Ok(stop_timestamp-start_timestamp)
}
