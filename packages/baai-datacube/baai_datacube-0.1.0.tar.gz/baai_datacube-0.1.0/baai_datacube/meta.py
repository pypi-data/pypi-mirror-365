import json

import requests

from .config import DATACUBE_HOME

def download_meta(dataset_id: str, host="http://127.0.0.1:30201"):
    login_api = f"{host}/auth/user-access-key-login"

    config_path = DATACUBE_HOME / "config.json"

    with open(config_path) as f:
        config = json.load(f)

    access_key = config.get("access_key")
    secret_key = config.get("secret_key")

    resp_login = requests.post(login_api, json={"accessKey": access_key, "secretKey": secret_key})
    token = resp_login.json().get("data").get("token")



    meta_api = f"{host}/storage/download/{dataset_id}"
    resp_meta = requests.get(meta_api, headers={"Authorization": f"Bearer {token}"})
    return resp_meta.text


if __name__ == "__main__":
    download_meta("1949761500801536000")

