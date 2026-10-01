import copy
import json
import subprocess
import sys
from pathlib import Path
import pytest
from append_learning import append_record
from learning_lib import (classify_record, command_fingerprint, find_duplicate,
    iter_learning_records, load_record, validate_record)
ROOT=Path(__file__).resolve().parents[1]

def candidate():
    r=load_record(ROOT/'knowledge/accepted/2026-07-22-java-ghost-bits.json')
    r.update(title='Synthetic prerequisite method', identifier='ctf-web:fixture',
        commands_or_code='local-byte-check --width 16', flag_verified=True,
        materially_contributed=True,reusable=True,reproducible=True,understood=True,
        confidence='high',category_confidence='high')
    return r

def test_payload_fingerprint_preserves_semantics():
    assert command_fingerprint('probe --count 99') != command_fingerprint('probe --count 12')
    assert command_fingerprint('%2f') != command_fingerprint('/')

def test_title_collision_is_review_not_suppression():
    a=candidate();b=candidate()
    a.update(core_insight='filesystem metadata offsets',technique='walk ext inode tree',
             trigger_conditions=['budgeted raw blocks'],resulting_primitive='read file',
             commands_or_code='inode walk',verification_evidence='local hash')
    assert find_duplicate(a,[b]).decision=='review'

def test_meaningful_known_runtime_variant_auto_accepts():
    a=candidate();b=copy.deepcopy(a)
    a['variant_dimensions']={'version':'2.39','mitigation':'safe-linking'}
    b['variant_dimensions']={'version':'2.31','mitigation':'plain pointers'}
    result=find_duplicate(a,[b])
    assert result.decision=='variant'
    assert classify_record(a,result)==('accepted',[])
    # A later exact copy wins over a partial authored neighbor.
    assert find_duplicate(a,[b,a]).decision=='duplicate'

@pytest.mark.parametrize('field',['understood','flag_verified','materially_contributed','reusable','reproducible'])
def test_approved_cannot_bypass_evidence(tmp_path,field):
    record=candidate();record[field]=False
    source=tmp_path/'record.json';source.write_text(json.dumps(record))
    with pytest.raises(ValueError): append_record(tmp_path,source,approved=True)
    assert not list(tmp_path.glob('ctf-web/learned/*.md'))

def test_failed_inbox_does_not_suppress_verified_learning(tmp_path):
    inbox=tmp_path/'knowledge/inbox';inbox.mkdir(parents=True)
    record=candidate();(inbox/'old.json').write_text(json.dumps(record))
    assert find_duplicate(record,iter_learning_records(tmp_path)).decision=='unique'

def test_capture_dry_run_and_atomic_promotion(tmp_path):
    record=candidate();source=tmp_path/'record.json';source.write_text(json.dumps(record))
    command=[sys.executable,str(ROOT/'scripts/capture_learning.py'),str(source),'--root',str(tmp_path),'--auto']
    dry=subprocess.run(command+['--dry-run'],capture_output=True,text=True)
    assert dry.returncode==0 and json.loads(dry.stdout)['dry_run']
    assert not (tmp_path/'knowledge').exists()
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    output=json.loads(result.stdout)
    assert output['status']=='accepted'
    assert (tmp_path/output['appended']).is_file()
    assert record['title'] in (tmp_path/'ctf-web/INDEX.md').read_text()
    assert len((tmp_path/'knowledge/learning-ledger.jsonl').read_text().splitlines())==1
    again=subprocess.run(command,capture_output=True,text=True)
    assert json.loads(again.stdout)['status'] != 'accepted'
    assert len(list((tmp_path/'ctf-web/learned').glob('*.md')))==1

def test_failed_index_build_restores_existing_files(tmp_path,monkeypatch):
    category=tmp_path/'ctf-web';category.mkdir()
    catalog=category/'LEARNED.md';catalog.write_text('personal original\n')
    index=category/'INDEX.md';index.write_text('original index\n')
    source=tmp_path/'record.json';source.write_text(json.dumps(candidate()))
    import rebuild_indexes
    def fail(*args): raise OSError('planted index failure')
    monkeypatch.setattr(rebuild_indexes,'build_index',fail)
    with pytest.raises(OSError): append_record(tmp_path,source)
    assert catalog.read_text()=='personal original\n'
    assert index.read_text()=='original index\n'
    assert not list(category.glob('learned/*.md'))
    assert not (tmp_path/'knowledge/.learning.lock').exists()

def test_authored_sections_ignore_code_heading_and_parse_dimensions(tmp_path):
    directory=tmp_path/'ctf-web';directory.mkdir()
    (directory/'ref.md').write_text('# Reference\n## Byte parser\n**Prerequisite dimensions:** {"version":"3.1"}\n```python\n## Fake heading\n```\n')
    records=list(iter_learning_records(tmp_path))
    assert not any(item['title']=='Fake heading' for item in records)
    assert next(item for item in records if item['title']=='Byte parser')['variant_dimensions']=={'version':'3.1'}

def test_rejects_literal_flag_and_invalid_dimensions():
    record=candidate();record['verification_evidence']='ctf{synthetic-secret-value}'
    assert validate_record(record)
    record=candidate();record['variant_dimensions']={'arbitrary':'value'}
    assert validate_record(record)
