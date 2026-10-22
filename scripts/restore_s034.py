"""Portable, bounded-memory restoration of the S034 lossless runtime archive.

Default restores metadata, logs and semantic checkpoints, omitting large DRAT
files. --proofs restores those too. Original absolute paths inside JSON are
provenance; a new Windows controller must explicitly import/rebase them.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT/'validation/S034/campaign.tar.xz')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--proofs', action='store_true')
    args = parser.parse_args()
    inventory = json.loads((ROOT/'validation/S034/RUNTIME_INVENTORY.json').read_text())
    names = {'proof:'+v['proof_id']: k for k,v in inventory['files'].items() if 'proof_id' in v}
    assert not args.output.exists(), 'Choose a new destination; never overwrite a campaign'
    args.output.mkdir(parents=True)
    hashes, sizes = {}, {}
    with tarfile.open(args.archive, 'r|xz') as archive:
        for member in archive:
            data = archive.extractfile(member).read()
            if member.name == 'INVENTORY.json':
                assert json.loads(data) == inventory
                continue
            proof = member.name.startswith('proof-chunks/')
            if proof:
                _, file_id, offset = member.name.split('/')
                key = 'proof:'+file_id
                name = names[key]
                assert sizes.get(key,0) == int(offset)
            else:
                assert member.name.startswith('runtime/')
                key = name = member.name[8:]
            relative = PurePosixPath(name)
            assert not relative.is_absolute() and '..' not in relative.parts
            hashes.setdefault(key,hashlib.sha256()).update(data)
            sizes[key] = sizes.get(key,0)+len(data)
            if not proof or args.proofs:
                target = args.output.joinpath(*relative.parts)
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('ab' if proof else 'wb') as f:
                    f.write(data)
    for name,row in inventory['files'].items():
        key = 'proof:'+row['proof_id'] if 'proof_id' in row else name
        assert sizes[key] == row['bytes'] and hashes[key].hexdigest() == row['sha256'], name
    print('PASS all archived original bytes verified; restored', args.output,
          'including DRAT' if args.proofs else 'without large DRAT files')
    print('No worker launched; absolute JSON paths need explicit Windows import.')

if __name__ == '__main__':
    main()
