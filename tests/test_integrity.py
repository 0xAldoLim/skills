from pathlib import Path
import json
import shutil

import pytest

from verify_append_only import verify


ROOT = Path(__file__).resolve().parents[1]


def test_original_inventory_migration_and_audited_prefixes() -> None:
    assert verify(ROOT, ROOT / "knowledge" / "integrity-manifest.json") == []


@pytest.fixture
def migration_copy(tmp_path):
    destination = tmp_path / 'repository'
    shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns('.git', '__pycache__', '.pytest_cache', '.ruff_cache'))
    return destination


def test_personal_knowledge_tampering_is_detected(migration_copy):
    path = migration_copy / 'ctf-pwn/personal-learnings.md'
    path.write_text(path.read_text(encoding='utf-8').replace('## ', '## ALTERED ', 1), encoding='utf-8')
    errors = verify(migration_copy, migration_copy / 'knowledge/integrity-manifest.json')
    assert any('relocated knowledge missing/altered' in error for error in errors)
    assert any('audited reference prefix changed' in error for error in errors)


def test_deleted_inventory_entry_is_detected(migration_copy):
    path = migration_copy / 'knowledge/migration/file-map.json'
    rows = json.loads(path.read_text(encoding='utf-8'))
    path.write_text(json.dumps(rows[1:]), encoding='utf-8')
    errors = verify(migration_copy, migration_copy / 'knowledge/integrity-manifest.json')
    assert any('metadata changed' in error for error in errors)
    assert any('inventory is incomplete' in error for error in errors)


def test_append_and_line_ending_normalization_preserve_integrity(migration_copy):
    path = migration_copy / 'ctf-pwn/personal-learnings.md'
    content = path.read_text(encoding='utf-8') + '\n## Local appended method\nReproducible addition.\n'
    path.write_bytes(content.replace('\n', '\r\n').encode())
    assert verify(migration_copy, migration_copy / 'knowledge/integrity-manifest.json') == []
