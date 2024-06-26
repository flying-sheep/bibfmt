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

    from pybtex.database import Entry


class FormatArgs(FileParserArgs, FormattingParserArgs):
    drop: list[str]


def run(args: FormatArgs) -> None:
    for infile in args.infiles:
        data = bibtex_parser(infile)

        if args.drop:
            data = filter_fields(data, args.drop)

        d: dict[str, Entry] = dict(data.entries)
        if False:  # TODO(flying-sheep): Add option  # noqa: TD003
            preserve_title_capitalization(d)
        adapt_doi_urls(d, args.doi_url_type)
        set_page_range_separator(d, args.page_range_separator)

        if args.sort_by_bibkey:
            d = dict(sorted(d.items()))

        string = dict_to_string(
            d,
            args.delimiter_type,
            indent=args.indent,
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
