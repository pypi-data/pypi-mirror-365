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
    pub fn get_storage_path(&self) -> String {

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
