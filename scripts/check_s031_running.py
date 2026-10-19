"""Validate the IN_PROGRESS handoff without fabricating closeout invariants."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
assert state['last_completed_session']=='S030' and state['active_session']['id']=='S031'
assert state['active_session']['status']=='IN_PROGRESS_LONG_RUN'
assert state['next_session_is_future_unexecuted'] is False
assert state['standing_continuation_authorization']['successive_sessions_authorized'] is False
assert state['standing_continuation_authorization']['decision']=='D066'
assert (ROOT/'sessions/S031/EXECUTED_PROMPT.md').read_bytes()==(ROOT/'sessions/S030/S031_FUTURE_PROMPT.md').read_bytes()
manifest=json.loads((ROOT/'sessions/S031/START_MANIFEST.json').read_text())
for name,row in manifest['artifact_sha256'].items():
    b=(ROOT/name).read_bytes()
    assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],name
start=ROOT/'validation/S031/start'
smoke=json.loads((start/'SMOKE.json').read_text());controls=json.loads((start/'CONTROLS.json').read_text())
assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==smoke['chromatic_cnf_byte_matches']==271
assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
assert controls['status']=='PASS' and controls['persistent_n4_assignments']==2916
for p in (ROOT/'sessions/S031').glob('CLOSEOUT*'):
    raise AssertionError('S031 is still running; do not claim a closeout')
print('PASS S031 running state, standing authorization, source/launch manifests, fresh gate and controls; not a completed session')
