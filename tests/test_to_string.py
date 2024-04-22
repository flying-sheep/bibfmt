from __future__ import annotations

import pytest
from pybtex.database import Entry, Person

import bibfmt


@pytest.mark.parametrize(
    ("ref_entry", "ref_str"),
    [
        pytest.param(
            Entry("article", fields={"doi": "foobar", "url": "https://doi.org/foobar"}),
            (
                "@article{foobar,\n"
                "  doi = {foobar},\n"
                "  url = {https://doi.org/foobar},\n"
                "}"
            ),
            id="basic",
        ),
        pytest.param(
            Entry("article", fields={"title": "Foo \\& Bar"}),
            "@article{foobar,\n  title = {Foo \\& Bar},\n}",
            id="escape_ampersand",
        ),
        pytest.param(
            Entry("article", fields={"title": "Foo on \\LaTeX"}),
            "@article{foobar,\n  title = {Foo on \\LaTeX},\n}",
            id="escape_command",
        ),
        pytest.param(
            Entry("article", fields={"title": "Foo \\ Bridge"}),
            "@article{foobar,\n  title = {Foo \\ Bridge},\n}",
            id="extra_space",
        ),
        pytest.param(
            Entry(
                "misc",
                fields={
                    "url": "https://www.wolframalpha.com/input/?i=integrate+from+0+to+2pi+(cos(x)+e%5E(i+*+(m+-+n)+*+x))",
                    "note": "Online; accessed 19-February-2019",
                },
            ),
            (
                "@misc{foobar,\n"
                "  url  = {https://www.wolframalpha.com/input/?i=integrate+from+0+to+2pi+(cos(x)+e%5E(i+*+(m+-+n)+*+x))},\n"
                "  note = {Online; accessed 19-February-2019},\n"
                "}"
            ),
            id="encode_url",
        ),
        pytest.param(
            Entry("misc", fields={"doi": "10.1007/978-1-4615-7419-4_6"}),
            "@misc{foobar,\n  doi = {10.1007/978-1-4615-7419-4_6},\n}",
            id="full_doi",
        ),
        pytest.param(
            Entry("misc", persons={"author": [Person("Doe, J. J.")]}),
            "@misc{foobar,\n  author = {Doe, J. J.},\n}",
            id="author",
        ),
        pytest.param(
            Entry("article", fields=dict(title="Test", publisher="Test Press")),
            (
                "@article{foobar,\n"
                "  title   = {Test},\n"
                "  publisher = {Test Press},\n"
                "}"
            ),
            id="exceeds_align",
        ),
    ],
)
def test_cli_format(ref_entry: Entry, ref_str: list[str]) -> None:
    assert bibfmt.pybtex_to_bibtex_string(ref_entry, "foobar", align=7) == ref_str
