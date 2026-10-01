#!/usr/bin/env python3
"""Rank local reference sections without loading entire category files."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TOKEN = re.compile(r"[a-z0-9][a-z0-9_+.-]+")


def sections(path: Path):
    """Yield real Markdown headings, excluding fenced code and YAML."""
    lines = path.read_text(encoding="utf-8").splitlines()
    fence = None
    starts = []
    frontmatter = bool(lines and lines[0] == "---")
    for i, line in enumerate(lines):
        if frontmatter:
            if i and line == "---":
                frontmatter = False
            continue
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            kind = marker[1][0]
            fence = None if fence == kind else (kind if fence is None else fence)
            continue
        match = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
        if match and fence is None:
            starts.append((i, match[2], len(match[1])))
    for n, (start, title, level) in enumerate(starts):
        end = next((row for row, _, depth in starts[n + 1:] if depth <= level), len(lines))
        yield {"title": title, "line": start + 1, "end_line": end,
               "text": "\n".join(lines[start:end]), "level": level}


def search(root: Path, query: str, category: str | None = None, limit: int = 5):
    wanted = set(TOKEN.findall(query.lower()))
    if not wanted:
        return []
    candidates = []
    directories = [root / category] if category else sorted(root.glob("ctf-*"))
    for directory in directories:
        for path in sorted(directory.rglob("*.md")):
            if path.name in {"SKILL.md", "INDEX.md"}:
                continue
            found = list(sections(path))
            # A file title covers every child and otherwise wins broad searches.
            narrow = [section for section in found if section['level'] > 1]
            for section in narrow or found:
                title_tokens = set(TOKEN.findall(section["title"].lower()))
                body_tokens = set(TOKEN.findall(section["text"].lower()))
                score = 4 * len(wanted & title_tokens) + len(wanted & body_tokens)
                if score:
                    candidates.append({"path": path.relative_to(root).as_posix(),
                                       "title": section["title"], "line": section["line"],
                                       "end_line": section["end_line"], "score": score})
    return sorted(candidates, key=lambda item: (-item["score"], item["end_line"] - item["line"], item["path"]))[:limit]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--category", choices=["ctf-" + name for name in ("web", "pwn", "crypto", "reverse", "forensics", "osint", "malware", "misc", "ai-ml")])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.limit <= 20:
        parser.error("limit must be between 1 and 20")
    print(json.dumps(search(args.root.resolve(), args.query, args.category, args.limit), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
