use once_cell::sync::Lazy;
use std::sync::{Arc, RwLock};
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use chrono::Utc;

#[warn(dead_code)]
pub(crate) struct Application{
    pub path: Arc<RwLock<String>>, // 文件保存位置
    pub count: AtomicU64,
    pub size: AtomicU64,
    pub chunk_size: AtomicU64,
    pub start_timestamp: Arc<RwLock<i64>>,
    pub metadata_path: Arc<RwLock<String>>, // 元数据文件保存位置
    pub download_count: AtomicU64, // 已经下载的文件数
    pub download_size: AtomicU64, // 已经下载的大小
    pub jobs: AtomicUsize, // 下载任务数

    pub api_host: Arc<RwLock<String>>, // 接口
    /// 密钥
    pub _access_key: Arc<RwLock<String>>,
    pub _secret_key: Arc<RwLock<String>>,
    pub _access_token: Arc<RwLock<String>>,

}

impl Application {
    pub fn new() -> Self {
        let timestamp = Utc::now().timestamp_millis();
        Self {
            count: AtomicU64::new(0),
            size: AtomicU64::new(0),
            path: Arc::new(RwLock::new("".to_string())),
            chunk_size: AtomicU64::new(1024 * 1024 * 5),
            start_timestamp: Arc::new(RwLock::new(timestamp)),
            metadata_path: Arc::new(RwLock::new("".to_string())),
            download_count: AtomicU64::new(0), // 下载大小
            download_size: AtomicU64::new(0), // 下载大小
            jobs: AtomicUsize::new(0),
            
            api_host: Arc::new(RwLock::new("".to_string())),

            _access_key: Arc::new(RwLock::new("".to_string())),
            _secret_key: Arc::new(RwLock::new("".to_string())),
            _access_token: Arc::new(RwLock::new("".to_string())),
        }
    }
    pub fn set_key(&self, access_key: &str, secret_key: &str) {
        let mut  access_guard= self._access_key.write().unwrap();
        access_guard.clear();
        access_guard.push_str(access_key);

        let mut  secret_guard= self._secret_key.write().unwrap();
        secret_guard.clear();
        secret_guard.push_str(secret_key);
    }

    pub fn get_key(&self) -> (String, String) {
        let access_guard = self._access_key.read().unwrap();
        let secret_guard = self._secret_key.read().unwrap();
        (access_guard.clone(), secret_guard.clone())
    }
    
    pub fn set_access_token(&self, token: &str) {
        let mut  access_guard= self._access_token.write().unwrap();
        access_guard.clear();
        access_guard.push_str(token);
    }
    pub fn get_access_token(&self) -> String {
        let access_guard = self._access_token.read().unwrap();
        access_guard.clone()
    }


    pub fn set_local_path(&self, path: &str) {
        let read_guard = self.path.read().unwrap();
        if !read_guard.is_empty() {
            return; // 已设置，直接返回
        }
        drop(read_guard);

        let mut write_guard = self.path.write().unwrap();
        if !write_guard.is_empty() {
            return; // double-check
        }

        write_guard.clear();
        write_guard.push_str(path);
        drop(write_guard);
    }
    pub fn local_path_get(&self) -> String {
        let read_guard = self.path.read().unwrap();
        read_guard.clone()
    }

    pub fn count_add(&self, count: u64){
        self.count.fetch_add(count, Ordering::Relaxed);
    }
    
    pub fn count_get(&self) -> u64{
        self.count.fetch_or(0, Ordering::Relaxed)
    }
    pub fn size_add(&self, size: u64){
        self.size.fetch_add(size, Ordering::Relaxed);
    }
    
    pub fn chunk_size(&self) -> u64{
        self.chunk_size.fetch_or(0, Ordering::Relaxed)
    }
    
    
    pub fn download_count_add(&self, size: u64) -> u64 {
        self.download_count.fetch_add(size, Ordering::Relaxed)
    }
    
    pub fn download_count_get(&self) -> u64{
        self.download_count.fetch_or(0, Ordering::Relaxed)
    }
    pub fn download_size_add(&self, size: u64) -> u64{
        self.download_size.fetch_add(size, Ordering::Relaxed)
    }
    pub fn download_size_get(&self) -> u64{
        self.download_size.fetch_or(0, Ordering::Relaxed)
    }

    pub fn jobs_store(&self, nums: usize){
        self.jobs.store(nums, Ordering::Relaxed);
    }

    pub fn jobs(&self) -> usize{
        self.jobs.load(Ordering::Relaxed)
    }

    // metadata_path
    pub fn metadata_path_set(&self, path: &str) {
        let mut  read_guard = self.metadata_path.write().unwrap();
        read_guard.clear();
        read_guard.push_str(path);
    }
    pub fn metadata_path_get(&self) -> String {
        let read_guard = self.metadata_path.read().unwrap();
        read_guard.clone()
    }
    
    pub fn api_host_set(&self, host: &str) {
        let mut  read_guard = self.api_host.write().unwrap();
        read_guard.clear();
        read_guard.push_str(host);
    }
    
    pub fn api_host_get(&self) -> String {
        let read_guard = self.api_host.read().unwrap();
        read_guard.clone()
    }
}


pub static APPLICATION: Lazy<Arc<Application>> = Lazy::new(|| {
    Arc::new(Application::new())
});
