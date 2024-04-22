from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

import bibfmt


TEST_BIBTEXT_PREAMBLE_UNFORMATTED = """\
@preamble{"\\RequirePackage{biblatex}"}
@preamble{"\\addbibressource{dependend.bib}"}
@article{foobar,
doi={foobar},
url = {https://doi.org/foobar}
}\
"""

TEST_BIBTEXT_PREAMBLE_FORMATTED_DROP = """\
@article{foobar,
  doi = {foobar},
  url = {https://doi.org/foobar},
}
"""

TEST_BIBTEXT_PREAMBLE_FORMATTED_KEEP = f"""\
@preamble{{"\\RequirePackage{{biblatex}}"}}

@preamble{{"\\addbibressource{{dependend.bib}}"}}

{TEST_BIBTEXT_PREAMBLE_FORMATTED_DROP}\
"""


@pytest.mark.parametrize(
    ("ref_in", "ref_out", "args"),
    [
        pytest.param(
            TEST_BIBTEXT_PREAMBLE_UNFORMATTED,
            TEST_BIBTEXT_PREAMBLE_FORMATTED_KEEP,
            [],
            id="unfmt",
        ),
        pytest.param(
            TEST_BIBTEXT_PREAMBLE_FORMATTED_KEEP,
            TEST_BIBTEXT_PREAMBLE_FORMATTED_KEEP,
            [],
            id="fmt_preamble",
        ),
        pytest.param(
            TEST_BIBTEXT_PREAMBLE_FORMATTED_DROP,
            TEST_BIBTEXT_PREAMBLE_FORMATTED_DROP,
            [],
            id="fmt_no_preamble",
        ),
        pytest.param(
            TEST_BIBTEXT_PREAMBLE_FORMATTED_DROP,
            TEST_BIBTEXT_PREAMBLE_FORMATTED_DROP.replace("  ", "\t"),
            ["--indent=tab"],
            id="fmt_tab",
        ),
    ],
)
def test_cli_format(
    ref_in: str, ref_out: str, args: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        infile = Path(tmpdir) / "test.bib"

        with infile.open("w") as f:
            f.write(ref_in)

        bibfmt.cli.main([*args, str(infile)])
        captured = capsys.readouterr()
        assert captured.out == ref_out

        bibfmt.cli.main(["--in-place", *args, str(infile)])
        with infile.open() as f:
            assert f.read() == ref_out
