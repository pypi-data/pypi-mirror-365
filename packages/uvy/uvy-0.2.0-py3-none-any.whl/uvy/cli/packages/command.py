from dataclasses import asdict
from typing import Dict, Final, List

from uvy.config.reader import read_uv_config
from uvy.data_printer.factory import OutputFormat, TabularDataPrinterFactory
from uvy.packages.packages_facade import PackageFilters, PackagesFacade


COLUMN_DEFINITIONS: Final[Dict[str, str]] = {
    "name": "Name",
    "path": "Path",
    "version": "Version",
    "tags": "Tags",
}


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
