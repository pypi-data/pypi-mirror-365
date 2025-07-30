#[allow(dead_code)]
#[derive(Debug, serde::Deserialize)]
pub struct VideoMetadata {
    #[serde(rename = "videoId")]
    pub video_id: i64,
    #[serde(rename = "scene")]
    pub scene: String,
    #[serde(rename = "resolutionHeight")]
    pub resolution_height: String,
    pub duration: String,
    #[serde(rename = "fileExt")]
    pub file_ext: String,
    #[serde(rename = "nFfE2LvQ")]
    pub source_is_self: String,
    #[serde(rename = "DO2I1Wev")]
    pub source_is_koala: String,
    #[serde(rename = "hashedVideoIdYt")]
    pub hashed_video_id_yt: String,
    pub score: f64,
}


impl VideoMetadata {
    pub fn get_storage_path(&self, user_role: i64) -> String {
        if user_role == 1 {
            format!(
                "ks3://baai-video-clips/yt/{}/koala-36m_{}.{}",
                self.hashed_video_id_yt, self.scene, self.file_ext
            )
        } else {
            if self.source_is_self == "1" {
                format!(
                    "ks3://baai-video-clips/yt/{}/{}.{}",
                    self.hashed_video_id_yt, self.scene, self.file_ext
                )
            } else {
                format!(
                    "ks3://baai-video-clips/yt/{}/koala-36m_{}.{}",
                    self.hashed_video_id_yt, self.scene, self.file_ext
                )
            }
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::{BufRead, BufReader};
    use serde_json;

    #[test]
    fn test_parse_jsonl_file() -> Result<(), Box<dyn std::error::Error>> {
        // 假设你有一个名为 test.jsonl 的文件
        let file = File::open("example/1cf8866d-fe36-497b-9511-4a043f5803c2.jsonl")?;
        let reader = BufReader::new(file);

        for line in reader.lines() {
            let line = line?;
            if line.trim().is_empty() {
                continue; // 跳过空行
            }
            let video_metadata: VideoMetadata = serde_json::from_str(&line)?;
            println!("{:?}", video_metadata.get_storage_path(1));
        }
        Ok(())
    }
}