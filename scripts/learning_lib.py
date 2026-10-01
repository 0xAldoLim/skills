#!/usr/bin/env python3
"""Shared helpers for evidence-gated learning and prerequisite-aware retrieval."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable


CATEGORIES = {
    "ctf-ai-ml",
    "ctf-crypto",
    "ctf-forensics",
    "ctf-malware",
    "ctf-misc",
    "ctf-osint",
    "ctf-pwn",
    "ctf-reverse",
    "ctf-web",
}

REQUIRED_FIELDS = (
    "title",
    "category",
    "subcategories",
    "trigger_conditions",
    "challenge_context",
    "observed_problem",
    "technique",
    "core_insight",
    "commands_or_code",
    "verification_evidence",
    "resulting_primitive",
    "flag_verified",
    "failure_modes",
    "when_not_to_use",
    "related_existing_techniques",
    "source_type",
    "source_reference",
    "confidence",
    "date_added",
)

INVALID_SOURCE_TYPES = {"failed_guess", "unverified_payload", "speculation", "accident"}
HIGH_CONFIDENCE = {"high", "verified"}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+_.-]+")
DIMENSIONS = ("runtime", "architecture", "mitigation", "parser", "oracle", "constraint", "framework", "version", "protocol")


@dataclass(frozen=True)
class DuplicateResult:
    decision: str
    score: float
    matches: tuple[str, ...]
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "score": round(self.score, 3),
            "matches": list(self.matches),
            "reason": self.reason,
        }


def load_record(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ImportError as yaml_exc:
            raise ValueError("record must be JSON unless PyYAML is installed") from yaml_exc
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("learning record must be an object")
    return value


def validate_record(record: dict[str, Any]) -> list[str]:
    errors = [f"missing required field: {field}" for field in REQUIRED_FIELDS if field not in record]
    category = record.get("category")
    if category not in CATEGORIES:
        errors.append(f"category must be one of: {', '.join(sorted(CATEGORIES))}")
    if "flag_verified" in record and not isinstance(record["flag_verified"], bool):
        errors.append("flag_verified must be boolean")
    for field in ("subcategories", "trigger_conditions", "failure_modes", "when_not_to_use", "related_existing_techniques"):
        if field in record and not isinstance(record[field], list):
            errors.append(f"{field} must be an array")
    if "confidence" in record and str(record["confidence"]).lower() not in {"low", "medium", "high", "verified"}:
        errors.append("confidence must be low, medium, high, or verified")
    if "date_added" in record:
        try:
            date.fromisoformat(str(record["date_added"]))
        except ValueError:
            errors.append("date_added must use YYYY-MM-DD")
    for field in ("title", "technique", "core_insight", "verification_evidence", "resulting_primitive"):
        if field in record and (not isinstance(record[field], str) or not record[field].strip()):
            errors.append(f"{field} must be nonempty text")
    for field in ("flag_value", "password", "instance_id", "live_target", "credentials"):
        if record.get(field):
            errors.append(f"remove challenge-specific sensitive field: {field}")
    if re.search(r"\b(?:flag|ctf|ductf|wgmy|gemastik|htb|picoctf|sekai)\{[^{}\n]{3,}\}", json.dumps(record), re.I):
        errors.append("remove literal flag values from reusable knowledge")
    if "variant_dimensions" in record:
        dimensions = record['variant_dimensions']
        if not isinstance(dimensions, dict):
            errors.append("variant_dimensions must be an object")
        elif any(key not in DIMENSIONS or not isinstance(value, str) or not value.strip() for key, value in dimensions.items()):
            errors.append("variant_dimensions requires recognized dimensions with nonempty text")
    for field in ('understood', 'materially_contributed', 'reusable', 'reproducible'):
        if field in record and not isinstance(record[field], bool):
            errors.append(field + ' must be boolean')
    for field in ('subcategories', 'trigger_conditions', 'failure_modes', 'when_not_to_use', 'related_existing_techniques'):
        if isinstance(record.get(field), list) and any(not isinstance(item, str) for item in record[field]):
            errors.append(field + ' items must be text')
    return errors


def normalize(value: Any) -> str:
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    return " ".join(TOKEN_RE.findall(str(value).lower()))


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "learning"


def command_fingerprint(value: Any) -> str:
    if isinstance(value, list):
        value = "\n".join(str(item) for item in value)
    # Preserve punctuation, numbers and encoding: payload bytes are semantics.
    normalized = str(value).replace("\r\n", "\n").strip()
    return hashlib.sha256(normalized.encode()).hexdigest() if normalized else ""


def record_identifier(record: dict[str, Any]) -> str:
    explicit = str(record.get("identifier", "")).strip().lower()
    return explicit or f"{record.get('category', 'unknown')}:{slugify(str(record.get('title', 'learning')))}"


def _tokens(record: dict[str, Any]) -> set[str]:
    fields = (
        record.get("title", ""),
        record.get("trigger_conditions", []),
        record.get("resulting_primitive", ""),
        record.get("core_insight", ""),
        record.get("technique", ""),
        record.get("prerequisites", []),
    )
    return set(normalize(list(fields)).split())


def _jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right) if left or right else 0.0


def find_duplicate(candidate: dict[str, Any], existing: Iterable[dict[str, Any]]) -> DuplicateResult:
    candidate_id = record_identifier(candidate)
    candidate_title = normalize(candidate.get("title", ""))
    candidate_aliases = {normalize(x) for x in candidate.get("aliases", [])}
    candidate_commands = command_fingerprint(candidate.get("commands_or_code", ""))
    candidate_triplet = normalize([
        candidate.get("trigger_conditions", []),
        candidate.get("resulting_primitive", ""),
        candidate.get("verification_evidence", ""),
    ])
    strong_variant = None
    title_review = None
    best_score = 0.0
    best_match = ""
    best_reason = "no equivalent technique found"
    for record in existing:
        identifier = record_identifier(record)
        if record.get("category") != candidate.get("category"):
            continue
        left = candidate.get("variant_dimensions", {})
        right = record.get("variant_dimensions", {})
        changed = [key for key in DIMENSIONS if key in left and key in right and normalize(left[key]) != normalize(right[key])]
        if changed and (_jaccard(_tokens(candidate), _tokens(record)) >= 0.4 or candidate_title == normalize(record.get("title", ""))):
            strong_variant = DuplicateResult("variant", 0.8, (identifier,), "different verified prerequisites: " + ", ".join(changed))
            continue
        title = normalize(record.get("title", ""))
        similarity = _jaccard(_tokens(candidate), _tokens(record))
        aliases = {normalize(x) for x in record.get("aliases", [])}
        if candidate_id == identifier:
            result = DuplicateResult("duplicate" if similarity >= 0.78 else "review", 1.0, (identifier,), "exact identifier match")
            if result.decision == 'duplicate':
                return result
            title_review = result
        if candidate_title and candidate_title == title:
            result = DuplicateResult("duplicate" if similarity >= 0.78 else "review", similarity, (identifier,), "normalized title match")
            if result.decision == 'duplicate':
                return result
            title_review = result
        if candidate_title in aliases or title in candidate_aliases or candidate_aliases & aliases:
            result = DuplicateResult("duplicate" if similarity >= 0.78 else "review", similarity, (identifier,), "alias match")
            if result.decision == 'duplicate':
                return result
            title_review = result
        fingerprint = command_fingerprint(record.get("commands_or_code", ""))
        if candidate_commands and candidate_commands == fingerprint:
            return DuplicateResult("duplicate", 0.95, (identifier,), "command or payload fingerprint match")
        triplet = normalize([
            record.get("trigger_conditions", []),
            record.get("resulting_primitive", ""),
            record.get("verification_evidence", ""),
        ])
        if candidate_triplet and candidate_triplet == triplet:
            return DuplicateResult("duplicate", 0.93, (identifier,), "same trigger, primitive, and outcome")
        score = _jaccard(_tokens(candidate), _tokens(record))
        if score > best_score:
            best_score, best_match, best_reason = score, identifier, "semantic token similarity"
    if strong_variant is not None:
        return strong_variant
    if title_review is not None:
        return title_review
    if best_score >= 0.78:
        return DuplicateResult("review", best_score, (best_match,), best_reason)
    if best_score >= 0.52:
        return DuplicateResult("variant", best_score, (best_match,), "related technique; preserve meaningful constraints")
    return DuplicateResult("unique", best_score, tuple(filter(None, (best_match,))), best_reason)


def iter_learning_records(root: Path, exclude: Path | None = None) -> Iterable[dict[str, Any]]:
    from lookup_knowledge import sections
    fence_re = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
    for category in sorted(CATEGORIES):
        directory = root / category
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            if path.name in {"INDEX.md", "SKILL.md"}:
                continue
            text = path.read_text(encoding="utf-8")
            for section in sections(path):
                if section['level'] == 1:
                    continue
                body = section['text']
                title = section['title'].strip(" *:#`")
                if len(title) < 4:
                    continue
                dimensions = {}
                match = re.search(r"^\*\*Prerequisite dimensions:\*\* (.+)$", body, re.M)
                if match:
                    try:
                        parsed = json.loads(match[1])
                        if isinstance(parsed, dict):
                            dimensions = parsed
                    except ValueError:
                        pass
                yield {
                    "identifier": f"authored:{path.relative_to(root).as_posix()}:{section['line']}",
                    "title": title, "category": category,
                    "trigger_conditions": [body], "resulting_primitive": "",
                    "verification_evidence": "", "core_insight": body,
                    "technique": body, "commands_or_code": "",
                    "variant_dimensions": dimensions,
                }
            for block_number, block in enumerate(fence_re.findall(text), 1):
                if not normalize(block):
                    continue
                yield {
                    "identifier": f"authored-code:{path.relative_to(root).as_posix()}:{block_number}",
                    "title": f"Code example in {path.name} section {block_number}",
                    "category": category, "trigger_conditions": [],
                    "resulting_primitive": "", "verification_evidence": "",
                    "core_insight": "", "commands_or_code": block,
                }
    # Failed/speculative inbox and rejected records must not suppress a later verified method.
    for area in ("accepted",):
        directory = root / "knowledge" / area
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            if exclude and path.resolve() == exclude.resolve():
                continue
            try:
                yield load_record(path)
            except (OSError, ValueError):
                continue


def classify_record(record: dict[str, Any], duplicate: DuplicateResult) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if str(record.get("source_type", "")).lower() in INVALID_SOURCE_TYPES:
        return "rejected", ["source type is excluded from learning"]
    gates = {
        "verified flag": record.get("flag_verified") is True,
        "material contribution": record.get("materially_contributed") is True,
        "reusable beyond one challenge": record.get("reusable") is True,
        "reproducible": record.get("reproducible") is True,
        "high category confidence": str(record.get("category_confidence", record.get("confidence", ""))).lower() in HIGH_CONFIDENCE,
        "no equivalent technique": duplicate.decision == "unique" or (
            duplicate.decision == "variant" and bool(record.get("variant_dimensions"))
            and duplicate.reason.startswith("different verified prerequisites:")),
        "understood behavior": record.get("understood") is True,
    }
    reasons.extend(label for label, passed in gates.items() if not passed)
    return ("accepted", []) if all(gates.values()) else ("inbox", reasons)


def render_learning_markdown(record: dict[str, Any], variant_of: str | None = None) -> str:
    def bullets(value: Any) -> str:
        items = value if isinstance(value, list) else [value]
        return "\n".join(f"- {item}" for item in items if str(item).strip()) or "- None recorded"

    variant = f"\n**Variant of:** {variant_of}\n" if variant_of else ""
    return (
        f"\n## {record['title']}\n\n<!-- learning:{record_identifier(record)} -->\n\n"
        f"**Added:** {record['date_added']}\n\n"
        f"**Source:** {record['source_type']} — {record['source_reference']}\n\n"
        f"**Confidence:** {record['confidence']}\n"
        f"\n**Prerequisite dimensions:** {json.dumps(record.get('variant_dimensions', {}), sort_keys=True)}\n"
        f"{variant}\n"
        f"**Trigger conditions**\n\n{bullets(record['trigger_conditions'])}\n\n"
        f"**Core insight**\n\n{record['core_insight']}\n\n"
        f"**Technique**\n\n{record['technique']}\n\n"
        f"**Commands or code**\n\n```text\n{record['commands_or_code']}\n```\n\n"
        f"**Verification evidence**\n\n{record['verification_evidence']}\n\n"
        f"**Resulting primitive**\n\n{record['resulting_primitive']}\n\n"
        f"**Failure modes**\n\n{bullets(record['failure_modes'])}\n\n"
        f"**When not to use**\n\n{bullets(record['when_not_to_use'])}\n"
    )


def append_ledger(root: Path, event: dict[str, Any]) -> None:
    ledger = root / "knowledge" / "learning-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
