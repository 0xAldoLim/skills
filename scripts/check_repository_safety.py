#!/usr/bin/env python3
"""Scan the complete active repository for credential material and broken fences.

Research citations and historical addresses do not authorize network actions.
Behavioral scope enforcement is covered by dedicated helper/policy tests.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----\s+[A-Za-z0-9+/=]{40,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bctfd_[A-Za-z0-9_-]{16,}\b"),
)
IP_RE = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
SAFE_HOSTS = {"example.com", "example.org", "example.net", "example.invalid", "target.example", "localhost"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".jsonl"}


def scan(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        text = data.decode("utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relative}: possible secret matching {pattern.pattern}")
        if path.suffix.lower() == '.md':
            fence = None
            for line in text.splitlines():
                marker = re.match(r'^\s*(`{3,}|~{3,})', line)
                if marker:
                    if fence is None:
                        fence = (marker[1][0], len(marker[1]))
                    elif marker[1][0] == fence[0] and len(marker[1]) >= fence[1]:
                        fence = None
            if fence is not None:
                errors.append(f'{relative}: unbalanced fenced code block')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = scan(args.root.resolve())
    if errors:
        print("repository safety scan failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("repository safety scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
