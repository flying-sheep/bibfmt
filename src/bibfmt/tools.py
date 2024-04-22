"""Assorted functions."""

from __future__ import annotations

import contextlib
import logging
import re
import sys
from collections.abc import Iterable
from copy import deepcopy
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, cast
from warnings import warn

import requests
from pybtex.database import Person
from pybtex.database.input import bibtex
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexencode import unicode_to_latex


if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping, Sequence
    from collections.abc import Set as AbstractSet
    from typing import IO, Literal

    from pybtex.database import BibliographyData, Entry


@cache
def get_dict() -> AbstractSet[str]:
    """Get set of words from the web2 dictionary."""
    from english_words import get_english_words_set

    return get_english_words_set(["web2"])


def decode(entry: Entry) -> Entry:
    """Decode a dictionary with LaTeX strings into a dictionary with unicode strings."""
    translator = LatexNodes2Text()
    # Perform a deepcopy, otherwise the input entry will get altered
    out = deepcopy(entry)
    assert out.fields is not None  # noqa: S101
    for key, value in out.fields.items():
        if key == "url":
            # The url can contain special LaTeX characters (like %) and that's fine
            continue
        out.fields[key] = translator.latex_to_text(value)
    return out


def pybtex_to_dict(entry: Entry) -> dict[str, str]:
    """Represent BibTeX entry as dict."""
    d = {}
    d["genre"] = entry.type
    transform = unicode_to_latex
    assert entry.persons is not None  # noqa: S101
    assert entry.fields is not None  # noqa: S101
    for key, persons in cast(dict[str, Iterable[Person]], entry.persons).items():
        d[key.lower()] = [
            {
                "first": [transform(string) for string in p.first_names or ()],
                "middle": [transform(string) for string in p.middle_names or ()],
                "prelast": [transform(string) for string in p.prelast_names or ()],
                "last": [transform(string) for string in p.last_names or ()],
                "lineage": [transform(string) for string in p.lineage_names or ()],
            }
            for p in persons
        ]
    for field, value in entry.fields.items():
        d[field.lower()] = value
    return d


def translate_month(key: str) -> str | None:
    """Unify month formats.

    The month value can take weird forms. Sometimes, it's given as an int, sometimes
    as a string representing an int, and sometimes the name of the month is spelled out.
    Try to handle most of this here.
    """
    months = [
        *("jan", "feb", "mar", "apr", "may", "jun"),
        *("jul", "aug", "sep", "oct", "nov", "dec"),
    ]

    # Sometimes, the key is just a month
    try:
        return months[int(key) - 1]
    except (TypeError, ValueError):
        # TypeError: unsupported operand type(s) for -: 'str' and 'int'
        pass

    # Split for entries like "March-April"
    strings = []
    for k in key.split("-"):
        month = k[:3].lower()

        # Month values like '????' appear -- skip them
        if month in months:
            strings.append(month)
        else:
            logging.warning(f"Unknown month value {key!r}. Skipping.")
            return None

    return ' # "-" # '.join(strings)


def _translate_word(word: str) -> str:
    """Check if the word needs to be protected by `{}` to prevent recapitalization."""
    if (
        not word
        or word.count("{") != word.count("}")
        or (word[0] == "{" and word[-1] == "}")
        or word[0] == "\\"
    ):
        needs_protection = False
    elif any(char.isupper() for char in word[1:]):
        needs_protection = True
    else:
        english = get_dict()

        # with a better spell checker, we could do “and word in english”
        needs_protection = (
            any(char.isupper() for char in word) and word.lower() not in english
        )

    if needs_protection:
        return f"{{{word}}}"
    return word


