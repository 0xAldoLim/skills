import json
import subprocess
import sys
from pathlib import Path
import install_tools
from enrich_from_sources import compare
ROOT=Path(__file__).resolve().parents[1]

def test_same_heading_different_body_requires_review():
    old={'title':'parser','body':'## parser\nold version 2.1','category':'ctf-web','path':'old.md'}
    new={**old,'body':'## parser\nnew namespace version 3.2'}
    assert compare(new,[old])[2]=='inbox'
    assert compare(old,[old])[2]=='skipped'

def test_dry_run_does_not_create_venv(tmp_path):
    venv=tmp_path/'no-write'
    result=subprocess.run([sys.executable,str(ROOT/'scripts/install_tools.py'),'all','--dry-run','--venv',str(venv)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    plan=json.loads(result.stdout)
    assert plan['heavy_explicit'] is False and 'torch' not in plan['missing_python']
    assert not venv.exists()

def test_missing_only_performs_install_and_verifies(monkeypatch,tmp_path):
    installed=set();importable=set();calls=[]
    manifest={'tiers':{'core':{'apt':{'tool-a':'cmd-a'},'python':{'dist-a':'module_a'}}}}
    class Result:
        returncode=0
    def run(command,**kw):
        calls.append(command)
        if 'apt-get' in command: installed.add('tool-a')
        if 'venv' in command:
            interpreter=tmp_path/'venv/bin/python';interpreter.parent.mkdir(parents=True);interpreter.touch()
        if 'pip' in command: importable.add('dist-a')
        return Result()
    real_loads=install_tools.json.loads
    monkeypatch.setattr(install_tools.json,'loads',lambda text:manifest if 'tiers' in text else real_loads(text))
    monkeypatch.setattr(install_tools,'apt_installed',lambda name:name in installed)
    monkeypatch.setattr(install_tools,'python_installed',lambda python,name,module:name in importable)
    monkeypatch.setattr(install_tools.shutil,'which',lambda name:'/usr/bin/'+name if name=='apt-get' or 'tool-a' in installed else None)
    monkeypatch.setattr(install_tools.subprocess,'run',run)
    monkeypatch.setattr(sys,'argv',['install_tools.py','core','--missing-only','--venv',str(tmp_path/'venv')])
    assert install_tools.main()==0
    assert any('apt-get' in call for call in calls) and any('pip' in call for call in calls)
    calls.clear()
    assert install_tools.main()==0 and not calls


def test_existing_sage_does_not_require_a_debian_package(monkeypatch):
    monkeypatch.setattr(install_tools.shutil,'which',lambda name:'/opt/sage/bin/sage' if name=='sage' else None)
    missing,setup=install_tools.resolve_sage({'sagemath':'sage'},['sagemath','ghidra'])
    assert missing==['ghidra'] and setup is None
    manifest={'tiers':{'heavy':{'apt':{'sagemath':'sage'},'python':{}}}}
    real_loads=install_tools.json.loads
    monkeypatch.setattr(install_tools.json,'loads',lambda text:manifest if 'tiers' in text else real_loads(text))
    monkeypatch.setattr(install_tools,'apt_installed',lambda name:False)
    monkeypatch.setattr(sys,'argv',['install_tools.py','heavy','--missing-only'])
    assert install_tools.main()==0


def test_missing_sage_candidate_is_an_actionable_fallback(monkeypatch):
    monkeypatch.setattr(install_tools.shutil,'which',lambda name:'/usr/bin/apt-cache' if name=='apt-cache' else None)
    class Result:
        returncode=0
        stdout='sagemath:\n  Candidate: (none)\n'
    monkeypatch.setattr(install_tools.subprocess,'run',lambda *args,**kwargs:Result())
    missing,setup=install_tools.resolve_sage({'sagemath':'sage'},['sagemath'])
    assert missing==[] and setup['tool']=='sage' and 'conda' in setup['fallback']
