"""Stdlib metadata/hash checks for S030; not a mathematical proof replay."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
d=ROOT/'validation/S030'
p=json.loads((d/'PACKAGE.json').read_text())
for name,row in p['files'].items():
    data=(ROOT/name).read_bytes()
    assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],name
    if name.endswith('.gz'):gzip.decompress(data)
s=json.loads((d/'SUMMARY.json').read_text())
assert s['witness'] is None and not s['certified_strata'] and s['S11_m155_156']=='UNKNOWN'
assert all(s[k]=='NOT_RUN' for k in ('S10','S9','S8_unconditional_fallback'))
smoke=json.loads((d/'SMOKE.json').read_text())
assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==smoke['chromatic_cnf_byte_matches']==271
assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
ind=json.loads((d/'INDEPENDENT.json').read_text())
assert ind['status']=='PASS' and ind['exhaustive_n4_partition_controls']==2916
replay=json.loads((d/'SEARCH_REPLAY.json').read_text())
assert len(replay)==3 and all(r['status']=='PASS' and not r['exhaustion'] for r in replay)
assert sum(r['models_checked'] for r in replay)==s['sat_models']
assert (ROOT/'sessions/S030/EXECUTED_PROMPT.md').read_bytes()==(ROOT/'sessions/S029/S030_FUTURE_PROMPT.md').read_bytes()
state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
if state['last_completed_session']=='S030':
    assert state['recommended_next_session']=='S031'
    assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S030/S031_FUTURE_PROMPT.md').read_bytes()
manifest=json.loads((ROOT/'sessions/S030/MANIFEST.json').read_text())
for name,row in manifest['artifact_sha256'].items():
    data=(ROOT/name).read_bytes()
    assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],name
print('PASS S030 hashes, smoke receipt, independent control/replay records, prompt identity; metadata only')
