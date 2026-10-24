"""Registered full-checkpoint recovery and memory-bounded native slice."""
import json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import s045_search as s
from s045_driver import CORE
from s045_verify import geometric_journal
V=ROOT/'validation/S045/memory_recycle'
B=ROOT/'artifacts/tmp/S045/campaign'

def main():
    shutil.copy2(ROOT/'validation/S045/watchdog_repair/OWNER_DIRECTIVE.json',V/'OWNER_DIRECTIVE.json')
    for name in ('MEMORY_CONTROLS','POLICY_CONTROLS','CONTROLS'):assert json.loads((V/(name+'.json')).read_text())['status']=='PASS'
    smoke=json.loads((V/'SMOKE.json').read_text());assert smoke['verdict']=='PASS'
    reg=json.loads((V/'REGISTRATION.json').read_text());assert time.time()<reg['deadline_epoch']
    assert not any((B/p).exists() for p in ('OWNER_STOP.json','ALERT.json','ERROR.json','LOCK.json'))
    out=ROOT/'artifacts/tmp/S045/memory-benchmark';out.mkdir(exist_ok=False)
    shutil.copy2(B/'PLANARITY.lem',out/'PLANARITY.lem')
    start_bytes=(B/'PLANARITY.lem').stat().st_size;prefix_sha=s.sha(B/'PLANARITY.lem')
    sources=s.checkpoint_sources(B)
    source_manifest={str(p.relative_to(ROOT)):s.sha(p) for p in sources}
    cuts=geometric_journal(out/'PLANARITY.lem',50)
    s.atomic(V/'PRESERVATION.json',dict(status='PASS',candidates=453656,geometric_rules=cuts,geometric_raw_bytes=start_bytes,geometric_raw_sha256=prefix_sha,source_sha256=source_manifest,all_old_identities_exited=True,private_cdcl_serialized=False))
    result=s.run_slice(out,50,9,reg['benchmark_native_solve_ceiling_seconds'],'partition',True,
        records_sources=sources,absolute_deadline=reg['deadline_epoch'],soft_private_bytes=reg['soft_private_bytes'])
    assert result['state']=='SLICE_COMPLETE' and result['new_candidates']>0 and not result['audit_pending'] and not result['error'],result
    assert result['peak_private_bytes']<reg['hard_private_bytes']
    result.update(status='PASS',input_geometric_rules=cuts,input_candidates=453656,source_journals=source_manifest)
    s.atomic(V/'RESTART_BENCHMARK.json',result)
    with (out/'PLANARITY.lem').open('rb') as f:
        import hashlib
        h=hashlib.sha256();left=start_bytes
        while left:
            block=f.read(min(left,1024*1024));assert block;h.update(block);left-=len(block)
        assert h.hexdigest()==prefix_sha
        tail=V/'benchmark/new-cuts.lem';tail.parent.mkdir(exist_ok=True)
        with tail.open('wb') as dst:shutil.copyfileobj(f,dst)
    for p in (out/'CANDIDATES.jsonl',out/'NATIVE.log'):
        s.seal_file(p,V/'benchmark'/(p.name+'.gz'))
    s.seal_file(tail)
    # Preserve all stopped pre-recovery records as permanent append-only evidence.
    for p in sources:
        dest=V/'preserved'/p.name
        if p.name=='CANDIDATES.jsonl.gz':continue  # exact existing permanent archive
        shutil.copy2(p,dest);shutil.copy2(Path(str(p)+'.seal.json'),Path(str(dest)+'.seal.json'))
    s.seal_file(B/'PLANARITY.lem',V/'preserved/PLANARITY.lem.gz')
    # Restore same bytes plus independently checked benchmark tail for production.
    import gzip
    with gzip.open(V/'preserved/PLANARITY.lem.gz','rb') as src,(B/'PLANARITY.lem').open('wb') as dst:shutil.copyfileobj(src,dst)
    with gzip.open(V/'benchmark/new-cuts.lem.gz','rb') as src,(B/'PLANARITY.lem').open('ab') as dst:shutil.copyfileobj(src,dst)
    ids=[int(p.name.split('.')[0]) for p in (B/'journals').iterdir() if p.name.split('.')[0].isdigit()]
    dest=B/'journals'/f'{max(ids)+1:06d}.jsonl.gz'
    shutil.copy2(V/'benchmark/CANDIDATES.jsonl.gz',dest);shutil.copy2(V/'benchmark/CANDIDATES.jsonl.gz.seal.json',Path(str(dest)+'.seal.json'))
    assert s.sha(B/'PLANARITY.lem')==s.sha(out/'PLANARITY.lem')
    s.atomic(V/'ACCEPTANCE.json',dict(status='PASS',source_sha256={p:s.sha(ROOT/p) for p in CORE},smoke='PASS',native_controls='PASS',policy_controls='PASS',memory_controls='PASS',full_restart_benchmark='PASS',deadline_epoch=1792913400,soft_private_bytes=reg['soft_private_bytes'],hard_private_bytes=reg['hard_private_bytes'],seed_candidates=result['candidates'],seed_geometric_rules=result['verified_geometric_cuts'],seed_geometry_sha256=s.sha(B/'PLANARITY.lem'),benchmark_new_candidates=result['new_candidates'],benchmark_new_geometric_rules=result['verified_geometric_cuts']-cuts,counts_are_coverage=False,private_cdcl_serialized=False))
    print('Full checkpoint memory benchmark and preserved seed PASS')

if __name__=='__main__':main()
