from typing import Any, Dict, Mapping, Optional, Tuple

from uvy.data_printer.base_printer import AbstractTabularDataPrinter
from uvy.data_printer.types import DataT, HeadersT


class TextPrinter(AbstractTabularDataPrinter):
    """
    Prints a list of dictionaries as plain text, columns separated by spaces, no extra formatting.
    """

    @property
    def horizontal_line(self) -> str:
        return ""

    @property
    def vertical_line(self) -> str:
        return "\t"

    @property
    def space(self) -> str:
        return ""

    @property
    def first_row_separators(self) -> Optional[Tuple[str, str, str]]:
        return None

    @property
    def middle_row_separators(self) -> Tuple[str, str, str]:
        return ("", "", "")

    @property
    def last_row_separators(self) -> Optional[Tuple[str, str, str]]:
        return None

    def _print(self, data: DataT, mappings: Optional[HeadersT] = None) -> str:
        headers = self._get_headers(data, mappings)
        column_widths = self._get_column_widths(data, headers)

        lines: list[str] = []
        lines.extend([self._print_row(row, column_widths) for row in data])

        return "\n".join(lines)

    def _get_column_widths(self, data: DataT, headers: HeadersT) -> Dict[str, int]:
        """
        Calculate the maximum width of each column based on the header and data values.
        """

        column_widths: Dict[str, int] = {}

        for header, _ in headers.items():
            column_widths[header] = 0

        return column_widths

    def _print_row(self, row: Mapping[str, Any], column_widths: Dict[str, int]) -> str:
        columns = [f"{str(row.get(header, '')).ljust(width)}" for header, width in column_widths.items()]

        return (self.vertical_line).join(columns)
