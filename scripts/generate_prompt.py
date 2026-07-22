#!/usr/bin/env python3
"""Render a category prompt without exposing internal reference filenames."""

from __future__ import annotations

import argparse
from pathlib import Path

from classify_challenge import classify, collect_facts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category")
    parser.add_argument("--description", required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--remote")
    args = parser.parse_args()
    category = args.category
    if not category:
        category = classify(collect_facts(args.description, args.workspace, args.remote))["primary_category"]
    template = Path(__file__).resolve().parents[1] / "prompts" / f"{category}.md"
    if not template.is_file():
        template = Path(__file__).resolve().parents[1] / "prompts" / "solve-challenge.md"
    text = template.read_text(encoding="utf-8")
    print(text.replace("{{WORKSPACE}}", str(args.workspace.resolve())).replace("{{DESCRIPTION}}", args.description).replace("{{REMOTE}}", args.remote or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
