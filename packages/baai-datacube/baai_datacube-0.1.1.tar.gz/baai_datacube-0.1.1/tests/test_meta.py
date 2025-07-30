if __name__ == "__main__":
    from baai_datacube.meta import download_meta


    meta_test = download_meta("1949989787863748608", "https://datacube.baai.ac.cn/api")
    lines = meta_test.split("\n")
    print(len(lines))