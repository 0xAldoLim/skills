from pathlib import Path

from validate_skills import MAJOR, parse_frontmatter, validate


ROOT = Path(__file__).resolve().parents[1]


def test_skill_validator() -> None:
    assert validate(ROOT) == []


def test_direct_invocation_names_and_prompts() -> None:
    for category in MAJOR:
        metadata, errors = parse_frontmatter(ROOT / category / "SKILL.md")
        assert not errors
        assert metadata["name"] == category
        agent = (ROOT / category / "agents" / "openai.yaml").read_text(encoding="utf-8")
        assert f"${category}" in agent
        assert "allow_implicit_invocation: true" in agent


def test_dispatcher_is_discoverable() -> None:
    metadata, errors = parse_frontmatter(ROOT / "solve-challenge" / "SKILL.md")
    assert not errors
    assert metadata["name"] == "solve-challenge"
