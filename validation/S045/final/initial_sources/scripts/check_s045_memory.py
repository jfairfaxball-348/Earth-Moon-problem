"""Portable verification of resource recycling, preserved evidence and new rules."""
import gzip,hashlib,itertools,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'validation/S045/memory_recycle'
sys.path.insert(0,str(ROOT/'tools'))
from s045_verify import check_pair,check_colouring,partition_clause,geometric_journal
def read(p):return json.loads((V/p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def main():
    reg=read('REGISTRATION.json');a=read('ACCEPTANCE.json');b=read('RESTART_BENCHMARK.json');pres=read('PRESERVATION.json')
    assert reg['domain_unchanged'] and reg['deadline_epoch']==a['deadline_epoch']==1792913400
    assert a['soft_private_bytes']==reg['soft_private_bytes']==int(2.5*2**30)
    assert a['hard_private_bytes']==reg['hard_private_bytes']==3*2**30
    assert a['status']==b['status']==pres['status']=='PASS'
    assert b['state']=='SLICE_COMPLETE' and b['new_candidates']>0 and not b['error'] and not b['audit_pending']
    assert b['reason'] in ('NATIVE_TIMEOUT','MEMORY_RECYCLE') and b['peak_private_bytes']<a['hard_private_bytes']
    assert b['input_candidates']==pres['candidates']==453656
    assert b['source_journals']==pres['source_sha256']
    old_rows=0
    for p,h in pres['source_sha256'].items():
        name=p.replace('\\','/').split('/')[-1]
        archive=ROOT/'validation/S045/watchdog_repair/preserved'/name if name=='CANDIDATES.jsonl.gz' else V/'preserved'/name
        assert sha(archive)==h,p
        with gzip.open(archive,'rb') as f:old_rows+=sum(1 for _ in f)
    assert old_rows==453656
    for p,h in a['source_sha256'].items():assert sha(ROOT/p)==h,p
    amendment=read('UNSAT_GATE_AMENDMENT.json')
    assert amendment['status']=='PASS' and amendment['current_source_sha256']==a['source_sha256']
    assert amendment['benchmark_source_sha256']==b['source_sha256']==a['benchmark_source_sha256']
    added=b"        if p.returncode==20:\n            guard=latch_stop(out,'NATIVE_UNSAT_UNCERTIFIED',stage=stage)\n"
    driver=(ROOT/'tools/s045_driver.py').read_bytes();assert driver.count(added)==1
    assert hashlib.sha256(driver.replace(added,b'',1)).hexdigest()==b['source_sha256']['tools/s045_driver.py']
    for p,h in a['source_sha256'].items():
        if p!='tools/s045_driver.py':assert h==b['source_sha256'][p]
    smoke=read('SMOKE.json');assert smoke['verdict']=='PASS'
    assert smoke['chromatic_rows_verified']==smoke['chromatic_cnf_byte_matches']==271 and smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    controls=read('MEMORY_CONTROLS.json');assert controls['status']=='PASS' and controls['source_sha256']==a['source_sha256']
    assert all(controls[k] for k in ('soft_cooperative_recycle','positive_activity_required','hard_cap_stays_latched','deadline_overrides_recycle','native_unsat_overrides_recycle'))
    native=read('CONTROLS.json');policy=read('POLICY_CONTROLS.json')
    assert native['status']==policy['status']=='PASS'
    assert native['stop_test']['source_sha256']==policy['source_sha256']==a['source_sha256']
    assert native['exhaustive_n5']==1024 and native['standalone_drat_verified']
    for p,h in read('BUILD.json')['sha256'].items():
        if p.startswith(('tools/','tools\\','scripts/','scripts\\')):assert sha(ROOT/p.replace('\\','/'))==h,p
    original=read('INITIAL_SOURCES.json');assert original['commit']=='673d4a6b38cecf2533f3fc21ae66f09c7908685e'
    for item in original['files'].values():assert sha(ROOT/item['archive'])==item['sha256']
    for archive in (V/'preserved').glob('*.gz'):
        seal=json.loads(Path(str(archive)+'.seal.json').read_text());assert sha(archive)==seal['archive_sha256']
        h=hashlib.sha256();size=0
        with gzip.open(archive,'rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block);size+=len(block)
        assert h.hexdigest()==seal['raw_sha256'] and size==seal['raw_bytes']
    assert json.loads((V/'preserved/PLANARITY.lem.gz.seal.json').read_text())['raw_sha256']==pres['geometric_raw_sha256']
    # Recheck the final slice's formerly unaudited geometric tail independently.
    with tempfile.TemporaryDirectory() as directory:
        target=Path(directory)/'pending.lem';prefix=reg['previous_fully_audited_geometric_rules'];total=0
        with gzip.open(V/'preserved/PLANARITY.lem.gz','rb') as src,target.open('wb') as dst:
            for i,line in enumerate(src):
                if i>=prefix:dst.write(line)
                total+=1
        pending=geometric_journal(target,50);assert total==pres['geometric_rules'] and pending==total-prefix
        target.write_bytes(gzip.decompress((V/'benchmark/new-cuts.lem.gz').read_bytes()))
        new_cuts=geometric_journal(target,50);assert new_cuts==a['benchmark_new_geometric_rules']
    count=0;pairs=list(itertools.combinations(range(50),2))
    with gzip.open(V/'benchmark/CANDIDATES.jsonl.gz','rt',encoding='utf-8') as f:
        for line in f:
            r=json.loads(line);assert (r['n'],r['k'],r['mode'])==(50,9,'partition')
            check_pair(50,r['layers'],r['rotations']);check_colouring(50,r['layers'],r['colours'],9)
            bits=r['bits'];assert len(bits)==2450
            assert all([list(e) for i,e in enumerate(pairs) if bits[2*i+j]=='1']==r['layers'][j] for j in (0,1))
            clause=partition_clause(50,r['colours']);assert clause and all(bits[v-1]=='0' for v in clause);count+=1
    assert count==a['benchmark_new_candidates']==b['new_candidates']
    assert a['seed_candidates']==b['candidates']==453656+count
    assert a['seed_geometric_rules']==b['verified_geometric_cuts']==pres['geometric_rules']+new_cuts
    assert not b['witness'] and not b['domain_excluded'] and not a['counts_are_coverage']
    launch=read('LAUNCH_SNAPSHOT.json');assert launch['status']=='PASS'
    assert any(row['cpu_after']>row['cpu_before'] for row in launch['samples'].values())
    assert launch['records']['DEADLINE.json']['deadline_epoch']==1792913400
    state=json.loads((ROOT/'authoritative/STATE.json').read_text());assert state['s036_closeout']['computation']=='STOPPED'
    assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S045/EXECUTION_PROMPT.md').read_bytes()
    for p,h in read('MANIFEST.json')['sha256'].items():assert sha(ROOT/p)==h,p
    print(json.dumps(dict(status='PASS',formerly_pending_geometric_rules_checked=pending,benchmark_new_rules_checked=new_cuts,benchmark_candidates_checked=count,projected_coverage=None,witness=False)))
if __name__=='__main__':main()