def _translate_title(val: str) -> str:
    """{}-protect parts whose capitalization should not change.

    The capitalization of BibTeX entries is handled by the style, so names (Newton)
    or abbreviations (GMRES) may not be capitalized. This is unless they are wrapped in
    curly braces.
    """
    # If the title is completely capitalized, it's probably by mistake.
    if val == val.upper():
        val = val.title()

    words = val.split()
    # Handle colons as in
    # ```
    # Algorithm 694: {A} collection...
    # ```
    for k in range(len(words)):
        if k > 0 and words[k - 1][-1] == ":" and words[k][0] != "{":
            words[k] = f"{{{words[k].capitalize()}}}"

    words = ["-".join(_translate_word(w) for w in word.split("-")) for word in words]

    return " ".join(words)


def preserve_title_capitalization(d: dict[str, Entry]) -> None:
    """Preserve title capitalization."""
    for entry in d.values():
        assert entry.fields is not None  # noqa: S101
        try:
            title = entry.fields["title"]
            entry.fields["title"] = _translate_title(title)
        except KeyError:
            warn(f"'entry' {entry} has no title", stacklevel=1)


def set_page_range_separator(d: MutableMapping[str, Entry], string: str) -> None:
    """Replace any number of dashes (hyphen, en, em, etc.) by page_range_separator.

    See Also
    --------
    - <https://tex.stackexchange.com/a/58671/13262>
    - <https://jkorpela.fi/dashes.html>

    """
    chars = (
        "-"
        "\N{HYPHEN}"
        "\N{NON-BREAKING HYPHEN}"
        "\N{FIGURE DASH}"
        "\N{EN DASH}"
        "\N{EM DASH}"
        "\N{HORIZONTAL BAR}"
    )
    for entry in d.values():
        assert entry.fields is not None  # noqa: S101
        if "pages" not in entry.fields:
            continue
        entry.fields["pages"] = re.sub(f"[{chars}]+", string, entry.fields["pages"])


def remove_multiple_spaces(d: dict[str, Entry]) -> None:
    """Collapse sequences of spaces."""
    for entry in d.values():
        assert entry.fields is not None  # noqa: S101
        for key, value in entry.fields.items():
            if key in ["url", "doi"]:
                continue
            try:
                new_value = re.sub(" +", " ", value)
                # Remove trailing spaces
                new_value = new_value.rstrip()
            except TypeError:
                # expected unicode for encode input, but got int instead
                pass
            else:
                entry.fields[key] = new_value


def pybtex_to_bibtex_string(
    entry: Entry,
    bibtex_key: str,
    *,
    delimiters: tuple[str, str] = ("{", "}"),
    indent: str = "  ",
    align: int = 14,
    sort: bool = False,
) -> str:
    """Represent BibTeX entry as str."""
    out = f"@{entry.type}{{{bibtex_key},\n{indent}"
    content = []

    left, right = delimiters

    assert entry.persons is not None  # noqa: S101
    for key, persons in entry.persons.items():
        persons_str = " and ".join([_get_person_str(p) for p in persons])
        content.append(f"{key.lower()} = {left}{persons_str}{right}")

    assert entry.fields is not None  # noqa: S101
    keys = entry.fields.keys()
    if sort:
        keys = sorted(keys)

    n_col = min(align, max((len(k) for k in keys), default=0))
    key_fmt = f"{{:<{n_col}}}"

    for key in keys:
        value: str = entry.fields[key]

        # Always make keys lowercase
        key = key.lower()  # noqa: PLW2901

        if key == "month":
            month_string = translate_month(value)
            if month_string:
                content.append(f"{key} = {month_string}")
            continue

        with contextlib.suppress(AttributeError):
            value = value.replace("\N{REPLACEMENT CHARACTER}", "?")

        if value is not None:
            content.append(f"{key_fmt.format(key)} = {left}{value}{right}")

    # Make sure that every line ends with a comma
    out += indent.join([line + ",\n" for line in content])
    out += "}"
    return out


def doi_from_url(url: str) -> str | None:
    """See if this is a DOI URL and return the DOI."""
    m = re.match("https?://(?:dx\\.)?doi\\.org/(.*)", url)
    if m:
        return m.group(1)
    return None


