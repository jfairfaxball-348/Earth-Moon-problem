"""Preserve a stopped S045 campaign and register the final independent audit."""
import hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
import psutil
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'validation/S045/final';B=ROOT/'artifacts/tmp/S045/campaign'
sys.path.insert(0,str(ROOT/'tools'))
import s045_search as s

def alive(i):
    try:
        p=psutil.Process(i['pid']);return abs(p.create_time()-i['create_time'])<.001 and p.exe().lower()==i['exe'].lower()
    except psutil.Error:return False

def main():
    V.mkdir(exist_ok=True)
    prior_registration=json.loads((V/'REGISTRATION.json').read_text()) if (V/'REGISTRATION.json').exists() else {}
    records={p:json.loads((B/(p+'.json')).read_text()) for p in ('CAMPAIGN','STATUS','IDENTITY','POWER','DEADLINE','STOP_CAUSE')}
    assert records['CAMPAIGN']['state']=='STOPPED' and records['STOP_CAUSE']['reason']=='OWNER_DEADLINE_0730'
    assert records['DEADLINE']['deadline_epoch']==1792913400 and time.time()>1792913400
    identities=[i for row in records.values() for k,i in row.items() if k in ('controller','generator','helper')]
    assert all(not alive(i) for i in identities)
    assert not any((B/p).exists() for p in ('LOCK.json','ALERT.json','ERROR.json','OWNER_STOP.json'))
    assert records['POWER']['state']=='RELEASED'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='307399a7ce471f722181098a93c8378d5b2f5824'
    # Freeze the preceding handover context. No historical manifest is rewritten.
    previous=json.loads((ROOT/'validation/S045/memory_recycle/MANIFEST.json').read_text())
    source_index={}
    for p in previous['sha256']:
        if not p.startswith('validation/') and p.endswith(('.py','.md','.json','.yml','.cpp','.hpp')):
            dest=V/'initial_sources'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/p).read_bytes())
            source_index[p]=dict(archive=dest.relative_to(ROOT).as_posix(),sha256=s.sha(dest))
    s.atomic(V/'INITIAL_SOURCES.json',dict(commit='307399a7ce471f722181098a93c8378d5b2f5824',files=source_index))
    snap=V/'stop_snapshot';snap.mkdir(exist_ok=True)
    for p in B.iterdir():
        if p.is_file() and p.name in ('CAMPAIGN.json','STATUS.json','IDENTITY.json','POWER.json','DEADLINE.json','STOP_CAUSE.json','LAUNCH.json','STOP','SLICE_STOP','SLICES.jsonl','controller.log'):
            shutil.copy2(p,snap/p.name)
    for p in (ROOT/'artifacts/tmp/S045/checkins').glob('*.json'):
        dest=V/'checkins';dest.mkdir(exist_ok=True);shutil.copy2(p,dest/p.name)
    complete=[json.loads(l) for l in (B/'SLICES.jsonl').read_text().splitlines() if json.loads(l)['state']=='SLICE_COMPLETE']
    last=complete[-1]
    s.atomic(V/'REGISTRATION.json',dict(session='S045',scope='Deadline closeout only; no new generation or successor execution',deadline_epoch=1792913400,observed_stop_epoch=records['STOP_CAUSE']['time_epoch'],expected_candidate_records=last['candidates'],expected_geometric_occurrences=last['verified_geometric_cuts'],inherited_independently_checked_prefix_records=453656,prefix_receipt='validation/S045/memory_recycle/RESTART_BENCHMARK.json',fresh_check_delta_records=last['candidates']-453656,all_archives_byte_checked=True,all_geometry_freshly_replayed=True,native_traces_scan_for_unjournalled_candidates=True,orphan_cap=1000,orphan_colouring_seconds=10,search_restarted=False,private_cdcl_serialized=False,registered_epoch=prior_registration.get('registered_epoch',time.time())))
    known={}
    for base in ('validation/S045/watchdog_repair','validation/S045/memory_recycle'):
        for p in (ROOT/base).rglob('*.gz'):
            if p.name.endswith('.jsonl.gz') or p.name in ('NATIVE.log.gz',):known[s.sha(p)]=p
    def preserve(p,kind):
        p=Path(p);h=s.sha(p)
        if h in known:archive=known[h]
        elif p.suffix=='.gz':
            archive=V/kind/p.name;archive.parent.mkdir(exist_ok=True);shutil.copy2(p,archive)
            seal=Path(str(p)+'.seal.json')
            if seal.exists():shutil.copy2(seal,Path(str(archive)+'.seal.json'))
            known[h]=archive
        else:
            archive=V/kind/(p.name+'.gz');archive.parent.mkdir(exist_ok=True);temp=archive.with_suffix('')
            shutil.copy2(p,temp);s.seal_file(temp,archive)
        return dict(runtime_source=p.relative_to(ROOT).as_posix(),archive=archive.relative_to(ROOT).as_posix(),archive_sha256=s.sha(archive))
    journals=[preserve(p,'journals') for p in s.checkpoint_sources(B)]
    trace_sources=[B/'NATIVE.log.gz',*sorted((B/'logs').glob('*.gz'))]
    if (B/'NATIVE.log').exists():trace_sources.append(B/'NATIVE.log')
    trace_sources.extend(ROOT/p for p in ('validation/S045/watchdog_repair/benchmark/NATIVE.log.gz','validation/S045/memory_recycle/preserved/NATIVE.log.gz','validation/S045/memory_recycle/benchmark/NATIVE.log.gz'))
    traces=[];seen=set()
    for p in trace_sources:
        if not p.exists():continue
        h=s.sha(p)
        if h in seen:continue
        seen.add(h);traces.append(preserve(p,'native'))
    raw=V/'PLANARITY.lem';shutil.copy2(B/'PLANARITY.lem',raw);geometry=s.seal_file(raw)
    assert geometry['raw_sha256']==s.sha(B/'PLANARITY.lem')
    s.atomic(V/'ARCHIVE_INDEX.json',dict(journals=journals,native_traces=traces,geometry=dict(geometry,archive='validation/S045/final/PLANARITY.lem.gz')))
    s.atomic(V/'ENTRY.json',dict(commit='307399a7ce471f722181098a93c8378d5b2f5824',tree='27e46b9ff7ec7fc81a1a12e3534877a071b5b276',parent='673d4a6b38cecf2533f3fc21ae66f09c7908685e',entry_hosted_run=40132656455,entry_hosted_job=120987486782,entry_hosted_conclusion='success',all_recorded_identities_exited=True,deadline_latched_epoch=records['STOP_CAUSE']['time_epoch'],preparation_searches=0))
    print('Stopped identities and final evidence preserved',flush=True)

if __name__=='__main__':main()
