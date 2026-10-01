import os
import subprocess
import pytest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_installer(destination: Path, *options: str):
    env = os.environ.copy()
    env['SKILLS_DIR'] = destination.as_posix()
    command = ['sh', (ROOT/'install.sh').as_posix(), *options]
    if os.name == 'nt':
        # Git for Windows starts with a host PATH; initialize its POSIX tools.
        bash = Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git/bin/bash.exe'
        if not bash.exists(): pytest.skip('Git Bash is required for shell installer tests on Windows')
        env['SKILLS_DIR'] = os.path.relpath(destination, ROOT).replace('\\','/')
        command = [str(bash), '-c', 'export PATH=/usr/bin:/bin:$PATH; exec sh "$@"', 'ctf-installer', *command[1:]]
    return subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=180)


def test_installer_copies_supporting_references(tmp_path: Path) -> None:
    destination = tmp_path / "skills"
    result = run_installer(destination, '--copy')
    assert result.returncode == 0, result.stderr
    assert (destination / "ctf-reverse" / "SKILL.md").is_file()
    assert (destination / "ctf-reverse" / "INDEX.md").is_file()
    assert (destination / "ctf-reverse" / "tools.md").is_file()
    assert (destination / "ctf-reverse" / "agents" / "openai.yaml").is_file()
    assert (destination / 'scripts/instance_health.py').is_file()
    assert (destination / 'docs/SCOPE.md').is_file()


def test_installer_preflights_conflicts_and_backs_up(tmp_path):
    destination=tmp_path/'skills'
    existing=destination/'ctf-web';existing.mkdir(parents=True)
    (existing/'personal.txt').write_text('keep me')
    result=run_installer(destination,'--copy')
    assert result.returncode != 0
    assert not (destination/'ctf-crypto').exists()
    assert (existing/'personal.txt').read_text() == 'keep me'
    result=run_installer(destination,'--copy','--replace')
    assert result.returncode == 0, result.stderr
    backups=list(tmp_path.glob('skills.ctf-backup-*'))
    assert len(backups)==1 and (backups[0]/'ctf-web/personal.txt').read_text()=='keep me'


def test_installer_dry_run_has_no_writes(tmp_path):
    destination=tmp_path/'new'
    assert run_installer(destination,'--dry-run').returncode == 0
    assert not destination.exists()
