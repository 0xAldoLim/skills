#!/usr/bin/env python3
"""Append one approved learning record to a category without overwriting knowledge."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from learning_lib import (
    append_ledger,
    classify_record,
    find_duplicate,
    iter_learning_records,
    load_record,
    record_identifier,
    render_learning_markdown,
    validate_record,
)


def append_record(root: Path, source: Path, approved: bool = False) -> Path:
    record = load_record(source)
    errors = validate_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    duplicate = find_duplicate(record, iter_learning_records(root, source))
    if duplicate.decision == "duplicate":
        raise ValueError(f"equivalent technique exists: {', '.join(duplicate.matches)}")
    decision, reasons = classify_record(record, duplicate)
    if not approved and decision != "accepted":
        raise ValueError(f"record is {decision}: {', '.join(reasons) or duplicate.reason}")
    variant_of = duplicate.matches[0] if duplicate.decision == "variant" and duplicate.matches else None
    destination = root / record["category"] / "LEARNED.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        if destination.stat().st_size == 0:
            handle.write("# Append-only Learned Techniques\n\nGenerated entries are appended after verification. Existing entries are never replaced.\n")
        handle.write(render_learning_markdown(record, variant_of))
    append_ledger(root, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "appended",
        "identifier": record_identifier(record),
        "destination": destination.relative_to(root).as_posix(),
        "duplicate": duplicate.as_dict(),
    })
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--approved", action="store_true", help="human approved an inbox/variant record")
    args = parser.parse_args()
    try:
        destination = append_record(args.root.resolve(), args.record.resolve(), args.approved)
    except ValueError as exc:
        print(json.dumps({"status": "not-appended", "reason": str(exc)}, indent=2))
        return 1
    print(json.dumps({"status": "appended", "destination": str(destination)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
