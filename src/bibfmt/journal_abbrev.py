from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybtex.database import Entry


def journal_abbrev(
    d: dict[str, Entry],
    long_journal_names: bool = False,
    custom_abbrev: str | None = None,
) -> None:
    this_dir = Path(__file__).resolve().parent
    with (this_dir / "data/journals.json").open() as f:
        table = json.load(f)

    if custom_abbrev is not None:
        with Path(custom_abbrev).open() as f:
            table.update(json.load(f))

    if long_journal_names:
        table = {v: k for k, v in table.items()}

    # fallback option
    table_keys_lower = {k.lower(): v for k, v in table.items()}

    for value in d.values():
        if "journal" not in value.fields:
            continue

        journal = value.fields["journal"]
        try:
            value.fields["journal"] = table[journal]
        except KeyError:
            try:
                value.fields["journal"] = table_keys_lower[journal.lower()]
            except KeyError:
                pass
