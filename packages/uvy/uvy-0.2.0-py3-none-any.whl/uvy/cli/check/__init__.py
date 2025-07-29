from uvy.cli.types import SubParsersType


def register_check_command(subparsers: SubParsersType) -> None:
    """Register the check command in the subparsers."""
    from uvy.cli.check.cycle_command import check_cycle_command

    parser = subparsers.add_parser(
        "check",
        help="Check the uv monorepo for issues.",
        allow_abbrev=False,
        description="Check the uv monorepo for issues.",
    )

    check_subparsers = parser.add_subparsers()
    cycles_parser = check_subparsers.add_parser(
        "cycles",
        help="Check for cycles in the package dependencies.",
        allow_abbrev=False,
        description="Check for cycles in the package dependencies.",
    )

    cycles_parser.set_defaults(func=check_cycle_command)
