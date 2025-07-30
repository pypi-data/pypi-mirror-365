import os
import pathlib


DATACUBE_HOME = pathlib.Path(os.path.expanduser("~")) / ".cache" / "datacube"
DATACUBE_HOME.parent.mkdir(parents=True, exist_ok=True)
