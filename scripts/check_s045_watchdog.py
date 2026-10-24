"""Portable repair receipt, archive and independent new-rule verification."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'validation/S045/watchdog_repair'
sys.path.insert(0,str(ROOT/'tools'))
from s045_verify import check_pair,check_colouring,partition_clause,geometric_journal

def read(name):return json.loads((V/name).read_text(encoding='utf-8'))
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    owner=read('OWNER_DIRECTIVE.json');reg=read('REGISTRATION.json');a=read('ACCEPTANCE.json')
    assert owner['deadline_epoch']==reg['deadline_epoch']==a['deadline_epoch']==1792913400
    assert owner['timezone']=='Europe/London' and owner['checkin_interval_hours']==2
    assert reg['domain_unchanged'] and (reg['benchmark_n'],reg['benchmark_k'],reg['benchmark_native_solve_seconds'])==(50,9,60)
    for p,h in reg['sha256'].items():assert digest(ROOT/p)==h,p
    assert a['status']=='PASS' and all(a[k]=='PASS' for k in ('smoke','native_controls','policy_controls','full_restart_benchmark'))
    assert len(a['source_sha256'])==9
    for p,h in a['source_sha256'].items():assert digest(ROOT/p)==h,p
    smoke=read('SMOKE.json');assert smoke['verdict']=='PASS'
    assert smoke['chromatic_rows_verified']==smoke['chromatic_cnf_byte_matches']==271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    native=read('CONTROLS.json');assert native['status']=='PASS' and native['exhaustive_n5']==1024 and native['fixed_layer_cases']==1026
    assert all(native[k] for k in ('padded50_positive','malformed_feedback_rejected','truncated_checkpoint_rejected','standalone_drat_verified','incremental_feedback','cooperative_stop'))
    policy=read('POLICY_CONTROLS.json');assert policy['status']=='PASS'
    assert all(policy[k] for k in ('slow_loading','first_cause_preserved','startup_ceiling','deadline_preparation','deadline_loading','deadline_solving','clock_rollback','compression_verified','duplicate_archive_recovery'))
    assert policy['source_sha256']==a['source_sha256']
    build=read('BUILD.json');assert build['status']=='PASS'
    for p,h in build['sha256'].items():
        if p.startswith(('tools/','tools\\','scripts/','scripts\\')):assert digest(ROOT/p.replace('\\','/'))==h,p
    original=read('INITIAL_SOURCES.json');assert original['commit']==reg['entry_commit']=='5d910fb86ecd2fdb3844051aaa01c63e4fb69442'
    for item in original['files'].values():assert digest(ROOT/item['archive'])==item['sha256']
    heartbeat=read('CHECKIN.json')
    assert heartbeat['status']=='ACTIVE' and heartbeat['kind']=='heartbeat' and heartbeat['rrule']=='FREQ=HOURLY;INTERVAL=2'
    assert heartbeat['id']==owner['checkin_automation_id'] and heartbeat['target_thread_id']
    preservation=read('PRESERVATION.json');assert preservation['status']=='PASS'
    assert (preservation['candidates'],preservation['geometric_cuts'])==(272374,900798)
    # Stream decoded bytes and CRC: no multi-gigabyte allocation, no alteration.
    for archive in sorted((V/'preserved').glob('*.gz')):
        seal=json.loads(Path(str(archive)+'.seal.json').read_text())
        assert seal['decoded_bytes_verified'] and digest(archive)==seal['archive_sha256']
        h=hashlib.sha256();size=0
        with gzip.open(archive,'rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block);size+=len(block)
        assert h.hexdigest()==seal['raw_sha256'] and size==seal['raw_bytes']
        if archive.name=='PLANARITY.lem.gz':assert h.hexdigest()==preservation['geometric_raw_sha256']
        else:assert h.hexdigest()==preservation['files'][archive.name[:-3]]['raw_sha256']
    b=read('RESTART_BENCHMARK.json')
    assert b['status']=='PASS' and b['state']=='SLICE_COMPLETE' and not b['error'] and not b['audit_pending']
    assert b['source_sha256']==a['source_sha256'] and b['native_startup_seconds']>15
    assert (b['new_candidates'],b['verified_geometric_cuts'])==(3587,924323)
    pairs=list(itertools.combinations(range(50),2));rows=0
    with gzip.open(V/'benchmark/CANDIDATES.jsonl.gz','rt',encoding='utf-8') as f:
        for line in f:
            r=json.loads(line);assert (r['n'],r['k'],r['mode'])==(50,9,'partition')
            check_pair(50,r['layers'],r['rotations']);check_colouring(50,r['layers'],r['colours'],9)
            bits=r['bits'];assert len(bits)==2450
            assert all([list(e) for i,e in enumerate(pairs) if bits[2*i+j]=='1']==r['layers'][j] for j in (0,1))
            clause=partition_clause(50,r['colours']);assert clause and all(bits[x-1]=='0' for x in clause)
            rows+=1
    assert rows==a['benchmark_new_candidates']==3587
    with tempfile.TemporaryDirectory() as temp:
        target=Path(temp)/'cuts.lem'
        target.write_bytes(gzip.decompress((V/'benchmark/new-cuts.lem.gz').read_bytes()))
        cuts=geometric_journal(target,50)
    assert cuts==a['benchmark_new_geometric_rules']==23525
    state=json.loads((ROOT/'authoritative/STATE.json').read_text())
    assert state['s036_closeout']['computation']=='STOPPED' and state['confirmed_classical_range']['lower']==9
    if state.get('active_session',{}).get('id')=='S045':
        assert state['active_session']['status']=='RUNNING' and state['s045_watchdog_repair']['status']=='ACCEPTED_RESTARTED'
        assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S045/EXECUTION_PROMPT.md').read_bytes()
    for p,h in read('MANIFEST.json')['sha256'].items():assert digest(ROOT/p)==h,p
    print(json.dumps(dict(status='PASS',preserved_candidate_bytes_verified=True,new_candidates_independently_checked=rows,new_geometric_rules_independently_checked=cuts,projected_coverage=None,witness=False)))

if __name__=='__main__':main()
