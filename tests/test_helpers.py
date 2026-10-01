import importlib.util
import json
import tarfile
import zipfile
from pathlib import Path

import pytest
from crypto_helpers import integer_root, crt, common_modulus, parity_recover, bsgs, reused_ecdsa_nonce
from extract_archive import extract
from instance_health import endpoint, scoped_urls, assess
from install_tools import selected_packages
from lookup_knowledge import search, sections

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bounded_fuzz', ROOT/'ctf-web/scripts/async_fuzz.py')
fuzz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fuzz)


@pytest.mark.parametrize('degree', [1, 2, 3, 7, 17])
def test_exact_roots_and_neighbor(degree):
    number = 123456789 ** degree
    assert integer_root(number, degree) == (123456789, True)
    if degree > 1:
        assert integer_root(number - 1, degree) == (123456788, False)
    assert integer_root(0, degree) == (0, True)


def test_general_crt():
    assert crt([2, 3, 2], [3, 5, 7]) == (23, 105)
    assert crt([2, 6], [4, 8]) == (6, 8)
    assert crt([0, 0], [1, 1]) == (0, 1)
    with pytest.raises(ValueError):
        crt([1, 2], [2, 4])


def test_common_modulus_and_noninvertible_factor():
    n, m = 101 * 113, 1234
    assert common_modulus(n, 3, 7, pow(m,3,n), pow(m,7,n)) == m
    with pytest.raises(ValueError, match='coprime'):
        common_modulus(n, 3, 9, 1, 1)
    with pytest.raises(ValueError, match='factor'):
        common_modulus(n, 3, 7, pow(101,3,n), pow(101,7,n))


@pytest.mark.parametrize('message', [0, 1, 2, 5, 1234, 11412])
def test_parity_oracle_exact_intervals(message):
    n, e = 101*113, 17
    d = pow(e, -1, 100*112)
    assert parity_recover(n,e,pow(message,e,n),lambda c: pow(c,d,n)&1) == message
    with pytest.raises(ValueError):
        parity_recover(n,e,2,lambda c: 'odd')


def test_discrete_log_budget_and_absent_subgroup():
    assert bsgs(2,pow(2,37,101),101,100) == 37
    assert bsgs(4,3,7,3) is None
    with pytest.raises(ValueError, match='budget'):
        bsgs(2,4,101,10**12)


def test_nonce_recovery_equations():
    q,k,d,r = 101,17,42,13
    h1,h2 = 31,77
    s1=(h1+r*d)*pow(k,-1,q)%q
    s2=(h2+r*d)*pow(k,-1,q)%q
    assert reused_ecdsa_nonce(q,r,s1,s2,h1,h2)==(k,d)


@pytest.mark.parametrize('name', ['../escape','/absolute','C:/evil','..\\escape'])
def test_archive_preflight_rejects_paths_without_writes(tmp_path,name):
    source=tmp_path/'bad.zip'
    with zipfile.ZipFile(source,'w') as z:
        z.writestr('valid',b'ok');z.writestr(name,b'bad')
    output=tmp_path/'out'
    with pytest.raises(ValueError): extract(source,output)
    assert not output.exists()


def test_archive_budget_symlink_collision_and_success(tmp_path):
    source=tmp_path/'data.zip'
    with zipfile.ZipFile(source,'w') as z: z.writestr('folder/file',b'hello')
    with pytest.raises(ValueError,match='budget'): extract(source,tmp_path/'large',max_bytes=4)
    assert extract(source,tmp_path/'ok') == 5
    assert (tmp_path/'ok/folder/file').read_bytes()==b'hello'
    with zipfile.ZipFile(source,'w') as z:
        z.writestr('a',b'file');z.writestr('a/b',b'other')
    with pytest.raises(ValueError,match='collision'): extract(source,tmp_path/'collision')
    assert not (tmp_path/'collision').exists()
    tar=tmp_path/'link.tar'
    with tarfile.open(tar,'w') as t:
        info=tarfile.TarInfo('link');info.type=tarfile.SYMTYPE;info.linkname='../escape';t.addfile(info)
    with pytest.raises(ValueError,match='links'): extract(tar,tmp_path/'links')


@pytest.mark.parametrize('target', ['https://user:pass@example.org','tcp://*.example.org:80','10.0.0.0/24','tcp://example.org:70000'])
def test_scope_refuses_ambiguous_target(target):
    with pytest.raises(ValueError): endpoint(target)


def test_health_budget_origin_and_infrastructure():
    scope={'kind':'challenge_instance','target':'https://target.example:444/a'}
    assert len(scoped_urls(scope,['/b','/c']))==3
    for routes in [['https://other.example/a'],['//target.example:445/a'],['/a','/b','/c']]:
        with pytest.raises(ValueError): scoped_urls(scope,routes)
    with pytest.raises(ValueError): scoped_urls({'kind':'platform','target':scope['target']},[])


def test_expiry_is_evidence_driven():
    proxy={'status':404,'proxy_marker':True,'error':None}
    assert assess([proxy])[0]=='inconclusive'
    assert assess([proxy,proxy])[0]=='likely-unavailable'
    assert assess([proxy,{'expected_marker':True,'status':404}])[0]=='application-reachable'
    assert assess([{'status':500},{'status':404}])[0]=='inconclusive'
    assert assess([{'connected':True,'sampled_bytes':0}])[0]=='inconclusive'
    assert assess([{'error':'tls'},{'error':'tls'}])[0]=='inconclusive'
    assert assess([{'error':'ConnectionRefusedError'}]*2)[0]=='likely-unavailable'


def test_fuzz_preserves_encoding_and_budget():
    scope={'kind':'challenge_instance','target':'https://target.example:444/'}
    assert fuzz.scoped_candidates(scope,'https://target.example:444/FUZZ',['%2f','x'],1,True)==['https://target.example:444/%2f']
    assert fuzz.render('https://target.example/FUZZ','%2f')=='https://target.example/%252f'
    with pytest.raises(ValueError): fuzz.scoped_candidates(scope,'https://FUZZ/',['evil.example'],1,True)
    assert fuzz.apply_processing('abc',[['prefix','x'],['encode','hex']])=='78616263'
    assert fuzz.apply_processing('abc',[['skip','b']]) is None


def test_heavy_is_explicit_even_with_all():
    manifest=json.loads((ROOT/'scripts/tool_manifest.json').read_text())
    apt,python=selected_packages(manifest,['all'])
    assert 'torch' not in python and 'sagemath' not in apt
    apt,python=selected_packages(manifest,['all','heavy'])
    assert 'torch' in python and 'sagemath' in apt
    with pytest.raises(ValueError): selected_packages(manifest,['no-such-tier'])


def test_lookup_reaches_late_sections_excludes_code(tmp_path):
    directory=tmp_path/'ctf-web';directory.mkdir()
    path=directory/'reference.md'
    path.write_text('# Reference\n\n## Early\nfoo\n```python\n## Fake heading\n```\n## Late quirk\nneedle namespace parser\n')
    assert 'Fake heading' not in [s['title'] for s in sections(path)]
    results=search(tmp_path,'namespace needle','ctf-web',2)
    assert results[0]['title']=='Late quirk' and results[0]['line']==8
