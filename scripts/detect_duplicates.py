#!/usr/bin/env python3
"""Layered duplicate detection for learning records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from learning_lib import find_duplicate, iter_learning_records, load_record, validate_record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    record = load_record(args.record)
    errors = validate_record(record)
    if errors:
        print(json.dumps({"errors": errors}, indent=2))
        return 2
    result = find_duplicate(record, iter_learning_records(args.root, args.record))
    print(json.dumps(result.as_dict(), indent=2))
    return 1 if result.decision in {"duplicate", "review"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
