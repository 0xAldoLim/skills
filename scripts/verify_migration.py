#!/usr/bin/env python3
"""Verify immutable source inventory, section migration and audited reference prefixes."""
from __future__ import annotations
import hashlib
import json
import re
import zipfile
from pathlib import Path

def normalized(data: bytes) -> bytes:
    return data.replace(b'\r\n', b'\n')

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sections(text: str):
    starts=[];fence=None;offset=0
    for line in text.splitlines(keepends=True):
        mark=re.match(r'^\s*(`{3,}|~{3,})',line)
        if mark:
            fence=None if fence==mark[1][0] else (mark[1][0] if fence is None else fence)
        if not fence and line.startswith('## '):
            starts.append((offset,line.strip()))
        offset+=len(line)
    for i,(start,title) in enumerate(starts):
        yield title,text[start:starts[i+1][0] if i+1<len(starts) else len(text)]

def verify_v2(root: Path, manifest: dict) -> list[str]:
    errors=[]
    for entry in manifest['audited_metadata']:
        path=root/entry['path']
        if not path.is_file() or digest(normalized(path.read_bytes()))!=entry['sha256']:
            errors.append('audited migration metadata changed: '+entry['path'])
    archive=root/manifest['archive']['path']
    if not archive.is_file() or digest(archive.read_bytes())!=manifest['archive']['sha256']:
        errors.append('original baseline archive missing or altered')
        return errors
    mapping=json.loads((root/manifest['section_map']).read_text(encoding='utf-8'))
    files=json.loads((root/manifest['file_map']).read_text(encoding='utf-8'))
    baseline=json.loads((root/'knowledge/migration/baseline.json').read_text(encoding='utf-8'))
    expected={row['path'] for row in baseline['files']}
    actual={row['old_path'] for row in files}
    if actual!=expected or len(files)!=manifest['original_file_count']:
        errors.append('original file inventory is incomplete or duplicated')
    with zipfile.ZipFile(archive) as original:
        for row in files:
            if row['old_path'] not in original.namelist() or digest(original.read(row['old_path']))!=row['original_git_blob_sha256']:
                errors.append('source snapshot mismatch: '+row['old_path'])
            if not (root/row['destination']).is_file() or not row.get('reason') or row['status'] in {'missing','review-required'}:
                errors.append('unaccounted original file: '+row['old_path'])
        for row in mapping:
            source=normalized(original.read(row['old_path'])).decode('utf-8')
            matches=[body for title,body in sections(source) if title==row['heading'] and digest(body.encode())==row['original_text_sha256']]
            if len(matches)!=1:
                errors.append('original section provenance mismatch: '+row['heading'])
                continue
            destination=root/row['destination']
            if not destination.is_file():
                errors.append('missing section destination: '+row['destination'])
            elif row['status']=='relocated':
                if matches[0].strip() not in destination.read_text(encoding='utf-8'):
                    errors.append('relocated knowledge missing/altered: '+row['old_path']+' '+row['heading'])
            elif row['status'] not in {'corrected','superseded'} or not row.get('reason'):
                errors.append('unexplained section removal: '+row['heading'])
    for row in manifest['protected_files']:
        path=root/row['path'];length=row['protected_original_byte_length']
        if not path.is_file():
            errors.append('missing protected reference: '+row['path'])
            continue
        data=normalized(path.read_bytes())
        if len(data)<length or digest(data[:length])!=row['protected_prefix_sha256']:
            errors.append('audited reference prefix changed: '+row['path'])
    return errors
