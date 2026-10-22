"""Losslessly archive stopped S034, interleaving proof chunks for solid compression.

No solver is run and no runtime file is modified. The archive is independently
stream-read and every original file's size/SHA256 checked before publication.
"""
import hashlib
import io
import json
import lzma
from pathlib import Path
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT/'artifacts/tmp/S034/campaign'
OUT = ROOT/'validation/S034'
TARGET = OUT/'campaign.tar.xz'
CHUNK = 1024*1024

def add(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    info.mtime = 0
    tar.addfile(info, io.BytesIO(data))

def verify(path):
    hashes, sizes, inventory = {}, {}, None
    with tarfile.open(path, 'r|xz') as tar:
        for member in tar:
            data = tar.extractfile(member).read()
            if member.name == 'INVENTORY.json':
                inventory = json.loads(data)
                continue
            if member.name.startswith('proof-chunks/'):
                _, file_id, offset = member.name.split('/')
                key = 'proof:'+file_id
                assert sizes.get(key, 0) == int(offset)
            else:
                assert member.name.startswith('runtime/')
                key = member.name[8:]
            hashes.setdefault(key, hashlib.sha256()).update(data)
            sizes[key] = sizes.get(key, 0)+len(data)
    assert inventory is not None
    for name, row in inventory['files'].items():
        key = 'proof:'+row['proof_id'] if 'proof_id' in row else name
        assert sizes[key] == row['bytes'], name
        assert hashes[key].hexdigest() == row['sha256'], name
    assert len(hashes) == len(inventory['files'])
    return inventory

def main():
    stopped = json.loads((AREA/'STOPPED.json').read_text())
    assert stopped['status'] == 'STOPPED'
    assert not stopped['progress']['active']
    files = sorted(p for p in AREA.rglob('*') if p.is_file())
    proofs = [p for p in files if p.name == 'proof.drat']
    inventory = dict(format='S034_SOLID_PROOF_CHUNKS_V1', chunk_bytes=CHUNK,
                     runtime_prefix=str(AREA), files={})
    start = time.monotonic()
    with lzma.open(TARGET.with_suffix('.part'), 'wb', preset=3) as compressed, tarfile.open(fileobj=compressed, mode='w|') as tar:
        for p in files:
            if p in proofs:
                continue
            data = p.read_bytes()
            name = p.relative_to(AREA).as_posix()
            inventory['files'][name] = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            add(tar, 'runtime/'+name, data)
        handles = [p.open('rb') for p in proofs]
        digests = [hashlib.sha256() for p in proofs]
        lengths = [0 for p in proofs]
        try:
            for offset in range(0, max(p.stat().st_size for p in proofs), CHUNK):
                for i, handle in enumerate(handles):
                    data = handle.read(CHUNK)
                    if not data:
                        continue
                    digests[i].update(data)
                    lengths[i] += len(data)
                    add(tar, f'proof-chunks/{i:04d}/{offset:012d}', data)
                if offset % (16*CHUNK) == 0:
                    print('archived proof offset', offset, 'seconds', round(time.monotonic()-start), flush=True)
        finally:
            for handle in handles:
                handle.close()
        for i, p in enumerate(proofs):
            inventory['files'][p.relative_to(AREA).as_posix()] = dict(
                bytes=lengths[i], sha256=digests[i].hexdigest(), proof_id=f'{i:04d}')
        add(tar, 'INVENTORY.json', json.dumps(inventory, sort_keys=True, indent=2).encode()+b'\n')
    temporary = TARGET.with_suffix('.part')
    assert verify(temporary) == inventory
    temporary.replace(TARGET)
    (OUT/'RUNTIME_INVENTORY.json').write_text(json.dumps(inventory, indent=2)+'\n')
    print('PASS lossless runtime archive', TARGET.stat().st_size, 'bytes;', len(files), 'files', flush=True)

if __name__ == '__main__':
    main()
