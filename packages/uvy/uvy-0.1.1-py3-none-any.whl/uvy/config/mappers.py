from typing import Any

from uvy.config.models import UvConf, Workspace

__all__ = ["to_workspace", "to_uv"]


def to_workspace(data: dict[str, Any]) -> Workspace:
    return Workspace(members=data["members"], exclude=data["exclude"])


def to_uv(data: dict[str, Any]) -> UvConf:
    return UvConf(
        workspace=to_workspace(data["workspace"]),
    )
