from enum import Enum, unique
from typing import Final, Mapping, Type

from uvy.data_printer.ascii_printer import AsciiPrinter
from uvy.data_printer.base_printer import ITabularDataPrinter
from uvy.data_printer.json_printer import JsonPrinter
from uvy.data_printer.markdown_printer import MarkdownPrinter
from uvy.data_printer.text_printer import TextPrinter
from uvy.data_printer.unicode_printer import UnicodePrinter


@unique
class OutputFormat(Enum):
    """
    Output formats for the data table.
    """

    ascii = "ascii"
    json = "json"
    markdown = "markdown"
    text = "text"
    unicode = "unicode"


class TabularDataPrinterFactory:
    DATA_PRINTER_MAPPINGS: Final[Mapping[OutputFormat, Type[ITabularDataPrinter]]] = {
        OutputFormat.ascii: AsciiPrinter,
        OutputFormat.json: JsonPrinter,
        OutputFormat.markdown: MarkdownPrinter,
        OutputFormat.text: TextPrinter,
        OutputFormat.unicode: UnicodePrinter,
    }

    @staticmethod
    def create(output_format: OutputFormat) -> ITabularDataPrinter:
        printer = TabularDataPrinterFactory.DATA_PRINTER_MAPPINGS.get(output_format)

        if printer is None:
            raise ValueError(f"Unknown output format: {output_format}")

        return printer()
