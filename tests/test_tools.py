from __future__ import annotations

import pybtex
import pybtex.database

import bibfmt


def test_merge() -> None:
    entry1 = pybtex.database.Entry(
        "article",
        fields={"title": "Yes", "year": 2000},
        persons={"author": [pybtex.database.Person("Doe, John")]},
    )
    entry2 = pybtex.database.Entry(
        "book",
        fields={"title": "No", "pages": "1-19"},
        persons={"author": [pybtex.database.Person("Doe, John")]},
    )
    reference = pybtex.database.Entry(
        "book",
        fields={"title": "No", "year": 2000, "pages": "1-19"},
        persons={"author": [pybtex.database.Person("Doe, John")]},
    )

    merged = bibfmt.merge(entry1, entry2)

    assert bibfmt.pybtex_to_bibtex_string(
        merged, "key", sort=True
    ) == bibfmt.pybtex_to_bibtex_string(reference, "key", sort=True)


def test_month_range() -> None:
    assert bibfmt.translate_month("June-July") == 'jun # "-" # jul'


def test_decode() -> None:
    url = "https://www.wolframalpha.com/input/?i=integrate+from+0+to+2pi+(cos(x)+e%5E(i+*+(m+-+n)+*+x))"
    entry = pybtex.database.Entry(
        "misc",
        fields=[("url", url), ("note", "Online; accessed 19-February-2019")],
    )
    out = bibfmt.decode(entry)
    assert out.fields["url"] == url


def test_decode_doi() -> None:
    doi = "10.1007/978-1-4615-7419-4_6"
    d = pybtex.database.Entry(
        "misc",
        fields=[("doi", doi), ("note", "Online; accessed 19-February-2019")],
    )
    out = bibfmt.decode(d)
    assert out.fields["doi"] == doi
