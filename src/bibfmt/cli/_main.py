from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from . import _format


if TYPE_CHECKING:
    from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Format BibTeX files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version", "-v", action="version", help="display version information"
    )

    _format.add_args(parser)

    args = parser.parse_args(argv)

    return _format.run(args)
