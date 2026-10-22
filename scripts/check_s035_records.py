"""Portable S035 launch evidence integrity. Does not run Windows code or certify exhaustion."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s035_archive_parts import resolve
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read('sessions/S035/RUNNING_MANIFEST.json')
assert manifest['status'] in ('RUNNING_NOT_CLOSED','PAUSED_NOT_CLOSED')
for name,row in manifest['files'].items():
    p=resolve(ROOT/name);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
smoke=read('validation/S035/SMOKE.json');native=read('validation/S035/NATIVE_CONTROLS.json')
assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==smoke['chromatic_cnf_byte_matches']==271
assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
assert native['exhaustive_n5_fixed_graphs']==1024 and native['K33']==native['positive24']=='PASS'
audit=read('validation/S035/INPUT_AUDIT.json');imported=read('validation/S035/IMPORT_AUDIT.json')
assert audit['status']=='PASS' and audit['independently_checked_native_clauses']==2579937 and audit['bijective_renaming_checked']
assert imported['status']=='PASS' and imported['clauses']==93047 and len(imported['proofs'])==16
assert all(r['status']=='FRESH_WINDOWS_DRAT_VERIFIED' for r in imported['proofs'])
controls=read('validation/S035/SCHEDULER_CONTROLS.json')
assert controls['status']=='PASS' and controls['controller_kill_restart']=='PASS' and controls['damaged_proof_rejected'] and controls['read_only_status']
for name,digest in controls['source_sha256'].items():assert sha(ROOT/name)==digest,name
cfg=read('validation/S035/REGISTERED_CONFIG.json')
assert cfg['session']=='S035' and cfg['workers'] in (2,3) and cfg['deadline'] is None
assert cfg['native_sha256']==controls['native_sha256']==native['native_sha256']
assert cfg['variables']==17976 and cfg['base_clauses']==336030
assert cfg['disk_reserve_bytes']>=10*1024**3 and cfg['concurrency_increase_validated']
for name,digest in cfg['source_sha256'].items():assert sha(ROOT/name)==digest,name
bench=read('validation/S035/BENCHMARKS.json');concurrency=read('validation/S035/SOLVER_CONCURRENCY.json')
assert bench['status']=='PASS' and [r['workers'] for r in bench['rows']]==[1,2,3]
assert all(r['registered_wall_seconds']==120 for r in bench['rows'])
assert concurrency[str(cfg['workers'])]['solvers']>=2
state=read('authoritative/STATE.json')
assert state['last_completed_session']=='S034' and state['active_session']['id']=='S035' and state['active_session']['status'] in ('RUNNING','PAUSED')
assert state['next_session_is_future_unexecuted'] is False
assert (ROOT/'sessions/S035/EXECUTED_PROMPT.md').read_bytes()==(ROOT/'sessions/S034/S035_FUTURE_PROMPT.md').read_bytes()
print('PASS S035 fresh Windows acceptance, replay and real multiworker launch evidence; not a closeout, search exhaustion or headline advance')
