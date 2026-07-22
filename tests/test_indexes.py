from pathlib import Path

from rebuild_indexes import CATEGORY_ROUTES, build_index


ROOT = Path(__file__).resolve().parents[1]


def test_indexes_are_deterministic_and_current() -> None:
    for category in CATEGORY_ROUTES:
        expected = build_index(ROOT, category)
        assert (ROOT / category / "INDEX.md").read_text(encoding="utf-8") == expected


def test_web_index_exposes_curated_learning() -> None:
    assert "[LEARNED.md](LEARNED.md)" in (ROOT / "ctf-web" / "INDEX.md").read_text(encoding="utf-8")
