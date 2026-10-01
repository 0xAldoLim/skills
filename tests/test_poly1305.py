import struct
import pytest
from poly1305_helper import aead_mac_data, poly1305_tag

def test_rfc8439_poly1305_known_answer():
    key=bytes.fromhex('85d6be7857556d337f4452fe42d506a80103808afb0db2fd4abff6af4149f51b')
    assert poly1305_tag(key,b'Cryptographic Forum Research Group').hex()=='a8061dc1305136c6c22b8baf0c0127a9'

def test_padding_lengths_and_empty_message():
    assert aead_mac_data(b'A'*17,b'C')==b'A'*17+b'\0'*15+b'C'+b'\0'*15+struct.pack('<QQ',17,1)
    assert aead_mac_data(b'',b'')==bytes(16)
    assert poly1305_tag(bytes(range(32)),b'')==bytes(range(16,32))
    with pytest.raises(ValueError):poly1305_tag(b'bad',b'')
