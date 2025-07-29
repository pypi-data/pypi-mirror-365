from typing import Optional, Tuple

from uvy.data_printer.base_printer import AbstractTabularDataPrinter


class UnicodePrinter(AbstractTabularDataPrinter):
    """
    Prints a list of dictionaries as a Unicode table.
    """

    @property
    def horizontal_line(self) -> str:
        return "─"

    @property
    def vertical_line(self) -> str:
        return "│"

    @property
    def space(self) -> str:
        return " "

    @property
    def first_row_separators(self) -> Optional[Tuple[str, str, str]]:
        return ("┌─", "─┬─", "─┐")

    @property
    def middle_row_separators(self) -> Tuple[str, str, str]:
        return ("├─", "─┼─", "─┤")

    @property
    def last_row_separators(self) -> Optional[Tuple[str, str, str]]:
        return ("└─", "─┴─", "─┘")
