use serde::{Deserialize, Serialize};
use serde_json::json;
use crate::fetcher::app::APPLICATION;
use crate::fetcher::response::JSONResp;
use crate::helper::jwt;

#[derive(Serialize, Deserialize)]
pub struct DataLogin{
    pub token: String
}

pub fn check_token(token: &str) -> Result<String, Box<dyn std::error::Error + Send + Sync>> {
    if token.is_empty(){
        return Err("token is empty".into());
    }

    let a = jwt::claims_parse(token).ok();
    if a.is_none() {
        return Err("claims_parse err".into());
    }
    if a.unwrap().is_expired(){
        return Err("expired".into());
    }
    Ok(token.to_string())
}
pub async fn refresh_token() -> Result<String, Box<dyn std::error::Error>>{
    let (access_key, secret_key) = APPLICATION.get_key();
    let api_host = APPLICATION.api_host_get();

    let resp = reqwest::Client::new()
        .post(api_host + "/auth/user-access-key-login")
        .header("Content-Type", "application/json")
        .json(&json!({
            "accessKey": access_key,
            "secretKey": secret_key
        }))
        .send().await?;

    let resp_staus= resp.status();
    if resp_staus != reqwest::StatusCode::OK {
        return Err("Login failed".into());
    }


    let resp_login: JSONResp<DataLogin> = resp.json().await.ok().unwrap();
    if resp_login.code != 0 {
        Err("Login failed".into())
    }else {
        Ok(resp_login.data.unwrap().token)
    }

}

pub async fn try_login()  -> Result<String, Box<dyn std::error::Error>>{
    let access_token = APPLICATION.get_access_token();
    let rs_check = check_token(access_token.as_str());
    if rs_check.is_ok(){
        return Ok(access_token);
    }
    let rs_refresh = refresh_token().await;
    if rs_refresh.is_ok(){
        let refresh_token = rs_refresh.ok().unwrap();
        APPLICATION.set_access_token(refresh_token.as_str());
    }
    tracing::debug!("try login, {:?}, {:?}", APPLICATION.get_key(), APPLICATION.get_access_token());
    Ok(APPLICATION.get_access_token())
}
