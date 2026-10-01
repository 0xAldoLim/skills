#!/usr/bin/env python3
"""Bounded scoped HTTP enumeration. TLS verified; no redirects; derived wordlists only."""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from instance_health import endpoint, http_observation


def apply_processing(payload: str, chain: list[tuple]) -> str | None:
    current=payload
    for kind,*args in chain:
        if kind=='prefix': current=args[0]+current
        elif kind=='suffix': current+=args[0]
        elif kind=='replace': current=re.sub(args[0],args[1],current)
        elif kind=='substring': current=current[int(args[0]):int(args[0])+int(args[1])]
        elif kind=='case': current={'upper':str.upper,'lower':str.lower,'title':str.title}[args[0]](current)
        elif kind=='encode': current={'url':lambda value:quote(value,safe=''),'html':html.escape,'base64':lambda value:base64.b64encode(value.encode()).decode(),'hex':lambda value:value.encode().hex()}[args[0]](current)
        elif kind=='decode': current={'url':unquote,'base64':lambda value:base64.b64decode(value,validate=True).decode()}[args[0]](current)
        elif kind=='hash': current=hashlib.new(args[0],current.encode()).hexdigest()
        elif kind=='skip':
            if re.search(args[0],current): return None
        else: raise ValueError('unsupported processing operation: '+kind)
    return current


def render(url: str, payload: str, raw: bool=False) -> str:
    return url.replace('FUZZ',payload if raw else quote(payload,safe=''))


def scoped_candidates(scope: dict, template: str, payloads: list[str], cap: int, raw: bool=False) -> list[str]:
    if scope.get('kind')!='challenge_instance': raise ValueError('scope must explicitly name a challenge_instance')
    target=endpoint(scope['target'])
    if target[0] not in {'http','https'}: raise ValueError('HTTP scope required')
    if 'FUZZ' not in template: raise ValueError('URL needs a FUZZ marker in its path/query')
    if 'FUZZ' in urlsplit(template).netloc:
        raise ValueError('FUZZ must be in the path/query, never the authority')
    candidates=[]
    for payload in payloads[:cap]:
        candidate=render(template,payload,raw)
        if endpoint(candidate)!=target: raise ValueError('payload/template leaves supplied origin')
        candidates.append(candidate)
    return candidates


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope',type=Path,required=True)
    parser.add_argument('--url',required=True)
    parser.add_argument('--wordlist',type=Path,required=True)
    parser.add_argument('--max-requests',type=int,default=100)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--rate',type=float,default=2,help='global requests/second')
    parser.add_argument('--timeout',type=float,default=3)
    parser.add_argument('--raw-payload',action='store_true',help='preserve already encoded payload exactly')
    parser.add_argument('--processing',default='[]',help='JSON array of operation arrays')
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    try:
        if not 1<=args.max_requests<=10000 or not 1<=args.workers<=16 or not 0<args.rate<=100 or not 0<args.timeout<=10:
            raise ValueError('invalid request/concurrency/rate/timeout budget')
        scope=json.loads(args.scope.read_text(encoding='utf-8'))
        chain=json.loads(args.processing)
        payloads=[]
        with args.wordlist.open(encoding='utf-8') as handle:
            for line in handle:
                value=apply_processing(line.rstrip('\r\n'),chain)
                if value is not None: payloads.append(value)
                if len(payloads)>=args.max_requests: break
        candidates=scoped_candidates(scope,args.url,payloads,args.max_requests,args.raw_payload)
        if args.dry_run:
            print(json.dumps({'requests':len(candidates),'origin':list(endpoint(scope['target'])),'workers':args.workers,'rate':args.rate},indent=2))
            return 0
        failures=0
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            # Batches bound queued work; launch spacing enforces global rate.
            for begin in range(0,len(candidates),args.workers):
                batch=[]
                for url in candidates[begin:begin+args.workers]:
                    batch.append(pool.submit(http_observation,url,args.timeout,None))
                    time.sleep(1/args.rate)
                for future in batch:
                    result=future.result()
                    print(json.dumps(result),flush=True)
                    failures=failures+1 if result.get('error') or result.get('proxy_marker') else 0
                    if result.get('status')==429 or failures>=2:
                        print('Stopping: rate limit or repeated instance failures; preserve state and recheck health',file=sys.stderr)
                        return 3
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
