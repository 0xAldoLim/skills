#!/usr/bin/env python3
"""Offline Poly1305/RFC AEAD serialization diagnostic; not constant-time crypto."""
from __future__ import annotations
import argparse
import json
import struct
P = 2**130 - 5
MASK = 0x0ffffffc0ffffffc0ffffffc0fffffff

def poly1305_tag(one_time_key: bytes, message: bytes) -> bytes:
    if len(one_time_key) != 32:
        raise ValueError('one-time key must be 32 bytes')
    r = int.from_bytes(one_time_key[:16], 'little') & MASK
    s = int.from_bytes(one_time_key[16:], 'little')
    accumulator = 0
    for offset in range(0, len(message), 16):
        block = message[offset:offset+16]
        coefficient = int.from_bytes(block, 'little') + 2**(8*len(block))
        accumulator = (accumulator + coefficient) * r % P
    return ((accumulator+s) % 2**128).to_bytes(16, 'little')

def aead_mac_data(aad: bytes, ciphertext: bytes) -> bytes:
    if len(aad) >= 2**64 or len(ciphertext) >= 2**64:
        raise ValueError('length does not fit RFC 64-bit field')
    return aad + b'\0'*(-len(aad)%16) + ciphertext + b'\0'*(-len(ciphertext)%16) + struct.pack('<QQ',len(aad),len(ciphertext))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key-hex',required=True)
    parser.add_argument('--message-hex',required=True)
    parser.add_argument('--aad-hex',help='if supplied, wrap message as RFC AEAD ciphertext data')
    args=parser.parse_args()
    try:
        message=bytes.fromhex(args.message_hex)
        if args.aad_hex is not None:
            message=aead_mac_data(bytes.fromhex(args.aad_hex),message)
        print(json.dumps({'tag_hex':poly1305_tag(bytes.fromhex(args.key_hex),message).hex(),'mac_data_bytes':len(message)}))
    except ValueError as error:
        parser.error(str(error))
    return 0
if __name__=='__main__':
    raise SystemExit(main())
