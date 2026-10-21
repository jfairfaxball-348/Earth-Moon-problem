"""Portable S032 archive integrity checks; not fresh native/proof replay."""
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[1]


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def verify(rows):
    for name,row in rows.items():
        p=ROOT/name
        assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
        if name.endswith('.tar.gz'):
            with tarfile.open(p) as archive:
                for member in archive:
                    assert not member.name.startswith('/') and '..' not in Path(member.name).parts


verify(json.loads((ROOT/'validation/S032/PACKAGE.json').read_text())['files'])
verify(json.loads((ROOT/'sessions/S032/MANIFEST.json').read_text())['artifact_sha256'])
verify(json.loads((ROOT/'sessions/S032/START_MANIFEST.json').read_text())['artifact_sha256'])
s=json.loads((ROOT/'validation/S032/SUMMARY.json').read_text())
a=json.loads((ROOT/'validation/S032/stopped/CAMPAIGN_AUDIT.json').read_text())
c=json.loads((ROOT/'validation/S032/stopped/CONTROLLER.json').read_text())
cp=json.loads((ROOT/'validation/S032/stopped/CHECKPOINT.json').read_text())
assert s['status']=='COMPLETED_OWNER_STOP_UNKNOWN' and c['worker_result']['stop_reason']=='OWNER_STOP'
assert c['sleep_inhibition_released'] and a['status']=='PASS' and a['bijective_renaming_checked']
assert s['retained_geometric_rules']==a['independently_checked_native_clauses']==cp['complete_lemma_lines']==2579937
assert s['diagnostic_seed_rules']+s['campaign_new_rules']==s['retained_geometric_rules']
assert not cp['native_cdcl_state_saved'] and cp['omitted_incomplete_tail_bytes']==0
h=hashlib.sha256();count=size=0
with gzip.open(ROOT/'validation/S032/stopped/learned.lem.gz','rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):
        h.update(b);count+=b.count(b'\n');size+=len(b)
assert h.hexdigest()==a['lemma_sha256']==s['lemma_sha256']==cp['lemma_sha256']
assert count==s['retained_geometric_rules'] and size==s['lemma_bytes']==cp['complete_lemma_bytes']
assert s['S11_m155_156']=='UNKNOWN' and not s['certified_strata'] and s['witness'] is None
assert all(s[k]=='NOT_RUN' for k in ['S10','S9','S8_unconditional_fallback'])
assert s['monitor_status']=='PAUSED' and s['no_automatic_resume']
controls=json.loads((ROOT/'validation/S032/rebuild/CONTROLS.json').read_text())
assert controls['status']=='PASS' and controls['exhaustive_n5']==1024
assert controls['native_sha256']==s['rebuilt_native_sha256'] and controls['damaged_proof_rejected']
for name in ['coverage','coverage-base']:
    report=json.loads((ROOT/f'validation/S032/rebuild/{name}-REPORT.json').read_text())
    ledger=json.loads((ROOT/f'validation/S032/rebuild/{name}-coverage.json').read_text())
    assert report['proof_closed_regions']==1 and report['total_regions']==256
    assert sum(int(cell['weight']) for cell in ledger['cells'])==int(report['encoded_region_weight'])
    assert report['mathematical_verdict']=='UNKNOWN'
assert (ROOT/'sessions/S032/EXECUTED_PROMPT.md').read_bytes()==(ROOT/'sessions/S031/S032_FUTURE_PROMPT.md').read_bytes()
assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S032/S033_FUTURE_PROMPT.md').read_bytes()
state=json.loads((ROOT/'authoritative/STATE.json').read_text())
if state['last_completed_session']=='S032':
    assert state['recommended_next_session']=='S033' and state['next_session_is_future_unexecuted']
    assert 'active_session' not in state and not state['standing_continuation_authorization']['successive_sessions_authorized']
print('PASS S032 preserved rules/archive hashes, UNKNOWN boundaries, rebuilt controls and paired future prompt; integrity only, not fresh proof replay')
