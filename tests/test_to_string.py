from __future__ import annotations

import pytest
from pybtex.database import Entry, Person

import bibfmt


@pytest.mark.parametrize(
    ("ref_entry", "ref_str"),
    [
        pytest.param(
            Entry(
                "article",
                fields={
                    "doi": "foobar",
                    "url": "https://doi.org/foobar",
                },
            ),
            [
                "@article{foobar,",
                " doi = {foobar},",
                " url = {https://doi.org/foobar},",
                "}",
            ],
            id="basic",
        ),
        pytest.param(
            Entry("article", fields={"title": "Foo \\& Bar"}),
            ["@article{foobar,", " title = {Foo \\& Bar},", "}"],
            id="escape_ampersand",
        ),
        pytest.param(
            Entry("article", fields={"title": "Foo on \\LaTeX"}),
            ["@article{foobar,", " title = {Foo on \\LaTeX},", "}"],
            id="escape_command",
        ),
        pytest.param(
            Entry("article", fields={"title": "Foo \\ Bridge"}),
            ["@article{foobar,", " title = {Foo \\ Bridge},", "}"],
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
            [
                "@misc{foobar,",
                " url = {https://www.wolframalpha.com/input/?i=integrate+from+0+to+2pi+(cos(x)+e%5E(i+*+(m+-+n)+*+x))},",
                " note = {Online; accessed 19-February-2019},",
                "}",
            ],
            id="encode_url",
        ),
        pytest.param(
            Entry(
                "misc",
                fields={"doi": "10.1007/978-1-4615-7419-4_6"},
            ),
            [
                "@misc{foobar,",
                " doi = {10.1007/978-1-4615-7419-4_6},",
                "}",
            ],
            id="full_doi",
        ),
        pytest.param(
            Entry(
                "misc",
                persons={"author": [Person("Doe, J. J.")]},
            ),
            [
                "@misc{foobar,",
                " author = {Doe, J. J.},",
                "}",
            ],
            id="author",
        ),
    ],
)
def test_cli_format(ref_entry: Entry, ref_str: list[str]) -> None:
    assert bibfmt.pybtex_to_bibtex_string(ref_entry, "foobar") == "\n".join(ref_str)
