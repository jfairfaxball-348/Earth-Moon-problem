"""Independent stages; avoids changing running baseline sources."""
import datetime,itertools,json,math,sys,time
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
ROOT=Path('validation/S009');TMP=Path('artifacts/tmp/S009')

def controls():
    from s009_heavy_cover import HeavyCover,completion_k33
    import s007_static_controls
    s007_static_controls.StrongCover=HeavyCover
    rows=[]
    for row in json.loads(Path('validation/S007/static_truth_controls.json').read_text()):
        name=row['tag'];n=row['n'];layers=[set(map(tuple,es)) for es in row['completion_edges']]
        family=list(completion_k33(n));assert len(family)==10*math.comb(n,6) and len(set(family))==len(family)
        independent=set()
        for a in itertools.combinations(range(n),3):
            for b in itertools.combinations([v for v in range(n) if v not in a],3):
                if min(a)<min(b):independent.add(tuple(sorted(tuple(sorted((u,v))) for u in a for v in b)))
        assert set(family)==independent
        for es in family:assert all(not set(es)<=layer for layer in layers)
        ef=Path('artifacts/tmp/S008/replay')/(name+'.edges') if name[-2:].isdigit() else Path('validation/S003/splits')/(name[len('control-'):]+'.edges')
        split=Path('artifacts/tmp/S008/replay')/(name+'.split.json')
        pin=s007_static_controls.static_control(str(ef),str(split))
        rows.append(dict(name=name,n=n,completion_K33_count=len(family),pin=pin))
        save(ROOT/'heavy_controls.json',rows)
    assert len(rows)==23
    print('PASS23 full pins/rotations and independent complete K33 families',flush=True)

def heavy_search():
    assert len(json.loads((ROOT/'heavy_controls.json').read_text()))==23
    tmp=TMP/'heavy';tmp.mkdir(exist_ok=True);prefix=tmp/'K7-I5';ef=ROOT/'targets/K7-I5.edges'
    run=run_logged([sys.executable,'tools/s009_heavy_cover.py',str(ef),str(prefix),'1200','--lex'],1220,str(prefix)+'.run.log')
    row=dict(run=run,grade='PROVISIONAL_UNVERIFIED_NO_ACCEPTANCE_BEFORE_BASELINE',edge_sha256=sha(ef))
    meta=Path(str(prefix)+'.result.json')
    if meta.exists():row['search']=json.loads(meta.read_text())
    save(ROOT/'heavy_provisional.json',row);print('Heavy provisional',row,flush=True)

def heavy_accept():
    assert (ROOT/'BASELINE_PASS.json').exists()
    import s009_run
    from s009_heavy_cover import HeavyCover
    root=ROOT/'heavy';(root/'search').mkdir(parents=True,exist_ok=True)
    p=json.loads((ROOT/'heavy_provisional.json').read_text());prefix=TMP/'heavy/K7-I5';ef=str(ROOT/'targets/K7-I5.edges')
    row=dict(n=12,m=56,D=4,edgefile=ef,edge_sha256=sha(ef),verdict='UNKNOWN',run=p['run'],search=p.get('search',{}))
    if row['run']['returncode']==0 and row['search'].get('verdict')=='UNSAT':
        row['certificate']=s009_run.certificate(ef,prefix,root,'tools/s009_heavy_cover.py',HeavyCover)
        row['verdict']=row['certificate']['verdict']
    elif row['run']['returncode']==0 and row['search'].get('verdict')=='SAT_CHECKED':
        from check_layers import main as check_split
        from biplanar_cnf import read_edges
        check_split(ef,str(prefix)+'.split.json');split=json.loads(Path(str(prefix)+'.split.json').read_text())
        col=list(range(7))+[7]*5;es=set(read_edges(ef))
        assert all(col[a]!=col[b] for a,b in es) and set(itertools.combinations(range(8),2))<=es
        row.update(verdict='BIPLANAR_CHECKED_CHI8',split=split,proper_colouring=col,clique_lower=list(range(8)))
        save(root/'split.json',split)
    s009_run.package(ef,prefix,root,HeavyCover,row);save(root/'result.json',row)
    print('Final heavy',row['verdict'],flush=True)

if __name__=='__main__':
    mode=sys.argv[1]
    if len(sys.argv)>2 and sys.argv[2]=='worker':globals()[mode]();raise SystemExit
    observed=ROOT/(mode+'_stage_observed_launch.json');assert not observed.exists()
    files=sorted(set(str(p).replace('\\','/') for p in Path('tools').glob('s009*.py')) |
        {'tools/s005_search.py','tools/s006_run.py','tools/s007_static_controls.py',
         'tools/s008_tree.py','tools/s008_cover.py','tools/s007_cover.py','tools/triangulation_cover.py'})
    snap=ROOT/'launch_snapshots'/mode;snap.mkdir(parents=True,exist_ok=True)
    for f in files:(snap/(Path(f).name+'.txt')).write_bytes(Path(f).read_bytes())
    cmd=[sys.executable,'tools/s009_stage.py',mode,'worker']
    save(observed,dict(as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=cmd,
        sha256={f:sha(f) for f in files},grade='OBSERVED_BEFORE_LAUNCH',snapshots=str(snap)))
    cap={'controls':920,'heavy_search':1240,'heavy_accept':6600}[mode]
    r=run_logged(cmd,cap,ROOT/(mode+'_stage_driver.log'));save(ROOT/(mode+'_stage_command.json'),r)
    print(mode,r,flush=True);assert r['returncode']==0
