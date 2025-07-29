from argparse import ArgumentParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import _SubParsersAction  # type: ignore

    SubParsersType = _SubParsersAction[ArgumentParser]
else:
    SubParsersType = object  # type: ignore
