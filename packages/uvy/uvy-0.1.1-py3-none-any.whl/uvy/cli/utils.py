import argparse

from enum import Enum
from typing import Any, List, Optional


class EnumAction(argparse.Action):
    """
    Argparse action for handling Enums
    """

    def __init__(self, **kwargs: Any) -> None:
        # Pop off the type value
        enum_type = kwargs.pop("type", None)

        # Ensure an Enum subclass is provided
        if enum_type is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum_type, Enum):
            raise TypeError("type must be an Enum when using EnumAction")

        # Generate choices from the Enum
        kwargs.setdefault("choices", tuple(e.value for e in enum_type))

        super(EnumAction, self).__init__(**kwargs)

        self._enum = enum_type

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: Optional[str] = None,
    ) -> None:
        # Convert value back into an Enum
        value = self._enum(values)
        setattr(namespace, self.dest, value)


class CSVArgumentActionAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: Optional[str] = None,
    ) -> None:
        current: List[str] = getattr(namespace, self.dest, [])
        if current == self.default:
            current = []

        normalized_values = self.normalize_values(values)
        parsed_values = self.parse_dsv_list(normalized_values)

        # Combine current and parsed_values, preserving order and uniqueness
        combined = current + [v for v in parsed_values if v not in current]
        setattr(namespace, self.dest, combined)

    def normalize_values(self, values: Any) -> List[str]:
        if isinstance(values, str):
            return [values]

        return []

    def parse_dsv_list(self, values: List[str], delimiter: str = ",") -> List[str]:
        return [item for value in values for item in self.parse_dsv(value, delimiter)]

    def parse_dsv(self, value: str, delimiter: str = ",") -> List[str]:
        return [v.strip() for v in value.split(delimiter) if v.strip()]
