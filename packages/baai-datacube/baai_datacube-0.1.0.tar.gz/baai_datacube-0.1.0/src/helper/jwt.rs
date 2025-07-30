use std::fmt::Debug;
use base64::prelude::*;
use serde::{Deserialize, Serialize};


#[derive(Debug, Serialize, Deserialize)]
pub struct JwtClaims {
    pub sub: String,     // subject（用户ID）
    pub iat: u64,        // issued at（签发时间）
    pub exp: u64,        // expiration（过期时间）
}

impl JwtClaims {
    /// 检查 token 逻辑过期检查
    pub fn is_expired(&self) -> bool {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("时间异常")
            .as_secs();
        self.exp <= now + 60 * 5
    }
}
pub fn claims_parse(token: &str) -> Result<JwtClaims, Box<dyn std::error::Error>>{
    let parts: Vec<&str> = token.split('.').collect();
    if parts.len() != 3 {
        return Err("invalid jwt token".into());
    }
    let payload = BASE64_URL_SAFE.decode(parts[1]);
    if payload.is_err() {
        return Err(payload.err().unwrap().into());
    }
    let plaintext = String::from_utf8(payload.ok().unwrap()).map_err(|e| e.to_string())?;
    let jwt_claims: JwtClaims = serde_json::from_str(&plaintext)?;
    Ok(jwt_claims)
}


#[test]
fn test(){
    let jwt_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI3MTMzODc1MjU3Njk3ODQ4Njc3IiwiaWF0IjoxNzUzMjM4MTMwLCJleHAiOjE3NTMyNDE3MzB9.AJJ3azG-tuHC7LKk3vqR7FIBA1_Yxk0HRaM9jcP7r7vFwEIEyiKh_KL8TBDkhs6FT72u2q_rb4_SlKNeAvQ_YQ";
    let jwt_clams = claims_parse(jwt_token).ok().unwrap();
    jwt_clams.is_expired();
}
