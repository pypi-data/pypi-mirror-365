from dataclasses import asdict, dataclass
from typing import Dict, Final, List, Optional
import re

from uvy.config.reader import read_uv_config
from uvy.data_printer.factory import OutputFormat, TabularDataPrinterFactory
from uvy.graph.dg import DependencyGraph
from uvy.packages.discovery_service import PackageDiscoveryService
from uvy.packages.models import Package
from uvy.packages.package_registry import PackageRegistryService


COLUMN_DEFINITIONS: Final[Dict[str, str]] = {
    "name": "Name",
    "path": "Path",
    "version": "Version",
    "tags": "Tags",
}


@dataclass
class PackageFilters:
    name: Optional[str] = None
    tags: Optional[list[str]] = None
    with_dependents: bool = False
    with_dependees: bool = False


def _match_pattern(pattern: str, value: str) -> bool:
    # Try exact match first
    if pattern == value:
        return True
    # Try regex match, fallback to False if invalid regex
    try:
        return re.fullmatch(pattern, value) is not None
    except re.error:
        return False


def matches_package_filter(package: Package, filters: PackageFilters) -> bool:
    if filters.name:
        if not _match_pattern(filters.name, package.name):
            return False
    if filters.tags:
        # All tags in filters must be matched by at least one tag in package.tags
        for tag_pattern in filters.tags:
            if not any(_match_pattern(tag_pattern, tag) for tag in package.tags):
                return False
    return True


class PackagesFacade:
    discovery_service: PackageDiscoveryService
    registry_service: PackageRegistryService

    def __init__(self) -> None:
        self.discovery_service = PackageDiscoveryService()
        self.registry_service = PackageRegistryService()
        self.dependency_service = DependencyGraph[Package]()

    def load_packages(self, include: List[str], exclude: List[str]) -> None:
        all_packages = self.discovery_service.discover_packages(base_paths=include, exclude_patterns=exclude)

        self.registry_service.load(all_packages)

        for package in all_packages:
            for dep, dep_req in package.dependencies.items():
                dep_package = self.registry_service.get_package(dep_req.name)
                if dep_package is None:
                    continue
                self.dependency_service.add_edge(package, dep_package)

    def filter(self, filters: PackageFilters) -> List[Package]:
        """
        Filters the packages based on the provided filters.
        This method can be expanded to implement actual filtering logic.
        """

        filtered_packages = [
            package for package in self.registry_service.packages.values() if matches_package_filter(package, filters)
        ]

        transitive_packages: List[Package] = []
        if filters.with_dependents:
            transitive_packages.extend(self.dependency_service.get_dependents_of(filtered_packages))

        if filters.with_dependees:
            transitive_packages.extend(self.dependency_service.get_dependees_of(filtered_packages))

        return list(set(filtered_packages + transitive_packages))


def packages_command(
    columns: List[str],
    format: OutputFormat,
    tags: List[str],
    with_dependents: bool,
    with_dependees: bool,
) -> None:
    """
    This function is a placeholder for the 'list' command in the CLI.
    It currently does nothing but can be expanded in the future.
    """
    package_filters = PackageFilters(
        name=None,
        tags=tags,
        with_dependents=with_dependents,
        with_dependees=with_dependees,
    )

    uv_conf = read_uv_config("pyproject.toml")

    facade = PackagesFacade()
    facade.load_packages(uv_conf.workspace.members, uv_conf.workspace.exclude)
    packages = facade.filter(package_filters)
    packages.sort(key=lambda x: x.name)

    printer = TabularDataPrinterFactory.create(format)
    tabular_data = [
        {k: ", ".join(map(str, v)) if isinstance(v, list) else v for k, v in asdict(package).items()}
        for package in packages
    ]

    filtered_ordered = {k: COLUMN_DEFINITIONS[k] for k in columns if k in COLUMN_DEFINITIONS}
    output = printer.output(tabular_data, filtered_ordered)

    print(output)