def get_short_doi(doi: str) -> str | None:
    """Possibly shorten doi."""
    url = f"http://shortdoi.org/{doi}"
    r = requests.get(url, params={"format": "json"}, timeout=5)
    if not r.ok:
        return None

    data = r.json()
    if "ShortDOI" not in data:
        return None

    return data["ShortDOI"]


def _get_person_str(p: Person) -> str:
    name_parts = [
        " ".join((*(p.prelast_names or ()), *(p.last_names or ()))),
        " ".join(p.lineage_names or ()),
        # In plain English, you wouldn't put a full space between abbreviated
        # initials, see, e.g.,
        # <https://english.stackexchange.com/a/105529/23644>. In bib files,
        # though, it's useful, see
        # <https://github.com/nschloe/betterbib/issues/212> and
        # <https://clauswilke.com/blog/2015/10/02/bibtex/>.
        # See <https://tex.stackexchange.com/a/11083/13262> on how to configure
        # biber/biblatex to use thin spaces.
        " ".join((*(p.first_names or ()), *(p.middle_names or ()))),
    ]
    out = ", ".join(filter(None, name_parts))
    # If the name is completely capitalized, it's probably by mistake.
    if out == out.upper():
        out = out.title()
    return out


# This used to be a write() function, but beware of exceptions! Files would get
# unintentionally overridden, see <https://github.com/nschloe/betterbib/issues/184>
def dict_to_string(
    od: Mapping[str, Entry],
    delimiter_type: Literal["braces", "quotes"],
    *,
    indent: int | Literal["tab"] = 2,
    preamble: list | None = None,
) -> str:
    """Create a string representing the bib entries.

    Parameters
    ----------
    od
        dictionary of bibtex entries
    delimiter_type
        delimiter to use to mark strings
    indent
        how to indent the entries
    preamble
        list of preamble commands

    """
    # Write header to the output file.
    segments = []

    delimiters = {"braces": ("{", "}"), "quotes": ('"', '"')}[delimiter_type]

    if preamble:
        # Add segments for each preamble entry
        segments.extend(
            [f'@preamble{{"{preamble_string}"}}' for preamble_string in preamble]
        )

    # Add segments for each bibtex entry in order
    segments += [
        pybtex_to_bibtex_string(
            d,
            bib_id,
            delimiters=delimiters,
            indent="\t" if indent == "tab" else (" " * indent),
        )
        for bib_id, d in od.items()
    ]

    return "\n\n".join(segments) + "\n"


def merge(entry1: Entry, entry2: Entry | None) -> Entry:
    """Create a merged BibTeX entry with the data from entry2 taking precedence."""
    out = entry1
    if entry2 is not None:
        assert out.persons is not None  # noqa: S101
        assert out.fields is not None  # noqa: S101
        assert entry2.fields is not None  # noqa: S101

        if entry2.type:
            out.type = entry2.type

        if entry2.persons:
            for key, value in entry2.persons.items():
                if value:
                    out.persons[key] = value

        for key, value in entry2.fields.items():
            if value:
                out.fields[key] = value

    return out


def filter_fields(
    data: BibliographyData, excludes: Sequence[str] = ()
) -> BibliographyData:
    """Remove fields from bibtex entries."""
    entry: Entry
    for entry in data.entries.values():
        if entry.fields:
            entry.fields = {k: v for k, v in entry.fields.items() if k not in excludes}
    return data


def bibtex_parser(infile: IO[str]) -> BibliographyData:
    """Return the parsed bibtex data and adds context to the exception.

    Parameters
    ----------
    infile
        file to be parsed

    Returns
    -------
    bibtex entries

    """
    try:
        data = bibtex.Parser().parse_file(infile)

    except Exception as e:
        getattr(e, "add_note", print)(f"There was an error when parsing {infile.name}")
        raise
    else:
        return data


def write(string: str, outfile: IO[str] | None = None) -> None:
    """Write a string to a BibTeX file.

    Parameters
    ----------
    string
        string to write
    outfile
        file to write to (default: None)

    """
    if outfile:
        with Path(outfile.name).open("w") as f:
            f.write(string)
    else:
        sys.stdout.write(string)
