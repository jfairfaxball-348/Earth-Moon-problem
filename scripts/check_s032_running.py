"""Validate active S032 launch package without inventing a session closeout."""
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
assert state['last_completed_session']=='S031' and state['active_session']['id']=='S032'
assert state['active_session']['status']=='IN_PROGRESS_LONG_RUN'
assert state['next_session_is_future_unexecuted'] is False
assert not state['standing_continuation_authorization']['successive_sessions_authorized']
assert state['standing_continuation_authorization']['authorized_session']=='S032'
assert (ROOT/'sessions/S032/EXECUTED_PROMPT.md').read_bytes()==(ROOT/'sessions/S031/S032_FUTURE_PROMPT.md').read_bytes()
m=json.loads((ROOT/'sessions/S032/START_MANIFEST.json').read_text())
for name,row in m['artifact_sha256'].items():
    p=ROOT/name;b=p.read_bytes()
    assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],name
    if name.endswith('.tar.gz'):
        with tarfile.open(p) as t:
            assert all(not x.name.startswith('/') and '..' not in Path(x.name).parts for x in t.getmembers())
    elif name.endswith('.gz'):gzip.decompress(b)
start=ROOT/'validation/S032/start'
s=json.loads((start/'SMOKE.json').read_text())
assert s['verdict']=='PASS' and s['chromatic_rows_verified']==s['chromatic_cnf_byte_matches']==271
assert s['k9']['verified'] and s['solver_roundtrip']['fresh_proof_verified']
c=json.loads((start/'NATIVE_CONTROLS.json').read_text())
assert c['status'] in ('PASS','SCOPED_PASS_WITH_FREE_K9_UNKNOWN')
assert c['exhaustive_n5_fixed_graphs']==1024 and c['random_n6_partitions']==64
d=json.loads((start/'DIAGNOSTIC_AUDIT.json').read_text())
assert d['status']=='PASS' and d['independently_checked_native_clauses']>0
assert not d['whole_stratum_certified'] and d['verdict']=='UNKNOWN'
assert not (ROOT/'sessions/S032/CLOSEOUT.md').exists()
print('PASS S032 running launch hashes, scoped controls/K9 UNKNOWN, diagnostic receipt and exact invocation; not completed-session CI')
