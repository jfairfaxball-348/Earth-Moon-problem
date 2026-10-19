"""Package the S027 local campaign tree into validation/S027/local (no science).

Copies every record, log, certificate and proof; raw .cnf / .lemmas.json scratch
files are stored gzipped (byte-recoverable). The run lock and temp files are
skipped. Writes validation/S027/local/PACKAGE_MANIFEST.json with raw and stored
SHA-256 of every file.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'artifacts/tmp/S027-local'
DST = ROOT / 'validation/S027/local'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    if DST.exists():
        shutil.rmtree(DST)
    rows = []
    for p in sorted(SRC.rglob('*')):
        if not p.is_file() or p.name == 'RUN.lock' or '.tmp' in p.name:
            continue
        rel = p.relative_to(SRC)
        if p.name == 'minor.checkpoint.json.gz' and (p.parent / 'lemmas.json.gz').exists():
            continue  # certified graph: complete lemma record and DRAT supersede the cut checkpoint
        raw = p.read_bytes()
        gz = p.suffix in ('.cnf', '.drat') or p.name.endswith('.lemmas.json')
        out = DST / (str(rel) + ('.gz' if gz else ''))
        out.parent.mkdir(parents=True, exist_ok=True)
        data = gzip.compress(raw, 9, mtime=0) if gz else raw
        out.write_bytes(data)
        rows.append({'path': str(out.relative_to(ROOT)).replace('\\', '/'), 'raw_sha256': sha(raw),
                     'raw_bytes': len(raw), 'stored_sha256': sha(data), 'gzipped_by_packager': gz})
    (DST / 'PACKAGE_MANIFEST.json').write_text(json.dumps(rows, indent=0), newline='\n')
    print(len(rows), 'files packaged,', round(sum(r['raw_bytes'] for r in rows) / 2**20, 1), 'MiB raw')


if __name__ == '__main__':
    main()
