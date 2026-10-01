#!/usr/bin/env python3
"""Extract ZIP/TAR data into an empty output directory with path/size/link guards."""
from __future__ import annotations

import argparse
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath


def destination(root: Path, name: str) -> Path:
    posix=PurePosixPath(name.replace('\\','/'))
    if posix.is_absolute() or '..' in posix.parts or not posix.parts or any(':' in part for part in posix.parts):
        raise ValueError('unsafe archive path: '+name)
    result=root.joinpath(*posix.parts)
    if not result.resolve().is_relative_to(root.resolve()): raise ValueError('archive path escapes output directory')
    return result


def extract(source: Path, output: Path, max_files: int=1000, max_bytes: int=100*1024*1024) -> int:
    if output.exists() and any(output.iterdir()): raise ValueError('output directory must be empty')
    opener=zipfile.ZipFile if zipfile.is_zipfile(source) else tarfile.open
    with opener(source) as archive:
        members=archive.infolist() if isinstance(archive,zipfile.ZipFile) else archive
        plans=[]; total=0; seen=set()
        for member in members:
            if len(plans) >= max_files: raise ValueError('archive member count exceeds budget')
            is_zip=isinstance(archive,zipfile.ZipFile)
            name=member.filename if is_zip else member.name
            target=destination(output,name)
            if target in seen: raise ValueError('duplicate archive path: '+name)
            seen.add(target)
            if is_zip:
                mode=member.external_attr>>16
                if stat.S_ISLNK(mode): raise ValueError('archive symlinks are refused')
                size=member.file_size; directory=member.is_dir()
            else:
                if not member.isfile() and not member.isdir(): raise ValueError('archive links/devices are refused')
                size=member.size; directory=member.isdir()
            total+=size
            if size < 0: raise ValueError('negative archive member size')
            if total>max_bytes: raise ValueError('archive expanded size exceeds budget')
            plans.append((member,target,directory,size))
        regular_files = {target for _,target,directory,_ in plans if not directory}
        for _,target,_,_ in plans:
            if any(parent in regular_files for parent in target.parents):
                raise ValueError('archive file/directory hierarchy collision')
        # Validate every member before writing any file.
        output.mkdir(parents=True,exist_ok=True)
        actual=0
        for member,target,directory,size in plans:
            if directory: target.mkdir(parents=True,exist_ok=True); continue
            target.parent.mkdir(parents=True,exist_ok=True)
            reader=archive.open(member) if isinstance(archive,zipfile.ZipFile) else archive.extractfile(member)
            with reader, target.open('xb') as writer:
                remaining=size
                while remaining:
                    data=reader.read(min(65536,remaining))
                    if not data: raise ValueError('archive member shorter than declared size')
                    writer.write(data); actual+=len(data); remaining-=len(data)
                    if actual>max_bytes: raise ValueError('actual expanded data exceeds budget')
                if reader.read(1): raise ValueError('archive member larger than declared size')
        return actual


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--max-files',type=int,default=1000)
    parser.add_argument('--max-bytes',type=int,default=100*1024*1024)
    args=parser.parse_args()
    if args.max_files<=0 or args.max_bytes<=0: parser.error('budgets must be positive')
    try:
        print('Extracted bytes:',extract(args.source,args.output,args.max_files,args.max_bytes))
        return 0
    except (ValueError,OSError,tarfile.TarError,zipfile.BadZipFile,RuntimeError) as error:
        parser.error(str(error))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
