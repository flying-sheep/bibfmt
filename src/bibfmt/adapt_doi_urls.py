"""Adapt DOI URLs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import tools


if TYPE_CHECKING:
    from typing import Callable, Literal

    from pybtex.database import Entry


def adapt_doi_urls(
    d: dict[str, Entry], doi_url_type: Literal["new", "short", "unchanged"]
) -> None:
    """Adapt DOI URLs."""
    if doi_url_type == "new":
        _update_doi_url(d, lambda doi: f"https://doi.org/{doi}")

    elif doi_url_type == "short":

        def update_to_short_doi(doi: str) -> str | None:
            short_doi = tools.get_short_doi(doi)
            if short_doi:
                return f"https://doi.org/{short_doi}"
            return None

        _update_doi_url(d, update_to_short_doi)

    elif doi_url_type != "unchanged":
        msg = f"Unknown doi_url_type {doi_url_type}"
        raise AssertionError(msg)


def _update_doi_url(
    d: dict[str, Entry], url_from_doi: Callable[[str], str | None]
) -> None:
    for bib_id, value in d.items():
        assert value.fields is not None  # noqa: S101
        if "url" not in value.fields:
            continue

        doi = tools.doi_from_url(value.fields["url"])
        if doi:
            new_url = url_from_doi(doi)
            if new_url:
                d[bib_id].fields["url"] = new_url
