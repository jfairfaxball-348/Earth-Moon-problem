"""S027 stdlib integrity/metadata audit; never a fresh scientific proof replay."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(b):
    return hashlib.sha256(b).hexdigest()


rows = json.loads((ROOT / 'validation/S027/local/PACKAGE_MANIFEST.json').read_text())
for r in rows:
    data = (ROOT / r['path']).read_bytes()
    assert sha(data) == r['stored_sha256'], r['path']
    raw = gzip.decompress(data) if r['gzipped_by_packager'] else data
    assert sha(raw) == r['raw_sha256'] and len(raw) == r['raw_bytes'], r['path']

env = json.loads((ROOT / 'validation/S027/local/ENVIRONMENT.json').read_text())
for name, expected in env['source_sha256'].items():
    snap = ROOT / 'validation/S027/source-bytes' / (expected + '.py.gz')
    assert sha(gzip.decompress(snap.read_bytes())) == expected, name

smoke = json.loads((ROOT / 'validation/S027/local/SMOKE.json').read_text())
assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']

summary = json.loads((ROOT / 'validation/S027/SUMMARY.json').read_text())
replay = json.loads((ROOT / 'validation/S027/REPLAY.json').read_text())
assert replay['all_verified'] and replay['items'] == 19
assert summary['c5_sum17_certified'] == 24 and summary['iff_complete'] is False
assert summary['source']['closed_profiles_drat'] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 17, 25]
assert summary['source']['closed_blocking_dependencies'] == 0 and summary['witness'] is None
for d in sorted((ROOT / 'validation/S027/local/source').glob('profile*')):
    cp = d / 'domain.certificate.json'
    if cp.exists():
        c = json.loads(cp.read_text())
        assert c['verdict'] == 'UNSAT_DRAT_VERIFIED' and 's VERIFIED' in c['checker_tail']
        proof = gzip.decompress((d / 'domain.drat.gz').read_bytes())
        assert sha(proof) == c['drat_sha256']
        assert sha(gzip.decompress((d / 'domain.cnf.gz').read_bytes())) == c['cnf_sha256']

state = json.loads((ROOT / 'authoritative/STATE.json').read_text(encoding='utf-8'))
if state['last_completed_session'] == 'S027':
    assert state['recommended_next_session'] == 'S028'
    assert (ROOT / 'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == \
        (ROOT / 'sessions/S027/S028_FUTURE_PROMPT.md').read_bytes()
manifest = json.loads((ROOT / 'sessions/S027/MANIFEST.json').read_text())
for name, item in manifest['artifact_sha256'].items():
    data = (ROOT / name).read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256'], name
print(f'PASS S027 package ({len(rows)} files), source pins, smoke, 19-item replay record, '
      'domain certificate hashes, state and identical S028 prompts')
print('Metadata/packaging only: no native proof replay or new mathematical computation')
