#!/usr/bin/env python3
"""Promote one verified learning into a targeted reference and compact index."""

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
    slugify,
)


def append_record(root: Path, source: Path, approved: bool = False) -> Path:
    directory = root / 'knowledge'
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / '.learning.lock'
    try:
        with lock.open('x', encoding='utf-8') as handle:
            import os
            handle.write(str(os.getpid()))
    except FileExistsError as error:
        raise ValueError('another learning promotion is active; inspect stale lock after a crash') from error
    try:
        return _append_record(root, source, approved)
    finally:
        lock.unlink(missing_ok=True)


def _append_record(root: Path, source: Path, approved: bool = False) -> Path:
    record = load_record(source)
    errors = validate_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    duplicate = find_duplicate(record, iter_learning_records(root, source))
    if duplicate.decision == "duplicate":
        raise ValueError(f"equivalent technique exists: {', '.join(duplicate.matches)}")
    decision, reasons = classify_record(record, duplicate)
    # A reviewed semantic overlap is the only overridable gate.
    immutable_failures = [reason for reason in reasons if reason != 'no equivalent technique']
    if decision != "accepted" and (not approved or immutable_failures or decision == 'rejected'):
        raise ValueError(f"record is {decision}: {', '.join(reasons) or duplicate.reason}")
    variant_of = duplicate.matches[0] if duplicate.decision == "variant" and duplicate.matches else None
    destination = root / record["category"] / "learned" / f"{slugify(record['title'])}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    # A same-title variant needs a distinct destination, not an overwrite.
    if destination.exists():
        import hashlib
        suffix = hashlib.sha256(json.dumps(record.get("variant_dimensions", {}), sort_keys=True).encode()).hexdigest()[:8]
        destination = destination.with_name(destination.stem + '-' + suffix + '.md')
    catalog = root / record["category"] / 'LEARNED.md'
    index = root / record["category"] / 'INDEX.md'
    ledger = root / 'knowledge/learning-ledger.jsonl'
    protected = (catalog, index, ledger)
    snapshots = {path: path.read_bytes() if path.exists() else None for path in protected}
    created = False
    try:
        with destination.open("x", encoding="utf-8") as handle:
            created = True
            handle.write('# Verified technique\n' + render_learning_markdown(record, variant_of))
        if not catalog.exists():
            catalog.write_text('# Learned techniques\n\nTargeted references require verification.\n', encoding='utf-8')
        with catalog.open('a', encoding='utf-8') as handle:
            handle.write(f"\n- [{record['title']}](learned/{destination.name}) — {record['resulting_primitive']}\n")
        from rebuild_indexes import build_index, CATEGORY_ROUTES
        if record['category'] in CATEGORY_ROUTES:
            index.write_text(build_index(root, record['category']), encoding='utf-8')
        append_ledger(root, {
            "timestamp": datetime.now(timezone.utc).isoformat(), "action": "appended",
            "identifier": record_identifier(record), "record": str(source),
            "destination": destination.relative_to(root).as_posix(), "duplicate": duplicate.as_dict(),
        })
    except BaseException:
        if created:
            destination.unlink(missing_ok=True)
        for path, contents in snapshots.items():
            if contents is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(contents)
        raise
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--approved", action="store_true", help="resolve a semantic review; cannot bypass verification gates")
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
