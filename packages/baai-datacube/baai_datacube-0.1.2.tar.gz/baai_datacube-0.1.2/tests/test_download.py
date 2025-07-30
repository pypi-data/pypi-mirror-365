def test_download():
    from baai_datacube.downloader import dataset_download

    dataset_download("1949989787863748608", save_path="download")
