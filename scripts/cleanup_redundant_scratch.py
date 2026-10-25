"""Remove only scratch files identical to verified retained archive contents.

Maintenance only: no solver or research session is launched. The append-only
receipt records each removed path, hash, size and retained recovery source.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = (ROOT / 'artifacts/tmp').resolve()
OUT = ROOT / 'artifacts/maintenance/2026-10-25-cleanup'
CHUNK = 4 * 1024 * 1024


def digest(stream):
    h, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(CHUNK), b''):
        h.update(block)
        size += len(block)
    return size, h.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if '--compress' in sys.argv:
        compress_scratch()
        return
    retained = {}
    def register(size, sha, source):
        retained.setdefault(size, {})[sha] = source

    # Read compressed files to EOF (including gzip CRC checks), never trusting
    # old receipts alone. Keep every original archive.
    for p in ([] if '--s035' in sys.argv else sorted((ROOT / 'validation').rglob('*.gz'))):
        if p.name.endswith('.tar.gz'):
            continue
        with gzip.open(p, 'rb') as f:
            size, sha = digest(f)
        register(size, sha, {'archive': p.relative_to(ROOT).as_posix(),
                             'recovery': 'gzip decompression'})
    print('Verified gzip archives:', sum(len(v) for v in retained.values()), flush=True)

    sys.path.insert(0, str(ROOT / 'scripts'))
    from archive_s034 import verify
    archive = ROOT / 'validation/S034/campaign.tar.xz'
    if archive.exists() and '--s035' not in sys.argv:
        inventory = verify(archive)
        for name, row in inventory['files'].items():
            register(row['bytes'], row['sha256'], {
                'archive': archive.relative_to(ROOT).as_posix(),
                'member': name, 'recovery': 'scripts/restore_s034.py'})
        print('Verified complete S034 archive', flush=True)

    if '--s035' in sys.argv:
        from restore_s035_preserved import verify_stream
        archive = ROOT / 'validation/S035/pause/runtime.tar.xz'
        inventory = json.loads((archive.parent/'RUNTIME_INVENTORY.json').read_text())
        verify_stream(archive, inventory)
        for key, row in inventory['objects'].items():
            source = {'archive': archive.relative_to(ROOT).as_posix(),
                      'object': key, 'recovery': 'scripts/restore_s035_preserved.py'}
            register(row['bytes'], key, source)
            register(row['decoded_bytes'], row['decoded_sha256'],
                     dict(source, decoded=True))
        print('Verified complete S035 pause archive', flush=True)
        for p in (ROOT/'validation').rglob('*'):
            if p.is_file() and p.stat().st_size >= 1024*1024:
                with p.open('rb') as f:
                    size, sha = digest(f)
                register(size, sha, {'file': p.relative_to(ROOT).as_posix(),
                                     'recovery': 'retained identical file'})

    removed, freed = 0, 0
    receipt = OUT / 'REMOVED.jsonl'
    with receipt.open('a', encoding='utf-8') as log:
        for p in SCRATCH.rglob('*'):
            if p.is_symlink() or not p.is_file():
                continue
            size = p.stat().st_size
            if size < 1024 * 1024 or size not in retained:
                continue
            resolved = p.resolve(strict=True)
            if not resolved.is_relative_to(SCRATCH):
                raise RuntimeError(f'Outside scratch: {p}')
            before = p.stat()
            with p.open('rb') as f:
                actual_size, sha = digest(f)
            source = retained[size].get(sha)
            if source is None:
                continue
            after = p.stat()
            assert actual_size == size and before.st_mtime_ns == after.st_mtime_ns
            row = dict(path=p.relative_to(ROOT).as_posix(), bytes=size,
                       sha256=sha, retained=source, time=time.time())
            log.write(json.dumps(dict(event='VERIFIED_BEFORE_DELETE', **row))+'\n')
            log.flush()
            p.unlink()
            log.write(json.dumps(dict(event='REMOVED', **row))+'\n')
            log.flush()
            removed += 1
            freed += size
            if removed % 100 == 0:
                print('Removed', removed, 'files;', round(freed/2**30, 2), 'GiB', flush=True)
    summary = dict(files_removed=removed, bytes_freed=freed,
                   scope='Only >=1MiB scratch files hash-matching verified retained archives',
                   receipt=str(receipt))
    suffix = '-s035' if '--s035' in sys.argv else ''
    (OUT/f'SUMMARY{suffix}.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary), flush=True)


def compress_scratch():
    """Keep a lossless compressed copy of large, stopped-run text scratch."""
    count, saved = 0, 0
    with (OUT/'COMPRESSED.jsonl').open('a', encoding='utf-8') as log:
        for p in SCRATCH.rglob('*'):
            if p.is_symlink() or not p.is_file():
                continue
            if p.suffix not in {'.drat', '.cnf', '.inst', '.lem', '.json', '.jsonl', '.txt'}:
                continue
            before = p.stat()
            if before.st_size < 10*1024*1024:
                continue
            assert p.resolve(strict=True).is_relative_to(SCRATCH)
            dest = p.with_name(p.name+'.cleanup.gz')
            if dest.exists():
                continue
            with p.open('rb') as f:
                size, sha = digest(f)
            with p.open('rb') as source, dest.open('xb') as output:
                with gzip.GzipFile(fileobj=output, mode='wb', compresslevel=1, mtime=0) as zipped:
                    for block in iter(lambda: source.read(CHUNK), b''):
                        zipped.write(block)
            with gzip.open(dest, 'rb') as f:
                assert digest(f) == (size, sha)
            if dest.stat().st_size >= size:
                dest.unlink()
                continue
            assert p.stat().st_mtime_ns == before.st_mtime_ns
            row = dict(path=p.relative_to(ROOT).as_posix(), bytes=size, sha256=sha,
                       retained=dest.relative_to(ROOT).as_posix(),
                       compressed_bytes=dest.stat().st_size,
                       recovery='gzip decompress retained to original path')
            log.write(json.dumps(dict(event='VERIFIED_BEFORE_DELETE', **row))+'\n')
            log.flush()
            p.unlink()
            log.write(json.dumps(dict(event='COMPRESSED', **row))+'\n')
            log.flush()
            count += 1
            saved += size-dest.stat().st_size
            if count % 25 == 0:
                print('Compressed', count, 'files; saved', round(saved/2**30, 2), 'GiB', flush=True)
    summary = dict(files_compressed=count, bytes_freed=saved)
    (OUT/'SUMMARY-compression.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
