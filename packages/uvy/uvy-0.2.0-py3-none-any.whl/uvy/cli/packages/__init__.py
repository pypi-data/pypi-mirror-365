from uvy.cli.types import SubParsersType
from uvy.cli.utils import CSVArgumentActionAction, EnumAction
from uvy.data_printer.factory import OutputFormat


def register_packages_command(subparsers: SubParsersType) -> None:
    """Register the list command in the subparsers."""
    from uvy.cli.packages.command import packages_command

    parser = subparsers.add_parser(
        "list",
        help="List and filter packages in the uv monorepo.",
        allow_abbrev=False,
        description="List and filter packages in the current uv monorepo.",
    )
    parser.add_argument(
        "-c",
        "--columns",
        action=CSVArgumentActionAction,
        type=str,
        help="Comma-separated list of columns. Can be specified multiple times. Defaults to 'name,path,version,tags'.",
        default=["name", "path", "version", "tags"],
    )
    parser.add_argument(
        "-f",
        "--format",
        type=OutputFormat,
        action=EnumAction,
        help="Output format. Must be one of: ascii, json, markdown, text, unicode. Defaults to unicode.",
        default=OutputFormat.unicode,
    )
    parser.add_argument(
        "-t",
        "--tags",
        action=CSVArgumentActionAction,
        help="Filter packages by tags. You can use regex patterns to match tags."
             "Tags can be specified multiple times or provided as a comma-separated list.",
    )
    parser.add_argument(
        "--with-dependents",
        action="store_true",
        help="Include packages that the listed packages depend on.",
    )

    parser.add_argument(
        "--with-dependees",
        action="store_true",
        help="Include packages that depend on the listed packages.",
    )

    parser.set_defaults(func=packages_command)
