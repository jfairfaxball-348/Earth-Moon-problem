"""Restore exact S035 pause bytes with bounded open file handles on Windows.

The frozen restore_s035_pause/archive_s035_pause sources remain byte-identical.
This adapter replaces only their object writer: hashes, gzip reconstruction,
new-directory refusal, S034 proof restore, and all byte gates remain in force.
It never launches a campaign process.
"""
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import restore_s035_pause as frozen


def verify_stream(archive, inventory, output=None):
    """Reconstruct original bytes, closing the destination after each chunk."""
    assert zlib.ZLIB_VERSION == inventory['zlib_version'] == '1.3.1'
    target = Path(output) if output else None
    if target:
        assert not target.exists(), 'Never overwrite a prior recovery object root'
        target.mkdir(parents=True)
    states = {}
    inventory_seen = False
    with tarfile.open(archive, 'r|xz') as tf:
        for member in tf:
            assert member.isfile()
            if member.name == 'INVENTORY.json':
                assert not inventory_seen
                assert json.loads(tf.extractfile(member).read()) == inventory
                inventory_seen = True
                continue
            prefix, key, offset = member.name.split('/')
            assert prefix == 'objects' and len(key) == 64
            assert all(c in '0123456789abcdef' for c in key)
            row = inventory['objects'][key]
            if key not in states:
                state = dict(size=0, raw=hashlib.sha256(), original=hashlib.sha256())
                assert row['encoding'] in ('identity', 'gzip-deflate-1')
                header = b''
                if row['encoding'] == 'gzip-deflate-1':
                    state['z'] = zlib.compressobj(1, zlib.DEFLATED, -15)
                    header = bytes.fromhex(row['header'])
                    state['original'].update(header)
                states[key] = state
                if target:
                    with (target/key).open('xb') as dest:
                        dest.write(header)
            state = states[key]
            assert state['size'] == int(offset)
            data = tf.extractfile(member).read()
            state['size'] += len(data)
            assert state['size'] <= row['decoded_bytes']
            state['raw'].update(data)
            encoded = state['z'].compress(data) if 'z' in state else data
            state['original'].update(encoded)
            if target:
                with (target/key).open('ab') as dest:
                    dest.write(encoded)
    assert inventory_seen and len(states) == len(inventory['objects'])
    for key, row in inventory['objects'].items():
        state = states[key]
        if 'z' in state:
            end = state['z'].flush() + bytes.fromhex(row['footer'])
            state['original'].update(end)
            if target:
                with (target/key).open('ab') as dest:
                    dest.write(end)
        assert state['size'] == row['decoded_bytes'], key
        assert state['raw'].hexdigest() == row['decoded_sha256'], key
        assert state['original'].hexdigest() == key, key
        if target:
            assert (target/key).stat().st_size == row['bytes'], key
    return len(states)


def main():
    manifest = json.loads((ROOT/'validation/S035/pause/MANIFEST.json').read_text())
    for name in ('scripts/archive_s035_pause.py', 'scripts/restore_s035_pause.py'):
        row = manifest['files'][name]
        assert (ROOT/name).stat().st_size == row['bytes']
        assert frozen.digest(ROOT/name) == row['sha256'], 'Frozen recovery source changed: '+name
    frozen.verify = verify_stream
    frozen.main()


if __name__ == '__main__':
    main()
