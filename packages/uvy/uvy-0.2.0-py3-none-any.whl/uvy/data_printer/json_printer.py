import json
from typing import Optional

from uvy.data_printer.base_printer import ITabularDataPrinter
from uvy.data_printer.types import DataT, HeadersT


class JsonPrinter(ITabularDataPrinter):
    """
    Prints a list of dictionaries as a JSON string.
    """

    def output(self, data: DataT, headers: Optional[HeadersT] = None) -> str:
        if not data and headers is None:
            return "Nothing to display."

        filtered_data = data
        if headers is not None:
            filtered_data = [{h: row.get(h) for h in headers if h in row} for row in data]
        return json.dumps(filtered_data, indent=2, ensure_ascii=False)
