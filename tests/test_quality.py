import subprocess
import sys
from pathlib import Path

from check_repository_safety import scan


ROOT = Path(__file__).resolve().parents[1]


def test_no_new_secrets_or_live_infrastructure() -> None:
    assert scan(ROOT) == []


def test_python_scripts_compile() -> None:
    result = subprocess.run([sys.executable, "-m", "compileall", "-q", str(ROOT / "scripts")], check=False)
    assert result.returncode == 0


def test_shell_scripts_parse() -> None:
    for path in (ROOT / "install.sh", ROOT / "scripts" / "install_ctf_tools.sh"):
        result = subprocess.run(["sh", "-n", str(path)], check=False)
        assert result.returncode == 0
