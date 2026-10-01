#!/usr/bin/env python3
"""Capture a solve-derived learning record and conservatively route it."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from append_learning import append_record
from learning_lib import (
    append_ledger,
    classify_record,
    find_duplicate,
    iter_learning_records,
    load_record,
    record_identifier,
    slugify,
    validate_record,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--auto", action="store_true", help="append only when every acceptance gate passes")
    parser.add_argument("--dry-run", action="store_true", help="classify without writing records, references or ledgers")
    args = parser.parse_args()
    root, source = args.root.resolve(), args.record.resolve()
    record = load_record(source)
    errors = validate_record(record)
    if errors:
        print(json.dumps({"status": "invalid", "errors": errors}, indent=2))
        return 2
    duplicate = find_duplicate(record, iter_learning_records(root, source))
    decision, reasons = classify_record(record, duplicate)
    if not args.auto and decision == "accepted":
        decision, reasons = "inbox", ["automatic acceptance was not requested"]
    area = decision if decision in {"accepted", "rejected"} else "inbox"
    import hashlib
    suffix = hashlib.sha256(json.dumps(record.get('variant_dimensions', {}), sort_keys=True).encode()).hexdigest()[:8]
    destination = root / "knowledge" / area / f"{record['date_added']}-{slugify(record['title'])}-{suffix}.json"
    if args.dry_run:
        print(json.dumps({'status': decision, 'dry_run': True, 'reasons': reasons, 'duplicate': duplicate.as_dict()}, indent=2))
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        print(json.dumps({"status": "not-captured", "reason": "candidate path already exists"}, indent=2))
        return 1
    with destination.open('x', encoding='utf-8') as handle:
        json.dump(record, handle, indent=2)
        handle.write('\n')
    appended = None
    if decision == "accepted":
        try:
            appended = append_record(root, destination)
        except (ValueError, OSError) as error:
            destination.unlink()
            print(json.dumps({'status': 'not-captured', 'reason': str(error)}, indent=2))
            return 1
    if decision != "accepted":
        append_ledger(root, {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "captured",
            "identifier": record_identifier(record),
            "decision": decision,
            "reasons": reasons,
            "duplicate": duplicate.as_dict(),
            "record": destination.relative_to(root).as_posix(),
        })
    print(json.dumps({
        "status": decision,
        "record": destination.relative_to(root).as_posix(),
        "appended": appended.relative_to(root).as_posix() if appended else None,
        "reasons": reasons,
        "duplicate": duplicate.as_dict(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
