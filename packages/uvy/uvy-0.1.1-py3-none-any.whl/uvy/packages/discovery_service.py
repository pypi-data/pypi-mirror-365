import fnmatch
from pathlib import Path
from typing import Final, List
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager

from uvy.config.uvy import read_uvy_conf
from uvy.packages.models import Package

__all__ = ["PackageDiscoveryService"]

PACKAGE_MARKER_FILE: Final[str] = "pyproject.toml"


class PackageDiscoveryService:
    def discover_packages(
        self, base_paths: List[str], exclude_patterns: List[str] = []
    ) -> List[Package]:
        members = self.get_packages_base_dirs(base_paths, exclude_patterns)
        return [self.get_package(member) for member in members]

    def get_packages_base_dirs(
        self, base_paths: List[str], exclude_patterns: List[str] = []
    ) -> List[str]:
        return list(
            {
                str(path)
                for base_path in base_paths
                for path in Path().glob(base_path)
                for marker_path in path.glob(PACKAGE_MARKER_FILE)
                if not any(
                    fnmatch.fnmatch(str(marker_path.parent), pattern)
                    for pattern in exclude_patterns
                )
            }
        )

    def get_package(self, path: str) -> Package:
        metadata = ProjectMetadata(path, PluginManager())

        data = read_uvy_conf(f"{path}/pyproject.toml")

        package = Package(
            name=metadata.name,
            path=metadata.root,
            version=metadata.version,
            dependencies=metadata.core.dependencies_complex,
            tags=data.tags,
        )

        return package
