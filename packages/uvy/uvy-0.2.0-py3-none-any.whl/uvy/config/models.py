from dataclasses import dataclass

__all__ = ["Workspace", "UvConf"]


@dataclass
class Workspace:
    members: list[str]
    exclude: list[str]


@dataclass
class UvConf:
    workspace: Workspace
