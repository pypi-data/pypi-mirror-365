from dataclasses import dataclass
from typing import Any, Dict, Optional, cast

import tomli


def get_by_dot_path(d: Dict[str, Any], path: str, default: Optional[Any] = None):
    keys = path.split(".")
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d


@dataclass
class UvyConf:
    tags: list[str]


def to_uvy_conf(data: dict[str, Any]) -> UvyConf:
    return UvyConf(
        tags=data.get("tags", []),
    )


def read_uvy_conf(file_path: str) -> UvyConf:
    with open(file_path, "rb") as file:
        data = tomli.load(file)

    uvy_data = cast(dict[str, Any], get_by_dot_path(data, "tool.uvy", {}))

    return to_uvy_conf(uvy_data)
