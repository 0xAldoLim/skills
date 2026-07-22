from pathlib import Path

from rebuild_indexes import CATEGORY_ROUTES


ROOT = Path(__file__).resolve().parents[1]


def test_every_category_has_a_direct_prompt() -> None:
    for category in CATEGORY_ROUTES:
        text = (ROOT / "prompts" / f"{category}.md").read_text(encoding="utf-8")
        assert text.startswith(f"Use ${category}.")
        assert "{{DESCRIPTION}}" in text
        assert "{{WORKSPACE}}" in text


def test_dispatcher_prompt_exists() -> None:
    assert (ROOT / "prompts" / "solve-challenge.md").is_file()
