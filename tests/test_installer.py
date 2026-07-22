import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_installer_copies_supporting_references(tmp_path: Path) -> None:
    destination = tmp_path / "skills"
    env = os.environ.copy()
    env["SKILLS_DIR"] = str(destination)
    subprocess.run(["sh", str(ROOT / "install.sh")], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert (destination / "ctf-reverse" / "SKILL.md").is_file()
    assert (destination / "ctf-reverse" / "INDEX.md").is_file()
    assert (destination / "ctf-reverse" / "tools.md").is_file()
    assert (destination / "ctf-reverse" / "agents" / "openai.yaml").is_file()
