import os
import json
import pathlib

from .baai_datacube import run_progress
from .config import DATACUBE_HOME
from .meta import download_meta

def dataset_download(dataset_id, save_path="."):

    config_path = DATACUBE_HOME / "config.json"

    if not config_path.exists():
        print("请先登录")
        return

    with config_path.open("r") as fr:
        config = json.load(fr)

    access_key = config.get("access_key")
    secret_key = config.get("secret_key")

    format_save_path =  os.getcwd() if save_path == "." else save_path
    path = pathlib.Path(format_save_path)
    if not pathlib.Path(format_save_path).exists():
        print(f"{path.resolve()}, 保存路径不存在")
    save_path = path.resolve().__str__()

    # TODO: 根据数据集下载meta文件信息
    resp_meta = download_meta(dataset_id)

    meta_path = path / f"{dataset_id}_meta.bin"
    with meta_path.open("w") as fw:
        fw.write(resp_meta)
    # TODO: 编写下载文件位置
    run_progress(4, 10, access_key, secret_key, save_path, meta_path.resolve().__str__())
    meta_path.unlink()
