from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

# import pickle


def _main():
    args = _parse_cmd_arguments()

    # read input file into dictionary
    # only take the first two entries per row
    with args.infile.open() as f:
        out = {row[0]: row[1] for row in csv.reader(f, delimiter=";")}

    with args.outfile.open("w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # with open(args.outfile, "wb") as f:
    #     pickle.dump(out, f)


def _parse_cmd_arguments():
    parser = argparse.ArgumentParser(description="Update journals.json.")
    parser.add_argument("infile", type=Path)
    parser.add_argument("outfile", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    _main()
