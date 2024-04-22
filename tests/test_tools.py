from __future__ import annotations

from pathlib import Path

import pybtex
import pybtex.database
import pytest

import bibfmt

this_dir = Path(__file__).resolve().parent
data_file_exists = Path(this_dir / "../src/bibfmt/data/journals.json").is_file()


def test_merge():
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


@pytest.mark.skipif(not data_file_exists, reason="Data file missing")
def test_journal_name():
    shrt = pybtex.database.Entry(
        "article", fields={"journal": "SIAM J. Matrix Anal. Appl."}
    )
    lng = pybtex.database.Entry(
        "article",
        fields={"journal": "SIAM Journal on Matrix Analysis and Applications"},
    )

    tmp = {"key": lng}
    bibfmt.journal_abbrev(tmp)
    assert tmp["key"].fields["journal"] == shrt.fields["journal"]

    lng = pybtex.database.Entry(
        "article",
        fields={"journal": "SIAM Journal on Matrix Analysis and Applications"},
    )
    tmp = {"key": shrt}
    bibfmt.journal_abbrev(tmp, long_journal_names=True)
    assert tmp["key"].fields["journal"] == lng.fields["journal"]


def test_month_range():
    assert bibfmt.translate_month("June-July") == 'jun # "-" # jul'


def test_decode():
    url = "https://www.wolframalpha.com/input/?i=integrate+from+0+to+2pi+(cos(x)+e%5E(i+*+(m+-+n)+*+x))"
    entry = pybtex.database.Entry(
        "misc",
        fields=[("url", url), ("note", "Online; accessed 19-February-2019")],
    )
    out = bibfmt.decode(entry)
    assert out.fields["url"] == url


def test_decode_doi():
    doi = "10.1007/978-1-4615-7419-4_6"
    d = pybtex.database.Entry(
        "misc",
        fields=[("doi", doi), ("note", "Online; accessed 19-February-2019")],
    )
    out = bibfmt.decode(d)
    assert out.fields["doi"] == doi
