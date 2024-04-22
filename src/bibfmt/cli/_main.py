from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from ..adapt_doi_urls import adapt_doi_urls
from ..tools import (
    bibtex_parser,
    dict_to_string,
    filter_fields,
    preserve_title_capitalization,  # noqa: TCH001
    set_page_range_separator,
    write,
)
from .helpers import (
    FileParserArgs,
    FormattingParserArgs,
    add_file_parser_arguments,
    add_formatting_parser_arguments,
)


if TYPE_CHECKING:
    from collections.abc import Sequence


class FormatArgs(FileParserArgs, FormattingParserArgs):
    drop: list[str]


def run(args: FormatArgs) -> None:
    for infile in args.infiles:
        data = bibtex_parser(infile)

        if args.drop:
            data = filter_fields(data, args.drop)

        # Use an ordered dictionary to make sure that the entries are written out
        # sorted by their BibTeX key if demanded.
        tuples = data.entries.items()
        if args.sort_by_bibkey:
            tuples = sorted(data.entries.items())

        d = dict(tuples)
        if False:  # TODO(flying-sheep): Add parameter  # noqa: TD003
            preserve_title_capitalization(d)
        adapt_doi_urls(d, args.doi_url_type)
        set_page_range_separator(d, "--")

        string = dict_to_string(
            d,
            args.delimiter_type,
            tab_indent=args.tab_indent,
            # TODO(nschloe): use public field when it becomes possible  # noqa: TD003
            preamble=data._preamble,  # noqa: SLF001
        )

        write(string, infile if args.in_place else None)


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Format BibTeX files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version", "-V", action="version", help="display version information"
    )

    add_file_parser_arguments(parser)
    add_formatting_parser_arguments(parser)

    help_ = "drops field from bibtex entry if they exist, can be passed multiple times"
    parser.add_argument("--drop", action="append", help=help_)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = parser().parse_args(argv, namespace=FormatArgs())

    return run(args)
