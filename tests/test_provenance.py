import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_external_sources_are_commit_pinned_and_licensed() -> None:
    lock = json.loads((ROOT / "knowledge" / "sources.lock.json").read_text(encoding="utf-8"))
    assert {source["id"] for source in lock["sources"]} == {"ljagiello-ctf-skills", "yaklang-hack-skills"}
    for source in lock["sources"]:
        assert re.fullmatch(r"[0-9a-f]{40}", source["commit"])
        assert source["license"] == "MIT"


def test_enrichment_report_is_conservative_and_complete() -> None:
    report = json.loads((ROOT / "knowledge" / "enrichment-report.json").read_text(encoding="utf-8"))
    assert {entry["decision"] for entry in report} >= {"added", "skipped"}
    for entry in report:
        assert entry["source_commit"]
        assert entry["reason"]
        assert entry["decision"] in {"added", "inbox", "skipped"}
