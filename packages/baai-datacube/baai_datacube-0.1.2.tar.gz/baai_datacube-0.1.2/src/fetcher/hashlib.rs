use md5;

pub fn md5_compute(file_path: &str) -> String {
    let digest = md5::compute(file_path);
    format!("{:x}", digest)
}
