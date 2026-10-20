"""Stdlib integrity/governance checks; does not replay mathematical proofs."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def verify(rows):
    for name,row in rows.items():
        data=(ROOT/name).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],name
        if name.endswith('.gz'):gzip.decompress(data)


verify(json.loads((ROOT/'validation/S031/PACKAGE.json').read_text())['files'])
verify(json.loads((ROOT/'sessions/S031/MANIFEST.json').read_text())['artifact_sha256'])
verify(json.loads((ROOT/'sessions/S031/START_MANIFEST.json').read_text())['artifact_sha256'])
d=ROOT/'validation/S031'
s=json.loads((d/'SUMMARY.json').read_text())
r=json.loads((d/'SEARCH_REPLAY.json').read_text())
c=json.loads((d/'CONTROLLER.json').read_text())
assert s['sat_models']==r['models_checked']==46 and s['cuts']==r['cuts_checked']==1809
assert r['status']=='PASS' and r['chronological_assignment_checks'] and r['final_formula_regenerated']
assert r['each_model_has_two_checked_nonplanar_layers'] and not r['whole_stratum_certified']
assert s['S11_m155_156']=='UNKNOWN' and s['witness'] is None and not s['certified_strata']
assert all(s[k]=='NOT_RUN' for k in ('S10','S9','S8_unconditional_fallback'))
assert c['worker_process']['returncode']==0 and c['worker_process']['completed_process']
assert c['sleep_inhibition_released'] and c['worker_result']['status']=='WALL_CAPPED'
assert c['worker_process']['peak_tree_rss_kib']<c['memory_cap_kib']
for name,h in c['source_sha256'].items():
    archived=d/'start/source-bytes'/(h+'.py.gz')
    assert hashlib.sha256(gzip.decompress(archived.read_bytes())).hexdigest()==h,name
smoke=json.loads((d/'start/SMOKE.json').read_text())
assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==smoke['chromatic_cnf_byte_matches']==271
assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
controls=json.loads((d/'start/CONTROLS.json').read_text())
assert controls['status']=='PASS' and controls['persistent_n4_assignments']==2916
assert (ROOT/'sessions/S031/EXECUTED_PROMPT.md').read_bytes()==(ROOT/'sessions/S030/S031_FUTURE_PROMPT.md').read_bytes()
state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
if state['last_completed_session']=='S031':
    assert state['recommended_next_session']=='S032' and state['next_session_is_future_unexecuted']
    assert 'active_session' not in state
    assert state['standing_continuation_authorization']['successive_sessions_authorized'] is False
    assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S031/S032_FUTURE_PROMPT.md').read_bytes()
print('PASS S031 archived hashes, smoke/controls/replay receipts, UNKNOWN boundaries and future prompt; metadata only')
