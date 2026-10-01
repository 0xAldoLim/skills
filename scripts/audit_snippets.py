#!/usr/bin/env python3
"""Syntax-audit Markdown Python examples without executing artifact or source code."""
from __future__ import annotations
import argparse
import ast
import collections
import json
import re
from pathlib import Path

def audit(root: Path) -> list[dict]:
    rows=[]
    for path in sorted(root.glob('ctf-*/*.md')):
        lines=path.read_text(encoding='utf-8').splitlines()
        fence=None;body=[];start=0;language=''
        for line_number,line in enumerate(lines,1):
            marker=re.match(r'^\s*(`{3,}|~{3,})([^\n]*)$',line)
            if marker and fence is None:
                fence=(marker[1][0],len(marker[1]));language=marker[2].strip().lower();body=[];start=line_number
            elif marker and marker[1][0]==fence[0] and len(marker[1])>=fence[1]:
                if language in {'python','py','python3','sage'}:
                    text='\n'.join(body)
                    row={'path':path.relative_to(root).as_posix(),'line':start,'language':language}
                    if language=='sage':
                        row['status']='sage_runtime_required'
                    else:
                        try:
                            ast.parse(text)
                            row['status']='syntax_valid_context_required'
                        except SyntaxError as error:
                            row.update(status='syntax_error',error=str(error))
                    rows.append(row)
                fence=None
            elif fence:
                body.append(line)
    return rows

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    rows=audit(args.root.resolve())
    report={'scope':'Python/Sage fenced examples in category references; parsing is not runtime reproduction',
        'counts':dict(collections.Counter(row['status'] for row in rows)),'snippets':rows}
    if args.output:
        args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'counts':report['counts'],'syntax_errors':[row for row in rows if row['status']=='syntax_error']},indent=2))
    return int(any(row['status']=='syntax_error' for row in rows))
if __name__=='__main__':
    raise SystemExit(main())
