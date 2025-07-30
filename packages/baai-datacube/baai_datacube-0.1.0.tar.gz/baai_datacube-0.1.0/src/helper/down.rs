use std::path::Path;


/// 生成保存到本地的文件路径
pub fn get_path(file_path: &str) -> Result<String, Box<dyn std::error::Error>>{
    let path = Path::new(file_path);
    let down_name = path.file_name().unwrap().to_str().unwrap().to_string();
    let down_path = path.parent().unwrap().file_name().unwrap().to_str().unwrap().to_string();
    let download_name = format!("{}/{}", down_path, down_name);
    Ok(download_name)
}


#[test]
pub fn test(){
    let source_path = "ks3://baai-datasets/d714895cca28be958783d0b358ba9e56/data/mask/o_0810cb44.png";
    let target_path = get_path(source_path).ok().unwrap_or("".to_string());
    assert_eq!(target_path, "mask/o_0810cb44.png")
}