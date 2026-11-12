from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reverse_new_references_are_routed() -> None:
    index = (ROOT / "ctf-reverse" / "INDEX.md").read_text(encoding="utf-8")
    for name in ("radare2-r2pipe.md", "mba-simplification.md", "tools-mcp.md"):
        assert name in index
        assert (ROOT / "ctf-reverse" / name).is_file()


def test_pwn_new_references_and_scripts_are_routed() -> None:
    index = (ROOT / "ctf-pwn" / "INDEX.md").read_text(encoding="utf-8")
    assert "attack-playbook.md" in index
    assert "scripts/README.md" in index
    scripts = sorted((ROOT / "ctf-pwn" / "scripts").glob("*.py"))
    assert len(scripts) >= 5
    for path in scripts:
        text = path.read_text(encoding="utf-8")
        assert "authorized local/assigned targets only" in text
        assert "ctfd" not in text.lower()
        assert "scoreboard" not in text.lower()


def test_similar_search_is_not_integrated() -> None:
    assert not (ROOT / "ctf-similar-search").exists()
    text = (ROOT / "docs" / "UPSTREAM_SKILLS.md").read_text(encoding="utf-8")
    assert "Tavily" in text
    assert "Rejected" in text
