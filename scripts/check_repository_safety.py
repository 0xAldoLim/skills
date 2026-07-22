#!/usr/bin/env python3
"""Scan added/appended material for secrets, live targets, and malformed Markdown."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
from pathlib import Path


SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bctfd_[A-Za-z0-9_-]{16,}\b"),
)
IP_RE = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
SAFE_HOSTS = {"example.com", "example.org", "example.net", "example.invalid", "target.example", "localhost"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".jsonl"}


def scan(root: Path) -> list[str]:
    errors: list[str] = []
    manifest = json.loads((root / "knowledge" / "integrity-manifest.json").read_text(encoding="utf-8"))
    protected = {entry["path"]: int(entry["protected_original_byte_length"]) for entry in manifest["protected_files"]}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        data = data[protected.get(relative, 0):]
        text = data.decode("utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relative}: possible secret matching {pattern.pattern}")
        for raw_ip in IP_RE.findall(text):
            try:
                address = ipaddress.ip_address(raw_ip)
            except ValueError:
                continue
            if address.is_global:
                errors.append(f"{relative}: globally routable example address {raw_ip}")
        for host in re.findall(r"https?://([A-Za-z0-9.-]+)", text):
            if host not in SAFE_HOSTS and not host.endswith(("github.com", "githubusercontent.com", "openai.com", "json-schema.org")):
                errors.append(f"{relative}: non-allowlisted example host {host}")
        if path.suffix.lower() == ".md" and text.count("```") % 2:
            errors.append(f"{relative}: unbalanced fenced code block in added/appended material")
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
