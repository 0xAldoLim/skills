#!/usr/bin/env python3
"""Compare section concepts and bodies; a shared heading is never sufficient."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from lookup_knowledge import sections

def normalized(value: str) -> str:
    return ' '.join(re.findall(r'[a-z0-9]+', value.lower()))

def concepts(root: Path):
    for path in sorted(root.glob('ctf-*/*.md')):
        if path.name in {'SKILL.md', 'INDEX.md'}:
            continue
        for section in sections(path):
            if section['level'] > 1:
                yield {'title': section['title'], 'body': section['text'],
                       'category': path.parent.name, 'path': path.relative_to(root).as_posix()}

def compare(candidate, existing):
    pool = [item for item in existing if item['category'] == candidate['category']]
    body = candidate['body'].replace('\r\n','\n').strip()
    for item in pool:
        if body == item['body'].replace('\r\n','\n').strip():
            return item, 1.0, 'skipped', 'equivalent complete section body'
    wanted = set(normalized(body).split())
    def score(item):
        tokens = set(normalized(item['body']).split())
        return len(wanted & tokens) / len(wanted | tokens) if wanted | tokens else 0
    best = max(pool, key=score, default=None)
    similarity = score(best) if best else 0
    return best, similarity, 'inbox', 'review concept, primitive and version prerequisites; heading match alone does not establish equivalence'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', action='append', nargs=2, metavar=('NAME','PATH'), required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    local = list(concepts(args.root.resolve()))
    report = []
    for name, raw in args.source:
        source = Path(raw).resolve()
        commit = subprocess.check_output(['git','-c',f'safe.directory={source.as_posix()}','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        for candidate in concepts(source):
            neighbor, score, decision, reason = compare(candidate, local)
            report.append({'source_technique': candidate['title'], 'source_repository': name,
                'source_commit': commit, 'source_path': candidate['path'],
                'candidate_category': candidate['category'], 'existing_overlap': neighbor['path'] if neighbor else None,
                'duplicate_score': round(score,3), 'decision': decision, 'reason': reason,
                'source_section_sha256': hashlib.sha256(candidate['body'].encode()).hexdigest(), 'destination_file': None})
    destination = args.output or args.root / 'knowledge/generated-enrichment-scan.json'
    destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'wrote {len(report)} body-aware comparisons to {destination}')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
