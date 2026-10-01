import hashlib
from triage_artifacts import inspect


def test_magic_outranks_filename_and_hash_is_complete(tmp_path):
    path = tmp_path / 'photo.jpg'
    data = b'\x7fELF' + b'x' * 10000
    path.write_bytes(data)
    result = inspect(path, sample_bytes=16, hash_file=True)
    assert result['format'] == 'ELF'
    assert result['sampled_bytes'] == 16
    assert result['size'] == len(data)
    assert result['sha256'] == hashlib.sha256(data).hexdigest()


def test_empty_and_uniform_artifacts(tmp_path):
    path = tmp_path / 'empty'
    path.write_bytes(b'')
    assert inspect(path)['sample_entropy_bits'] == 0
    path.write_bytes(b'a' * 256)
    assert inspect(path)['sample_entropy_bits'] == 0
