from dataclasses import dataclass
from typing import Any
from packaging.requirements import Requirement


@dataclass
class Package:
    name: str
    path: str
    version: str
    dependencies: dict[str, Requirement]
    tags: list[str]

    def __eq__(self, other: Any):
        if not isinstance(other, Package):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
