from typing import Dict, List, Optional

from uvy.packages.models import Package

__all__ = ["PackageRegistryService"]


class PackageRegistryService:
    def __init__(self) -> None:
        self.packages: Dict[str, Package] = {}

    def load(self, packages: List[Package]):
        for package in packages:
            self.add_package(package)

    def add_package(self, package: Package):
        self.packages[package.name] = package

    def get_package(self, name: str) -> Optional[Package]:
        return self.packages.get(name)

    # def get_all_packages(self) -> Collection[Package]:
    #     return Collection(self.packages.values())
