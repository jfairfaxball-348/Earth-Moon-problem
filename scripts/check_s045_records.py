"""Portable S045 acceptance/evidence checker; counts never imply coverage."""
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s045_verify import check_pair,check_colouring,geometric_journal,partition_clause
V=ROOT/'validation/S045'

def read(p):return json.loads((V/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    started=time.process_time()
    reg=read('REGISTRATION.json')
    assert (reg['vertices'],reg['pairs'],reg['production_wall_ceiling_seconds'])==(50,1225,28800)
    assert all(reg[k] is None for k in ('independence_restriction','degree_restriction','symmetry_restriction','exact_edges'))
    for p,h in reg['sha256'].items():assert sha(ROOT/p)==h,p
    smoke=read('SMOKE.json')
    assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==smoke['chromatic_cnf_byte_matches']==271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    controls=read('CONTROLS.json')
    assert controls['status']=='PASS' and controls['exhaustive_n5']==1024 and controls['fixed_layer_cases']==1026
    assert len(controls['rows'])==1026 and sum(not r['expected_planar'] for r in controls['rows'])==2
    assert all(controls[k] for k in ('padded50_positive','malformed_feedback_rejected','truncated_checkpoint_rejected',
               'standalone_drat_verified','incremental_feedback','cooperative_stop'))
    assert controls['partition_truth_table_cases']==64*3**4
    for p,h in controls['stop_test']['source_sha256'].items():assert sha(ROOT/p.replace('\\','/'))==h,p
    build=read('BUILD.json');assert build['status']=='PASS'
    for p,h in build['sha256'].items():
        if p.startswith(('tools/','tools\\','scripts/','scripts\\')):assert sha(ROOT/p.replace('\\','/'))==h,p
    assert read('ENVIRONMENT.json')['entry_state_sha256']==sha(V/'ENTRY_STATE.json')
    streaming=read('STREAMING_ACCEPTANCE.json')
    assert streaming['status']=='PASS' and streaming['rows']==38042 and streaming['exact_cnf_byte_match']
    assert streaming['rejected_schema_fields']==['k','n','mode','partial']
    for suffix,key in [('cnf','cnf_sha256'),('drat','proof_sha256')]:
        assert hashlib.sha256(gzip.decompress((V/f'K4-non3.{suffix}.gz').read_bytes())).hexdigest()==controls[key]
    b=read('BENCHMARK.json');assert b['status']=='PASS' and len(b['arms'])==3
    eligible=[r for r in b['arms'] if r['mode']=='partition' and r['state']=='SLICE_COMPLETE' and r['new_candidates']>0]
    best=max(eligible,key=lambda r:(r['new_candidates']/r['elapsed_seconds'],not r['positive_phases']))
    assert b['selected_arm']==best['arm'] and b['positive_phases']==best['positive_phases']
    assert all(r['state']=='SLICE_COMPLETE' and r['new_candidates']>0 and not r['error'] for r in b['arms'])
    assert b['restart']['state']=='SLICE_COMPLETE' and b['restart']['new_candidates']>0
    assert not b['counts_are_coverage'] and not b['witness'] and not b['domain_excluded']
    total=0;cuts=0
    with tempfile.TemporaryDirectory() as temp:
        for arm in b['arms']:
            directory=V/b.get('archive_directory','benchmark')/arm['arm']
            rows=[json.loads(line) for line in gzip.decompress((directory/'CANDIDATES.jsonl.gz').read_bytes()).decode().splitlines()]
            expected=arm['new_candidates']+(b['restart']['new_candidates'] if arm['arm']==b['selected_arm'] else 0)
            assert len(rows)==expected
            for r in rows:
                assert r['n']==50 and r['k']==9 and r['mode']==arm['mode']
                check_pair(50,r['layers'],r['rotations']);check_colouring(50,r['layers'],r['colours'],9)
                xs=partition_clause(50,r['colours']);assert xs and len(xs)==len(set(xs))
                pairs=list(it.combinations(range(50),2));bits=r['bits'];assert len(bits)==2450
                assert all([[list(e) for i,e in enumerate(pairs) if bits[2*i+j]=='1']==r['layers'][j] for j in (0,1)])
                # A valid colouring falsifies its own learned partition clause.
                assert all(bits[x-1]=='0' for x in xs)
            target=Path(temp)/'cuts.lem'
            target.write_bytes(gzip.decompress((directory/'PLANARITY.lem.gz').read_bytes()))
            count=geometric_journal(target,50)
            assert count==(b['restart']['verified_geometric_cuts'] if arm['arm']==b['selected_arm'] else arm['verified_geometric_cuts'])
            total+=len(rows);cuts+=count
    state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
    if state.get('active_session',{}).get('id')=='S045':
        assert state['active_session']['status']=='RUNNING' and not state['next_session_is_future_unexecuted']
        assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S045/EXECUTION_PROMPT.md').read_bytes()
    assert state['s036_closeout']['computation']=='STOPPED' and state['confirmed_classical_range']['lower']==9
    manifest=V/'MANIFEST.json'
    if manifest.exists():
        for p,h in read('MANIFEST.json')['sha256'].items():assert sha(ROOT/p)==h,p
    print(json.dumps(dict(status='PASS',benchmark_candidates=total,geometric_rules=cuts,
                         projected_graph_coverage=None,witness=False,cpu_seconds=time.process_time()-started)))

if __name__=='__main__':main()
