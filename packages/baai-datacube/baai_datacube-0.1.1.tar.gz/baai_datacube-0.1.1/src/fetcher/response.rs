use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct JSONResp<T> {
    /// 业务状态码（如 400, 500）
    pub code: i32,

    /// 业务状态码描述
    pub message: String,

    /// 完成时间（Unix 时间戳，毫秒）
    pub timestamp: u64,

    /// 返回数据（泛型）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<T>,
}
