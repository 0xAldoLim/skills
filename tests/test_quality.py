import subprocess
import sys
import shutil
from pathlib import Path
import pytest

from check_repository_safety import scan


ROOT = Path(__file__).resolve().parents[1]


def test_no_new_secrets_or_live_infrastructure() -> None:
    assert scan(ROOT) == []


def test_python_scripts_compile() -> None:
    result = subprocess.run([sys.executable, "-m", "compileall", "-q", str(ROOT / "scripts")], check=False)
    assert result.returncode == 0


def test_shell_scripts_parse() -> None:
    shell = shutil.which('sh')
    if shell is None and sys.platform == 'win32':
        git_bash = Path('C:/Program Files/Git/bin/bash.exe')
        shell = str(git_bash) if git_bash.is_file() else None
    if shell is None:
        pytest.skip('POSIX shell unavailable on this host')
    for path in (ROOT / "install.sh", ROOT / "scripts" / "install_ctf_tools.sh"):
        result = subprocess.run([shell, "-n", str(path)], check=False)
        assert result.returncode == 0
