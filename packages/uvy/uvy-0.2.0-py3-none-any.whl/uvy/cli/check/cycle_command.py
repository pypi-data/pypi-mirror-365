from uvy.config.reader import read_uv_config
from uvy.packages.packages_facade import PackagesFacade


def check_cycle_command() -> None:
    """Check the uv monorepo for issues."""

    uv_conf = read_uv_config("pyproject.toml")
    facade = PackagesFacade()
    facade.load_packages(uv_conf.workspace.members, uv_conf.workspace.exclude)

    if facade.find_cycles():
        print("Cycles detected in the package dependencies:")
        for index, cycle in enumerate(facade.find_cycles(), start=1):
            cycle_string = " → ".join(package.name for package in cycle)
            print(f"    {index}. {cycle_string}")
        exit(1)
    else:
        print("No cycles detected in the package dependencies.")
        exit(0)

    pass
