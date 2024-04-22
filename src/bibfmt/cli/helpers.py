"""Helper functions for the CLI."""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import IO, Literal


class FileParserArgs(argparse.Namespace):
    """File handling arguments."""

    infiles: Sequence[IO[str]]
    in_place: bool


def add_file_parser_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the file handling arguments to an argparse parser.

    Parameters
    ----------
    parser
        ArgumentParser

    """
    parser.add_argument(
        "infiles",
        nargs="+",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="input BibTeX files (default: stdin)",
    )
    parser.add_argument(
        "-i", "--in-place", action="store_true", help="modify infile in place"
    )


class FormattingParserArgs(argparse.Namespace):
    """Bibtex formatting arguments."""

    sort_by_bibkey: bool
    tab_indent: bool
    delimiter_type: Literal["braces", "quotes"]
    doi_url_type: Literal["unchanged", "new", "short"]
    page_range_separator: str


def add_formatting_parser_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the bibtex formatting arguments to an argparse parser.

    Parameters
    ----------
    parser
        ArgumentParser

    """
    formatting_group = parser.add_argument_group("Formatting")
    formatting_group.add_argument(
        "-b",
        "--sort-by-bibkey",
        action="store_true",
        help="sort entries by BibTeX key (default: false)",
    )
    formatting_group.add_argument(
        "-t",
        "--tab-indent",
        action="store_true",
        help="use tabs for indentation (default: false)",
    )
    formatting_group.add_argument(
        "-d",
        "--delimiter-type",
        choices=["braces", "quotes"],
        default="braces",
        help=("which delimiters to use in the output file " "(default: braces {...})"),
    )
    formatting_group.add_argument(
        "--doi-url-type",
        choices=["unchanged", "new", "short"],
        default="new",
        help=(
            "DOI URL (new: https://doi.org/<DOI> (default), "
            "short: https://doi.org/abcde)"
        ),
    )
    formatting_group.add_argument(
        "-p",
        "--page-range-separator",
        type=str,
        default="--",
        help="page range separator (default: --)",
    )
