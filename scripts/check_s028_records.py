"""S028 stdlib integrity/metadata audit; never a fresh scientific proof replay."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(b):
    return hashlib.sha256(b).hexdigest()


for r in json.loads((ROOT / 'validation/S028/local/PACKAGE_MANIFEST.json').read_text()):
    data = (ROOT / r['path']).read_bytes()
    assert sha(data) == r['stored_sha256'], r['path']
    raw = gzip.decompress(data) if r['gzipped_by_packager'] else data
    assert sha(raw) == r['raw_sha256'] and len(raw) == r['raw_bytes'], r['path']
env = json.loads((ROOT / 'validation/S028/local/ENVIRONMENT.json').read_text())
for name, expected in env['source_sha256'].items():
    snap = ROOT / 'validation/S028/source-bytes' / (expected + '.py.gz')
    assert sha(gzip.decompress(snap.read_bytes())) == expected, name
smoke = json.loads((ROOT / 'validation/S028/local/SMOKE.json').read_text())
assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == 271
replay = json.loads((ROOT / 'validation/S028/REPLAY.json').read_text())
assert replay['all_verified'] and replay['items'] == 29
summary = json.loads((ROOT / 'validation/S028/SUMMARY.json').read_text())
assert summary['witness'] is None and len(summary['closed_profiles']) == 16
state = json.loads((ROOT / 'authoritative/STATE.json').read_text(encoding='utf-8'))
if state['last_completed_session'] == 'S028':
    assert state['recommended_next_session'] == 'S029'
    assert (ROOT / 'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == \
        (ROOT / 'sessions/S028/S029_FUTURE_PROMPT.md').read_bytes()
for name, item in json.loads((ROOT / 'sessions/S028/MANIFEST.json').read_text())['artifact_sha256'].items():
    data = (ROOT / name).read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256'], name
print('PASS S028 package, source pins, smoke, 29-item replay record, state and identical S029 prompts')
print('Metadata/packaging only: no native proof replay or new mathematical computation')
