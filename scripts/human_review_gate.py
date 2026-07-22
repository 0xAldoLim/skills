#!/usr/bin/env python3
"""Gate human-review recommendations on concrete machine-comprehension evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


VALID_REASONS = {
    "handwriting",
    "ambiguous_glyphs",
    "conflicting_ocr",
    "distorted_visual",
    "spatial_arrangement",
    "difficult_speech",
    "physical_context_missing",
    "subtle_geolocation",
    "captcha_or_artistic_glyphs",
    "cultural_or_contextual_interpretation",
    "repeated_nonverifiable_candidates",
}


def evaluate(status: dict[str, Any]) -> dict[str, Any]:
    attempted = status.get("attempted_machine_methods", [])
    reasons: list[str] = []
    if status.get("status") != "unsolved":
        reasons.append("status is not unsolved")
    if status.get("machine_analysis_exhausted") is not True:
        reasons.append("machine analysis is not recorded as exhausted")
    if status.get("human_review_reason") not in VALID_REASONS:
        reasons.append("reason is not a recognized comprehension limitation")
    if not status.get("artifact"):
        reasons.append("artifact is missing")
    if not status.get("specific_question"):
        reasons.append("specific question is missing")
    if len(attempted) < 2:
        reasons.append("fewer than two relevant machine methods were attempted")
    if status.get("remaining_machine_options"):
        reasons.append("machine options remain")
    return {
        "human_review_recommended": not reasons,
        "reasons": reasons,
        "artifact": status.get("artifact"),
        "specific_question": status.get("specific_question"),
        "candidate_values": status.get("candidate_values", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("status", type=Path)
    args = parser.parse_args()
    value = json.loads(args.status.read_text(encoding="utf-8"))
    result = evaluate(value)
    print(json.dumps(result, indent=2))
    return 0 if result["human_review_recommended"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
