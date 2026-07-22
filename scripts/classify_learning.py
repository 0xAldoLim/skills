#!/usr/bin/env python3
"""Classify a learning candidate as accepted, inbox, or rejected."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from learning_lib import classify_record, find_duplicate, iter_learning_records, load_record, validate_record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    record = load_record(args.record)
    errors = validate_record(record)
    if errors:
        print(json.dumps({"decision": "invalid", "reasons": errors}, indent=2))
        return 2
    duplicate = find_duplicate(record, iter_learning_records(args.root, args.record))
    decision, reasons = classify_record(record, duplicate)
    print(json.dumps({"decision": decision, "reasons": reasons, "duplicate": duplicate.as_dict()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
