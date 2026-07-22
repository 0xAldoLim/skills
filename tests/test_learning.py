import copy
import json
from pathlib import Path

import pytest

from append_learning import append_record
from learning_lib import classify_record, find_duplicate, load_record, validate_record


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "knowledge" / "accepted" / "2026-07-22-java-ghost-bits.json"


def test_learning_records_match_required_contract() -> None:
    schema = json.loads((ROOT / "schemas" / "learning.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])
    for path in sorted((ROOT / "knowledge" / "accepted").glob("*.json")):
        record = load_record(path)
        assert not validate_record(record)
        assert required <= record.keys()


def test_duplicate_layers_detect_identifier_and_title() -> None:
    record = load_record(BASE)
    assert find_duplicate(record, [record]).decision == "duplicate"
    renamed = copy.deepcopy(record)
    renamed["identifier"] = "custom-id"
    assert find_duplicate(renamed, [record]).reason == "normalized title match"


def test_duplicate_layers_detect_alias_command_and_outcome() -> None:
    record = load_record(BASE)
    alias_existing = copy.deepcopy(record)
    alias_existing.update({"identifier": "existing:alias", "title": "Original name", "aliases": ["low byte bridge"]})
    alias_candidate = copy.deepcopy(record)
    alias_candidate.update({"identifier": "candidate:alias", "title": "Low Byte Bridge", "commands_or_code": "different", "verification_evidence": "different"})
    assert find_duplicate(alias_candidate, [alias_existing]).reason == "alias match"

    command_candidate = copy.deepcopy(record)
    command_candidate.update({"identifier": "candidate:command", "title": "Different title", "commands_or_code": "probe --count 99"})
    command_existing = copy.deepcopy(record)
    command_existing.update({"identifier": "existing:command", "title": "Other title", "commands_or_code": "probe --count 12"})
    assert find_duplicate(command_candidate, [command_existing]).reason == "command or payload fingerprint match"

    triplet_candidate = copy.deepcopy(record)
    triplet_candidate.update({"identifier": "candidate:triplet", "title": "Triplet one", "commands_or_code": "one"})
    triplet_existing = copy.deepcopy(record)
    triplet_existing.update({"identifier": "existing:triplet", "title": "Triplet two", "commands_or_code": "two"})
    assert find_duplicate(triplet_candidate, [triplet_existing]).reason == "same trigger, primitive, and outcome"


def test_auto_acceptance_requires_verified_solve() -> None:
    record = load_record(BASE)
    result = find_duplicate(record, [])
    decision, reasons = classify_record(record, result)
    assert decision == "inbox"
    assert "verified flag" in reasons
    assert "material contribution" in reasons


def test_verified_unique_record_can_auto_accept() -> None:
    record = load_record(BASE)
    record.update({
        "title": "Synthetic reusable verified technique",
        "flag_verified": True,
        "materially_contributed": True,
        "reusable": True,
        "reproducible": True,
        "category_confidence": "high",
    })
    decision, reasons = classify_record(record, find_duplicate(record, []))
    assert decision == "accepted"
    assert reasons == []


def test_append_pipeline_never_overwrites_and_ledgers(tmp_path: Path) -> None:
    record = load_record(BASE)
    record.update({
        "identifier": "ctf-web:synthetic-append",
        "title": "Synthetic append-only pipeline technique",
        "commands_or_code": "synthetic-command --safe-placeholder",
        "verification_evidence": "A synthetic test verifies deterministic append behavior.",
        "flag_verified": True,
        "materially_contributed": True,
        "reusable": True,
        "reproducible": True,
        "category_confidence": "high",
    })
    source = tmp_path / "candidate.json"
    source.write_text(json.dumps(record), encoding="utf-8")
    destination = append_record(tmp_path, source)
    first = destination.read_bytes()
    assert record["title"].encode() in first
    assert (tmp_path / "knowledge" / "learning-ledger.jsonl").is_file()
    with pytest.raises(ValueError, match="equivalent technique exists"):
        append_record(tmp_path, source)
    assert destination.read_bytes() == first
