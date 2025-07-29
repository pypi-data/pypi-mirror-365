import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping, Optional, Protocol, Tuple

from uvy.data_printer.types import DataT, HeadersT

logger = logging.getLogger(__name__)


class ITabularDataPrinter(Protocol):
    def output(self, data: DataT, headers: Optional[HeadersT] = None) -> str:
        """Print data into a tabular format.

        Order of columns can be controlled by the headers dictionary. Each entry of the dictionary should be a mapping
        of the column name to the header name.

        """


class AbstractTabularDataPrinter(ABC, ITabularDataPrinter):
    @property
    @abstractmethod
    def horizontal_line(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def vertical_line(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def space(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def first_row_separators(self) -> Optional[Tuple[str, str, str]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def middle_row_separators(self) -> Tuple[str, str, str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def last_row_separators(self) -> Optional[Tuple[str, str, str]]:
        raise NotImplementedError

    def output(self, data: DataT, headers: Optional[HeadersT] = None) -> str:
        if not data and headers is None:
            return "Nothing to display."

        return self._print(data, headers)

    def _print(self, data: DataT, mappings: Optional[HeadersT] = None) -> str:
        headers = self._get_headers(data, mappings)
        column_widths = self._get_column_widths(data, headers)

        lines: list[str] = []

        lines.append(self._print_first_row_separator(column_widths))
        lines.append(self._print_row(headers, column_widths))
        lines.append(self._print_row_separator(column_widths))

        lines.extend([self._print_row(row, column_widths) for row in data])

        lines.append(self._print_last_row_separator(column_widths))

        return "\n".join(lines)

    def _print_first_row_separator(self, column_widths: Dict[str, int]) -> str:
        if self.first_row_separators is None:
            return ""

        chars = self.first_row_separators
        columns = [self.horizontal_line * width for width in column_widths.values()]

        return chars[0] + chars[1].join(columns) + chars[2]

    def _print_last_row_separator(self, column_widths: Dict[str, int]) -> str:
        if self.last_row_separators is None:
            return ""

        chars = self.last_row_separators
        columns = [self.horizontal_line * width for width in column_widths.values()]

        return chars[0] + chars[1].join(columns) + chars[2]

    def _print_row_separator(self, column_widths: Dict[str, int]) -> str:
        columns = [self.horizontal_line * width for width in column_widths.values()]

        chars = self.middle_row_separators
        return chars[0] + chars[1].join(columns) + chars[2]

    def _print_row(self, row: Mapping[str, Any], column_widths: Dict[str, int]) -> str:
        columns = [f"{str(row.get(header, '')).ljust(width)}" for header, width in column_widths.items()]

        return (
            self.vertical_line
            + self.space
            + (self.space + self.vertical_line + self.space).join(columns)
            + self.space
            + self.vertical_line
        )

    def _get_headers(self, data: DataT, mappings: Optional[HeadersT] = None) -> Mapping[str, str]:
        """
        Calculate the headers for the table based on the mappings or the keys of the first object in the list.
        """

        headers = mappings
        if headers is None:
            keys = data[0].keys()
            headers = {key: key for key in keys}

        return headers

    def _get_column_widths(self, data: DataT, headers: HeadersT) -> Dict[str, int]:
        """
        Calculate the maximum width of each column based on the header and data values.
        """

        column_widths = {key: len(value) for key, value in headers.items()}

        for row in data:
            for header, _ in headers.items():
                value_length = len(str(row.get(header, "")))
                column_widths[header] = max(column_widths[header], value_length)

        return column_widths
