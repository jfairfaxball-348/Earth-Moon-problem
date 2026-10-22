"""Portable paused-session integrity; no native code or fresh proof replay."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s035_archive_parts import resolve
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
s=read('authoritative/STATE.json');assert s['active_session']['status']=='PAUSED' and s['active_session']['owner_resume_required']
assert s['last_completed_session']=='S034' and not s['next_session_is_future_unexecuted']
assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S035/RESUME_PROMPT.md').read_bytes()
assert read('validation/S035/pause/SAT_AUDIT.json')['hits']==[]
nine=read('validation/S035/pause/NINE_REGIONS.json')['regions']
assert [x['id'] for x in nine]==[0,1,3,7,15,31,63,127,255]
assert all(x['status']=='UNKNOWN' and not x['pending_unsat_proof'] and not x['verification_backlog'] for x in nine)
a=read('validation/S035/pause/AUDIT.json');assert a['proof_closed_regions']==len(a['certificates'])==247 and a['formula_hashes_reconstructed']
assert not a['fresh_DRAT_replay'] and not a['processes_exited'] and not a['ram_CDCL_serialized']
receipt=read('validation/S035/pause/ARCHIVE_VERIFICATION.json');inv=read('validation/S035/pause/RUNTIME_INVENTORY.json')
archive=resolve(ROOT/'validation/S035/pause/runtime.tar.xz');assert archive.stat().st_size==receipt['archive_bytes'] and sha(archive)==receipt['archive_sha256']
assert receipt['status']=='PASS_ALL_ORIGINAL_OBJECT_BYTES_AND_GZIP_RECONSTRUCTION' and receipt['no_original_deleted']
assert sha(ROOT/inv['external_archive'])==inv['external_archive_sha256']
for c in a['certificates']:
    if any(row.get('decoded_sha256')==c['proof_sha256'] for row in inv['objects'].values()):continue
    assert any(row['sha256']==c['proof_sha256'] for row in inv['external_S034'].values()),c['cell']
deps=read('validation/S035/pause/DEPENDENCIES.json');assert sha(ROOT/'validation/S035/pause/dependencies.tar.xz')==deps['archive_sha256']
for name,row in read('validation/S035/pause/MANIFEST.json')['files'].items():
    p=resolve(ROOT/name);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
print('PASS S035 owner pause, SAT-first audit, nine UNKNOWN regions and durable verified archive; RAM is not a durable snapshot')
