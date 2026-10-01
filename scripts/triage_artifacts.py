#!/usr/bin/env python3
"""Inventory artifact signatures and sampled entropy without executing anything."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path

MAGIC = [(b'\x7fELF','ELF'),(b'MZ','PE/DOS'),(b'PK\x03\x04','ZIP/container'),
         (b'\x89PNG\r\n\x1a\n','PNG'),(b'%PDF-','PDF'),(b'\xd4\xc3\xb2\xa1','PCAP LE'),
         (b'\xa1\xb2\xc3\xd4','PCAP BE'),(b'\x0a\x0d\x0d\x0a','PCAPNG'),
         (b'\x00asm','WASM'),(b'SQLite format 3\0','SQLite'),(b'\xd0\xcf\x11\xe0','OLE/Office')]


def inspect(path: Path, sample_bytes: int = 1048576, hash_file: bool = False) -> dict:
    with path.open('rb') as handle:
        sample = handle.read(sample_bytes)
    counts = collections.Counter(sample)
    entropy = -sum((count/len(sample))*math.log2(count/len(sample)) for count in counts.values()) if sample else 0
    result = {'path': str(path), 'size': path.stat().st_size, 'sampled_bytes': len(sample),
              'header_hex':sample[:32].hex(),'format':next((kind for magic,kind in MAGIC if sample.startswith(magic)),'unknown'),
              'sample_entropy_bits':round(entropy,3)}
    if hash_file:
        digest=hashlib.sha256()
        with path.open('rb') as handle:
            for block in iter(lambda:handle.read(1048576),b''): digest.update(block)
        result['sha256']=digest.hexdigest()
    return result


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path,nargs='?',default=Path.cwd())
    parser.add_argument('--sample-bytes',type=int,default=1048576)
    parser.add_argument('--hash',action='store_true')
    parser.add_argument('--recursive',action='store_true')
    parser.add_argument('--max-files',type=int,default=200)
    args=parser.parse_args()
    if not 1 <= args.sample_bytes <= 16777216 or not 1 <= args.max_files <= 10000:
        parser.error('sample budget 1..16777216; file budget 1..10000')
    paths=sorted(args.directory.rglob('*') if args.recursive else args.directory.iterdir())
    selected=[p for p in paths if p.is_file() and not p.is_symlink() and '.git' not in p.parts][:args.max_files]
    try:
        print(json.dumps([inspect(p,args.sample_bytes,args.hash) for p in selected],indent=2))
    except OSError as error:
        parser.error(str(error))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
