#!/usr/bin/env python3
"""Conservative heading-level comparison for pinned external skill sources."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


HEADING_RE = re.compile(r"^#{2,4}\s+(.+?)\s*$", re.MULTILINE)


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def headings(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        for heading in HEADING_RE.findall(path.read_text(encoding="utf-8", errors="ignore")):
            key = normalized(heading)
            if key:
                result.setdefault(key, path.relative_to(root).as_posix())
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", nargs=2, metavar=("NAME", "PATH"), required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    local = headings(args.root.resolve())
    report: list[dict[str, object]] = []
    for name, raw_path in args.source:
        source = Path(raw_path).resolve()
        commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        for title, source_path in headings(source).items():
            exact = title in local
            overlap = max((len(set(title.split()) & set(candidate.split())) / len(set(title.split()) | set(candidate.split())) for candidate in local), default=0.0)
            report.append({
                "source_technique": title,
                "source_repository": name,
                "source_commit": commit,
                "source_path": source_path,
                "candidate_category": None,
                "existing_overlap": local.get(title),
                "duplicate_score": round(1.0 if exact else overlap, 3),
                "decision": "skipped" if exact else "inbox",
                "reason": "exact normalized heading exists" if exact else "semantic review required before append",
                "destination_file": None,
            })
    destination = args.output or args.root / "knowledge" / "generated-enrichment-scan.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(report)} conservative comparisons to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
