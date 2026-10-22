"""Exercise the real Windows fd-limit failure and exact gzip restoration."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'scripts'))
from restore_s035_preserved import verify_stream

area = Path(tempfile.mkdtemp(prefix='S035-restore-control-', dir=ROOT/'artifacts/tmp'))
inventory = dict(zlib_version=zlib.ZLIB_VERSION, objects={})
originals = {}
raws = {}
for i in range(10000):
    raw = ('fd-limit-control-%05d' % i).encode()
    key = hashlib.sha256(raw).hexdigest()
    originals[key] = raws[key] = raw
    inventory['objects'][key] = dict(bytes=len(raw), encoding='identity', decoded_bytes=len(raw), decoded_sha256=key)
for i in range(4):
    raw = (('gzip-member-%d-' % i)*5000).encode()
    original = gzip.compress(raw, compresslevel=1, mtime=0)
    key = hashlib.sha256(original).hexdigest()
    originals[key] = original; raws[key] = raw
    inventory['objects'][key] = dict(bytes=len(original), encoding='gzip-deflate-1',
                                    header=original[:10].hex(), footer=original[-8:].hex(),
                                    decoded_bytes=len(raw), decoded_sha256=hashlib.sha256(raw).hexdigest())
archive = area/'control.tar.xz'
with tarfile.open(archive, 'w:xz') as tf:
    # Interleaving forces many simultaneous hash/zlib states, but needs only
    # one destination handle. The old Windows writer failed around8192.
    for offset in range(0, max(map(len, raws.values())), 4096):
        for key, raw in raws.items():
            if offset >= len(raw):
                continue
            data = raw[offset:offset+4096]
            member = tarfile.TarInfo('objects/%s/%d' % (key, offset))
            member.size = len(data); tf.addfile(member, io.BytesIO(data))
    data = json.dumps(inventory).encode()
    member = tarfile.TarInfo('INVENTORY.json'); member.size = len(data)
    tf.addfile(member, io.BytesIO(data))
assert verify_stream(archive, inventory, area/'objects') == 10004
for key, original in originals.items():
    assert (area/'objects'/key).read_bytes() == original
duplicate_rejected = False
try:
    verify_stream(archive, inventory, area/'objects')
except AssertionError:
    duplicate_rejected = True
assert duplicate_rejected
damaged = json.loads(json.dumps(inventory))
damaged['objects'][next(iter(damaged['objects']))]['decoded_sha256'] = '0'*64
corrupt_rejected = False
try:
    verify_stream(archive, damaged)
except AssertionError:
    corrupt_rejected = True
assert corrupt_rejected
result = dict(status='PASS', objects=10004, exact_gzip_members=4,
              refused_existing_root=duplicate_rejected, damaged_inventory_rejected=corrupt_rejected,
              controls_retained=str(area), process_actions='NONE')
Path(__file__).with_name('STREAM_CONTROL.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
