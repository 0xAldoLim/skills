from pathlib import Path

from verify_append_only import verify


ROOT = Path(__file__).resolve().parents[1]


def test_all_original_prefixes_are_preserved() -> None:
    assert verify(ROOT, ROOT / "knowledge" / "integrity-manifest.json") == []
