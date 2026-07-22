#!/usr/bin/env python3
"""Fail when any protected original file prefix changes or becomes shorter."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def verify(root: Path, manifest_path: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for entry in manifest.get("protected_files", []):
        path = root / entry["path"]
        length = int(entry["protected_original_byte_length"])
        if not path.is_file():
            errors.append(f"missing protected file: {entry['path']}")
            continue
        data = path.read_bytes()
        if len(data) < length:
            errors.append(f"protected file shortened: {entry['path']} ({len(data)} < {length})")
            continue
        digest = hashlib.sha256(data[:length]).hexdigest()
        expected = entry.get("protected_prefix_sha256", entry["sha256"])
        if digest != expected:
            errors.append(f"protected prefix changed: {entry['path']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = args.manifest or root / "knowledge" / "integrity-manifest.json"
    errors = verify(root, manifest)
    if errors:
        print("append-only verification failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    count = len(json.loads(manifest.read_text(encoding="utf-8"))["protected_files"])
    print(f"append-only verification passed for {count} protected files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
