from __future__ import annotations

import argparse

from . import _format


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Format BibTeX files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version", "-v", action="version", help="display version information"
    )

    _format.add_args(parser)

    args = parser.parse_args(argv)

    return _format.run(args)
