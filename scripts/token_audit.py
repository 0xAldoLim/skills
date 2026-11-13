#!/usr/bin/env python3
"""Measure skill prompt-loading cost and enforce a compact entrypoint budget.

Token estimates use characters/4, a deterministic approximation, not a provider
billing tokenizer. Measure relative changes, not exact billed usage.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import yaml

MAX_BODY_TOKENS = 1700
MAX_CATEGORY_LOAD_TOKENS = 3200
MAX_DESCRIPTION_CHARS = 1024
MAX_COMPATIBILITY_CHARS = 500
MAX_LISTING_CHARS = 12000


def estimate(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    try:
        data = yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        data = {}
    return (data if isinstance(data, dict) else {}), text[end + 4:].lstrip("\n")


def audit(root: Path) -> dict:
    skills = {}
    for path in sorted(root.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        metadata, body = split_frontmatter(text)
        skills[path.parent.name] = {
            "body_chars": len(body),
            "body_tokens": estimate(body),
            "description_chars": len(str(metadata.get("description", ""))),
            "compatibility_chars": len(str(metadata.get("compatibility", ""))),
            "license": metadata.get("license"),
        }
    common = skills.get("ctf-common", {})
    category_load = {}
    for name, item in skills.items():
        if name.startswith("ctf-") and name != "ctf-common":
            category_load[name] = item["body_tokens"] + common.get("body_tokens", 0)
    listing_chars = sum(item["description_chars"] for item in skills.values())
    violations = []
    for name, item in skills.items():
        if item["body_tokens"] > (1100 if name == "solve-challenge" else MAX_BODY_TOKENS):
            violations.append(f"{name}: body ~{item['body_tokens']} tokens exceeds budget")
        if item["description_chars"] > MAX_DESCRIPTION_CHARS:
            violations.append(f"{name}: description exceeds {MAX_DESCRIPTION_CHARS} characters")
        if item["compatibility_chars"] > MAX_COMPATIBILITY_CHARS:
            violations.append(f"{name}: compatibility exceeds {MAX_COMPATIBILITY_CHARS} characters")
        if not item["license"] and (name.startswith("ctf-") or name == "solve-challenge"):
            violations.append(f"{name}: missing license")
    for name, tokens in category_load.items():
        if tokens > MAX_CATEGORY_LOAD_TOKENS:
            violations.append(f"{name}: category+common ~{tokens} tokens exceeds budget")
    if listing_chars > MAX_LISTING_CHARS:
        violations.append(f"skill listing descriptions exceed {MAX_LISTING_CHARS} characters")
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "method": "ceil(characters/4); relative estimate only",
        "skills": skills,
        "category_load_tokens": category_load,
        "listing_description_chars": listing_chars,
        "budgets": {
            "max_body_tokens": MAX_BODY_TOKENS,
            "max_category_load_tokens": MAX_CATEGORY_LOAD_TOKENS,
            "max_description_chars": MAX_DESCRIPTION_CHARS,
            "max_compatibility_chars": MAX_COMPATIBILITY_CHARS,
            "max_listing_chars": MAX_LISTING_CHARS,
        },
        "violations": violations,
    }


def compare(report: dict, baseline_path: Path) -> dict:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    old = baseline.get("skills", {})
    changes = {}
    for name, item in report["skills"].items():
        before = old.get(name, {}).get("body_chars")
        if before:
            after = item["body_chars"]
            changes[name] = {
                "before_chars": before,
                "after_chars": after,
                "reduction_percent": round(100 * (before - after) / before, 1),
            }
    return {"baseline_commit": baseline.get("commit"), "entrypoints": changes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = audit(args.root.resolve())
    if args.baseline:
        report["comparison"] = compare(report, args.baseline)
    print(json.dumps(report, indent=2))
    if args.check and report["violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
