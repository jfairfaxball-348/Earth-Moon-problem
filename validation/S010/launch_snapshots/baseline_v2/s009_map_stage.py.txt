"""Separate provisional map discovery and gated independent map acceptance."""
import datetime,hashlib,inspect,json,sys
from pathlib import Path
import s009_run
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
ROOT=Path('validation/S009');TMP=Path('artifacts/tmp/S009')

def discover():
    source=inspect.getsource(s009_run.transfer)
    source=source.replace("assert (ROOT/'BASELINE_PASS.json').exists() and (ROOT/'injection_controls.json').exists()", "assert (ROOT/'injection_controls.json').exists()")
    source=source.replace("assert not accepted,'Maps retained; register acceptance checker lane prospectively before promotion'", "# All discovered maps remain provisional until separately gated acceptance.")
    p=TMP/'transfer_discovery_adapter.txt';p.write_text(source,newline='\n')
    save(ROOT/'transfer_discovery_adapter_observed.json',dict(path=str(p),sha256=sha(p),grade='BEFORE_ADAPTER_EXECUTION'))
    scope=dict(s009_run.__dict__);exec(source,scope);scope['transfer']()

def accept():
    from blowup_graph import blowup
    base=json.loads((ROOT/'BASELINE_PASS.json').read_text())
    assert base['cold_S008_full']==3 and base['cold_prior_full']==40
    assert json.loads((ROOT/'baseline_driver_command.json').read_text())['returncode']==0
    corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    specs=json.loads((ROOT/'transfer_maps.json').read_text());out=[];consecutive=0
    cold_sources=set(r['index'] for r in json.loads((ROOT/'cold_prior.json').read_text()))
    cold_sources|={165}|set(r['index'] for r in json.loads((ROOT/'cold_S008.json').read_text()))
    assert len(cold_sources)==44
    (ROOT/'transfer_targets').mkdir(exist_ok=True)
    for rec in specs:
        row=dict(rec,verdict='UNKNOWN')
        if consecutive>=2:row['reason']='NOT_RUN after two consecutive FINAL checker failures'
        else:
            try:
                si=rec['source'];ti=rec['target'];assert si in cold_sources
                se,_=blowup(*corpus[si][:2]);te,_=blowup(*corpus[ti][:2]);ns=sum(corpus[si][1]);nt=sum(corpus[ti][1])
                m={int(k):int(v) for k,v in rec['mapping'].items()}
                assert set(m)==set(range(ns)) and len(set(m.values()))==ns and all(0<=v<nt for v in m.values())
                assert all(tuple(sorted((m[u],m[v]))) in set(te) for u,v in se)
                assert hashlib.sha256(repr(se).encode()).hexdigest()==rec['source_edges_sha256']
                assert hashlib.sha256(repr(te).encode()).hexdigest()==rec['target_edges_sha256']
                ef=ROOT/'transfer_targets'/f'row{ti}.edges';ef.write_text(''.join(f'{u} {v}\n' for u,v in te),newline='\n')
                row.update(edgefile=str(ef),edge_sha256=sha(ef),fresh_chromatic=s009_run.lower(ti),
                    source_cold_baseline='validation/S009/BASELINE_PASS.json',verdict='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED')
            except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
            consecutive=consecutive+1 if row['verdict']=='UNKNOWN' else 0
        out.append(row);save(ROOT/'transfer_acceptance_rows.json',out)
        save(ROOT/'transfer_accepted.json',[r for r in out if r['verdict']=='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED'])
        print('Map acceptance',rec['source'],rec['target'],row['verdict'],flush=True)
    if not specs:save(ROOT/'transfer_acceptance_rows.json',[]);save(ROOT/'transfer_accepted.json',[])

if __name__=='__main__':
    mode=sys.argv[1]
    if len(sys.argv)>2 and sys.argv[2]=='worker':globals()[mode]();raise SystemExit
    record=ROOT/(mode+'_maps_observed_launch.json');assert not record.exists()
    files=sorted(set(str(p).replace('\\','/') for p in Path('tools').glob('s009*.py')) |
        {'tools/s005_replay.py','tools/s005_search.py','tools/blowup_graph.py','tools/blowup_chi_cnf.py',
         'validation/S003/survivors_alpha_ge3.json','validation/S004/chi10_results.json','campaigns/CAM-0010.md'})
    snap=ROOT/'launch_snapshots'/('maps_'+mode);snap.mkdir(parents=True,exist_ok=True)
    for f in files:
        if f.endswith('.py'):(snap/(Path(f).name+'.txt')).write_bytes(Path(f).read_bytes())
    cmd=[sys.executable,'tools/s009_map_stage.py',mode,'worker']
    save(record,dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sha256={f:sha(f) for f in files},grade='OBSERVED_BEFORE_LAUNCH',snapshots=str(snap)))
    r=run_logged(cmd,320 if mode=='discover' else 7200,ROOT/(mode+'_maps_driver.log'))
    save(ROOT/(mode+'_maps_command.json'),r);print(mode,r,flush=True);assert r['returncode']==0
