"""Portable integrity checks for S035 resident upgrade; no Windows execution or proof replay."""
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read('validation/S035/resident/MANIFEST.json')
for name,row in m['files'].items():
    p=ROOT/name;assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
cfg=read('validation/S035/resident/REGISTERED_CONFIG.json')
assert cfg['execution_revision']=='S035_RESIDENT_V2' and cfg['workers']==2 and cfg['deadline'] is None
assert cfg['resident_max_contexts']==4
assert cfg['resident_cache_private_bytes']<=5*1024**3 and cfg['rss_cap_kib']==6*1024*1024
for name,digest in cfg['source_sha256'].items():assert sha(ROOT/name)==digest,name
retained=read('validation/S035/resident/RETENTION_CONTROLS.json')
assert retained['status']=='PASS' and retained['same_pid_and_create_time_across_turns']
assert retained['original_delta_hashes_unchanged'] and retained['memory_eviction_kills_only_parked_identity']
assert retained['conflicts_after']>=retained['conflicts_before']>0
assert retained['native_sha256']==cfg['native_sha256']
controls=read('validation/S035/resident/SCHEDULER_CONTROLS.json')
assert controls['status']=='PASS' and controls['controller_kill_restart']=='PASS' and controls['read_only_status']
for name,digest in controls['source_sha256'].items():assert sha(ROOT/name)==digest,name
diag=read('validation/S035/resident/DIAGNOSTIC.json')
assert diag['status']=='PASS_DIAGNOSTIC_NOT_A_MATHEMATICAL_RESULT'
assert cfg['disable_congruence']==diag['disable_congruence']
assert read('validation/S035/pre-resident/ARCHIVE_VERIFICATION.json')['status']=='PASS_ALL_ORIGINAL_BYTES'
state=read('authoritative/STATE.json')
if state['last_completed_session']!='S034':  # S035 or later: historical S035 entry state
    state=read('validation/S035/closeout/ENTRY_STATE.json')
assert state['last_completed_session']=='S034' and state['active_session']['id']=='S035'
assert state['active_session']['status'] in ('RUNNING','PAUSED') and state['active_session']['no_automatic_S036']
assert state['active_session']['execution_revision']==cfg['execution_revision']
print('PASS S035 resident execution integrity; RAM retention and diagnostic evidence, not a mathematical result')
