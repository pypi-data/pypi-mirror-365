mod fetcher;
mod helper;

use pyo3::prelude::*;
use crate::fetcher::app::APPLICATION;
use crate::fetcher::logger;

/// Download files.
#[pyfunction]
fn run_progress(
    count: usize, size: usize, 
    access_key: &str, secret_key: &str, 
    save_path: &str, metadata_path: &str,
    api_host: &str,
) -> PyResult<String> {
    logger::init_logger();

    APPLICATION.api_host_set(api_host);
    APPLICATION.set_key(access_key, secret_key);
    APPLICATION.metadata_path_set(metadata_path); // 设置下载的元数据文件路径
    
    fetcher::progress::new_progress(count, size, save_path).unwrap();
    Ok("".to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn baai_datacube(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_progress, m)?)?;
    Ok(())
}
