"""BibTeX formatter for Python."""

from __future__ import annotations

from . import cli
from .adapt_doi_urls import adapt_doi_urls
from .tools import (
    decode,
    dict_to_string,
    merge,
    pybtex_to_bibtex_string,
    pybtex_to_dict,
    translate_month,
)


__all__ = [
    "cli",
    "decode",
    "pybtex_to_dict",
    "pybtex_to_bibtex_string",
    "dict_to_string",
    "merge",
    "translate_month",
    "adapt_doi_urls",
]
