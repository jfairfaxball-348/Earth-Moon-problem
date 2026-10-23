"""Portable closeout/recovery integrity, not fresh mathematical proof replay."""
import hashlib
import json
from pathlib import Path
import tarfile
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/S035/closeout'
sys.path.insert(0,str(ROOT/'tools'))
from s035_archive_parts import resolve
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

state=read(ROOT/'authoritative/STATE.json')
assert state['last_completed_session']=='S035' and state['recommended_next_session']=='S036'
assert state['next_session_is_future_unexecuted'] and not state.get('active_session')
assert state['s035_closeout']['S036_executed'] is False
prompt=(ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()
assert prompt==(ROOT/'sessions/S035/S036_FUTURE_PROMPT.md').read_bytes()
assert b'FUTURE / UNEXECUTED' in prompt and b'PermissionError' in prompt and b'SAT FIRST' in prompt
assert state['confirmed_classical_range']['lower']==9 and state['confirmed_classical_range']['upper']==12
audit=read(OUT/'AUDIT.json')
assert len(audit['certificates'])==audit['proof_closed_regions']==247
assert audit['formula_hashes_reconstructed'] and not audit['fresh_DRAT_replay']
assert read(OUT/'SAT_RESCAN.json')['hits']==[]
snapshot=read(OUT/'PROCESS_SNAPSHOT.json')
assert len(snapshot['processes'])==12 and snapshot['all_original_threads_suspended']
assert all(p['cpu_delta']==0 and all(t['suspend_count']>0 for t in p['threads']) for p in snapshot['processes'])
assert snapshot['private_cdcl_serialized'] is False
contexts=read(OUT/'CONTEXTS.json')
assert contexts['unresolved_ids']==[0,1,3,7,15,31,63,127,255]
assert sorted(c['cell'] for c in contexts['contexts'])==[0,7,127,255]
prefixes=read(OUT/'PREFIX_AUDIT.json')
assert all(p['status']=='INDEPENDENT_SUBDIVISION_AUDIT_PASS' for p in prefixes['prefixes'])
receipt=read(OUT/'DELTA_VERIFICATION.json');inventory=read(OUT/'DELTA_INVENTORY.json')
archive=resolve(OUT/'runtime-delta.tar.xz')
assert receipt['status']=='PASS_ACTUAL_RESTORE_ALL_DELTA_FILE_HASHES' and receipt['no_original_deleted']
assert not receipt['ram_state_in_archive']
assert archive.stat().st_size==receipt['archive_bytes'] and sha(archive)==receipt['archive_sha256']
assert sha(ROOT/inventory['base_inventory'])==inventory['base_inventory_sha256']
base=read(ROOT/inventory['base_inventory'])
seen=set()
with tarfile.open(archive,'r:xz') as tf:
    for m in tf:
        assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
        row=inventory['files'][m.name];assert row['storage']=='CLOSEOUT_DELTA' and row['bytes']==m.size
        h=hashlib.sha256()
        with tf.extractfile(m) as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        assert h.hexdigest()==row['sha256'];assert m.name not in seen;seen.add(m.name)
assert len(seen)==receipt['changed_files']
for name,row in inventory['files'].items():
    if row['storage']=='BASE_PAUSE_ARCHIVE':assert {k:row[k] for k in ('bytes','sha256')}==base['files'][name]
    elif row['storage']=='EXTERNAL_S034_ARCHIVE':assert all(row[k]==base['external_S034'][name][k] for k in ('bytes','sha256'))
    elif row['storage']=='CLOSEOUT_DELTA':assert name in seen
    else:assert name=='pre-resident-runtime.tar.gz' and row['sha256']==base['original_preupgrade_container']['sha256']
assert b'PermissionError' in (OUT/'resume-control/watcher-sustained.log').read_bytes()
assert read(OUT/'resume-control/GUARD_PAUSE.json')['reason']=='WATCHER_FAILURE'
for name,row in read(OUT/'MANIFEST.json')['files'].items():
    p=ROOT/name;assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
print('PASS S035 closed UNKNOWN, SAT-first preserved identities, exact delta/base recovery, S036 prompt; not fresh proof replay')
