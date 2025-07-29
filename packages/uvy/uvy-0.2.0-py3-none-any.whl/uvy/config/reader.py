import tomli

from uvy.config.mappers import to_uv
from uvy.config.models import UvConf


def read_uv_config(file_path: str) -> UvConf:
    with open(file_path, "rb") as file:
        data = tomli.load(file)

    return to_uv(data["tool"]["uv"])
