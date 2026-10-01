import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path
import pytest
from pwn_payloads import ret2libc
ROOT=Path(__file__).resolve().parents[1]

def test_measured_ret2libc_addresses_and_alignment():
    payload=ret2libc(24,0x401123,0x402555,0x7f001234,0x401000)
    assert payload[:24]==b'A'*24
    assert struct.unpack('<QQQQ',payload[24:])==(0x401000,0x401123,0x402555,0x7f001234)
    for offset in [-1,1000001]:
        with pytest.raises(ValueError): ret2libc(offset,1,2,3)
    with pytest.raises(ValueError): ret2libc(0,-1,2,3)

@pytest.mark.parametrize('args',[['srop','--register','rip=0x401000','--register','rsp=0x404000'],['fmtstr','--offset','6','--write','0x404000=0x41'],['shellcraft'],['orw','--path','/tmp/fixture','--buffer','0x404800']])
def test_optional_pwntools_payload_generation_only(args):
    if os.name!='posix': pytest.skip('pwntools assembler workflow requires native Linux')
    pytest.importorskip('pwn')
    if args[0] in {'orw','shellcraft'} and not shutil.which('as'): pytest.skip('GNU assembler missing')
    result=subprocess.run([sys.executable,str(ROOT/'scripts/pwn_payloads.py'),*args],capture_output=True,text=True,timeout=20)
    assert result.returncode==0,result.stderr
    payload=bytes.fromhex(result.stdout.strip())
    assert payload
    if args[0]=='srop':
        # Linux amd64 rt_sigreturn frame: ucontext + sigcontext ABI offsets.
        assert struct.unpack_from('<Q',payload,0xa8)[0]==0x401000
        assert struct.unpack_from('<Q',payload,0xa0)[0]==0x404000
    elif args[0]=='fmtstr':
        assert struct.pack('<Q',0x404000) in payload
