"""Prospective transfer from completed NEW direct S009 full refutations."""
import datetime,gzip,hashlib,json,sys,time
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
from s009_injection import injection
from blowup_graph import blowup
import s009_run
ROOT=Path('validation/S009')

def discover():
    assert json.loads((ROOT/'full_driver_command.json').read_text())['returncode']==0
    full=json.loads((ROOT/'full/results.json').read_text())
    source_rows=[r for r in full if r['verdict']=='NON_BIPLANAR_DRAT_VERIFIED']
    save(ROOT/'new_transfer_frozen_sources.json',source_rows)
    sources=[r['target']['index'] for r in source_rows]
    for r in source_rows:
        c=r['certificate'];i=r['target']['index']
        assert c['check']['returncode']==0 and c['core_check']['returncode']==0 and c['cold_retained_check']['returncode']==0
        assert sha(c['archive'])==c['archive_sha256']
        assert hashlib.sha256(gzip.decompress(Path(c['archive']).read_bytes())).hexdigest()==c['archive_raw_sha256']
        assert hashlib.sha256(gzip.decompress((ROOT/f'full/search/cover-row{i}.cnf.gz').read_bytes())).hexdigest()==c['cnf_sha256']
        for suffix in ('.check.log','.trim.log','.core.check.log','.cold.check.log'):
            assert 's VERIFIED' in (ROOT/'full/search'/f'cover-row{i}{suffix}').read_text()
    previous=set(json.loads(Path('validation/S008/SUMMARY.json').read_text())['excluded_indices'])|set(sources)
    p=ROOT/'local_transfer_acceptance.json'
    if p.exists():previous|={r['target'] for r in json.loads(p.read_text()) if r['verdict']=='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED'}
    targets=sorted(set(range(271))-previous);corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    graphs={i:(sum(r[1]),blowup(*r[:2])[0]) for i,r in enumerate(corpus)}
    rows=[];maps=[];begin=time.monotonic()
    for target in targets:
        found=False
        for source in sorted(sources):
            ns,es=graphs[source];nt,et=graphs[target]
            if found:r=dict(verdict='NOT_NEEDED_AFTER_MAP')
            elif time.monotonic()-begin>=300:r=dict(verdict='GLOBAL_CAP_NOT_RUN')
            else:r=injection(ns,es,nt,et,min(begin+300,time.monotonic()+2))
            r.update(source=source,target=target)
            if r['verdict']=='VERIFIED_MAP':
                m=r['mapping'];assert len(set(m.values()))==ns and set(m)==set(range(ns))
                assert all(tuple(sorted((m[u],m[v]))) in set(et) for u,v in es)
                found=True;maps.append(r)
            rows.append(r)
        save(ROOT/'new_transfer_pairs.json',rows);save(ROOT/'new_transfer_maps.json',maps)
    save(ROOT/'new_transfer_search_summary.json',dict(sources=sorted(sources),targets=targets,pair_count=len(rows),
        seconds=time.monotonic()-begin,verified_targets=[r['target'] for r in maps],
        verdict_counts={v:sum(r['verdict']==v for r in rows) for v in sorted({r['verdict'] for r in rows})},symmetry='NONE'))
    print('New-source transfer',len(rows),'pairs;',len(maps),'maps',flush=True)

def accept():
    corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    sources={r['target']['index']:r for r in json.loads((ROOT/'new_transfer_frozen_sources.json').read_text())}
    specs=json.loads((ROOT/'new_transfer_maps.json').read_text());rows=[];consecutive=0
    (ROOT/'new_transfer_targets').mkdir(exist_ok=True)
    for r in specs:
        row=dict(r,verdict='UNKNOWN')
        if consecutive>=2:row['reason']='NOT_RUN after two consecutive FINAL checker failures'
        else:
            try:
                si=r['source'];ti=r['target'];assert si in sources
                se,_=blowup(*corpus[si][:2]);te,_=blowup(*corpus[ti][:2]);m={int(k):v for k,v in r['mapping'].items()}
                assert set(m)==set(range(sum(corpus[si][1]))) and len(set(m.values()))==len(m)
                assert all(tuple(sorted((m[u],m[v]))) in set(te) for u,v in se)
                c=sources[si]['certificate'];assert sha(c['archive'])==c['archive_sha256']
                ef=ROOT/'new_transfer_targets'/f'row{ti}.edges';ef.write_text(''.join(f'{u} {v}\n' for u,v in te),newline='\n')
                row.update(edgefile=str(ef),edge_sha256=sha(ef),fresh_chromatic=s009_run.lower(ti),
                    source_proof='validation/S009/full/results.json',verdict='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED')
            except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
            consecutive=consecutive+1 if row['verdict']=='UNKNOWN' else 0
        rows.append(row);save(ROOT/'new_transfer_acceptance.json',rows)
        print('New map',r['source'],r['target'],row['verdict'],flush=True)
    if not specs:save(ROOT/'new_transfer_acceptance.json',[])

if __name__=='__main__':
    mode=sys.argv[1]
    if len(sys.argv)>2 and sys.argv[2]=='worker':globals()[mode]();raise SystemExit
    record=ROOT/('new_'+mode+'_observed_launch.json');assert not record.exists()
    files=['tools/s009_new_transfer.py','tools/s009_injection.py','tools/s009_run.py','tools/s005_search.py',
           'validation/S009/full/results.json','validation/S003/survivors_alpha_ge3.json','campaigns/CAM-0010.md']
    snap=ROOT/'launch_snapshots'/('new_'+mode);snap.mkdir(parents=True,exist_ok=True)
    for f in files:(snap/(Path(f).name+'.txt')).write_bytes(Path(f).read_bytes())
    cmd=[sys.executable,'tools/s009_new_transfer.py',mode,'worker']
    native=json.loads((ROOT/'environment.json').read_text())['native_sha256']
    for name,exp in native.items():assert sha(Path('artifacts/tmp/S004')/name)==exp
    save(record,dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256={f:sha(f) for f in files},
        native_sha256=native,grade='OBSERVED_BEFORE_LAUNCH'))
    result=run_logged(cmd,320 if mode=='discover' else 7200,ROOT/('new_'+mode+'_driver.log'))
    save(ROOT/('new_'+mode+'_command.json'),result);print(mode,result,flush=True);assert result['returncode']==0
