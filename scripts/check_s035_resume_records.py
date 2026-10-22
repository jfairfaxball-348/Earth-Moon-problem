"""Portable S035 recovery integrity; historical pause and current authority differ.

The original pause checker and all pause manifest bytes stay immutable. This
successor validates that evidence while accepting an explicitly invoked S035
continuation. It never launches a native worker or replays a mathematical proof.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s035_archive_parts import resolve


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


state = read('authoritative/STATE.json')
assert state['last_completed_session'] == 'S034'
assert state['active_session']['id'] == 'S035'
assert state['active_session']['status'] in ('RUNNING', 'PAUSED')
assert state['active_session']['no_automatic_S036']
assert state['next_session_is_future_unexecuted'] is False
assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S035/RESUME_PROMPT.md').read_bytes()
entry = read('validation/S035/resume/ENTRY.json')
assert entry['entry_main'] == '3118649b248b9045d48b408074b2dc77901b7d2c'
assert entry['owner_invocation'] and entry['S036_authorized'] is False
assert read('validation/S035/resume/ENTRY_STATE.json')['active_session']['status'] == 'PAUSED'

for name, row in read('validation/S035/pause/MANIFEST.json')['files'].items():
    path = resolve(ROOT/name)
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], name
pause_audit = read('validation/S035/pause/AUDIT.json')
assert pause_audit['proof_closed_regions'] == len(pause_audit['certificates']) == 247
assert pause_audit['formula_hashes_reconstructed'] and not pause_audit['fresh_DRAT_replay']
assert not pause_audit['processes_exited'] and not pause_audit['ram_CDCL_serialized']
nine = read('validation/S035/pause/NINE_REGIONS.json')['regions']
assert [r['id'] for r in nine] == [0,1,3,7,15,31,63,127,255]
assert all(r['status'] == 'UNKNOWN' and not r['pending_unsat_proof'] and not r['verification_backlog'] for r in nine)
receipt = read('validation/S035/pause/ARCHIVE_VERIFICATION.json')
inventory = read('validation/S035/pause/RUNTIME_INVENTORY.json')
archive = resolve(ROOT/'validation/S035/pause/runtime.tar.xz')
assert archive.stat().st_size == receipt['archive_bytes'] and sha(archive) == receipt['archive_sha256']
assert receipt['status'] == 'PASS_ALL_ORIGINAL_OBJECT_BYTES_AND_GZIP_RECONSTRUCTION' and receipt['no_original_deleted']
assert sha(ROOT/inventory['external_archive']) == inventory['external_archive_sha256']
for certificate in pause_audit['certificates']:
    if any(r.get('decoded_sha256') == certificate['proof_sha256'] for r in inventory['objects'].values()):
        continue
    assert any(r['sha256'] == certificate['proof_sha256'] for r in inventory['external_S034'].values())
dependencies = read('validation/S035/pause/DEPENDENCIES.json')
assert sha(ROOT/'validation/S035/pause/dependencies.tar.xz') == dependencies['archive_sha256']
assert read('validation/S035/resume/audit/SAT_RESCAN.json')['hits'] == []
assert read('validation/S035/resume/SAT_CONTROLS.json')['status'] == 'PASS'
assert read('validation/S035/resume/audit/VALIDATOR_CONTROLS.json')['status'] == 'PASS'

manifest = read('validation/S035/resume/MANIFEST.json')
for name, row in manifest['files'].items():
    path = ROOT/name
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], name
print('PASS S035 invoked recovery and immutable pause evidence; no fresh proof replay or headline advance')
