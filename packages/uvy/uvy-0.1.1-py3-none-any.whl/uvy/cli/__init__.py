import argparse

from uvy.cli.packages import register_packages_command


def uvy() -> int:
    parser = argparse.ArgumentParser(
        prog="uvy", description="A toolkit for the uv tool", allow_abbrev=False
    )
    subparsers = parser.add_subparsers()

    register_packages_command(subparsers)

    kwargs = vars(parser.parse_args())
    try:
        command = kwargs.pop("func")
    except KeyError:
        parser.print_help()
    else:
        command(**kwargs)
    return 0
