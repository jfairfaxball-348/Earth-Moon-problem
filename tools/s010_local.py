"""Prospective endpoint controls, provisional search and gated exact acceptance."""
import datetime, gzip, itertools, json, math, shutil, sys
from pathlib import Path
from s005_search import run_logged
from s005_replay import sha
from s007_run import save
ROOT=Path('validation/S010/local');TMP=Path('artifacts/tmp/S010/local')

def controls():
    import s007_static_controls
    from s010_local_cover import LocalCover,completion_k33
    from check_layers import main as check_split
    s007_static_controls.StrongCover=LocalCover;rows=[]
    for n in (13,14):
        es=[(0,1)]+[(u,v) for u in (0,1) for v in range(2,n)]
        split=dict(n=n,E1=[(0,1)]+[(0,v) for v in range(2,n)],E2=[(1,v) for v in range(2,n)])
        ef=ROOT/f'control{n}.edges';sf=ROOT/f'control{n}.split.json'
        ef.write_text(''.join(f'{u} {v}\n' for u,v in es),newline='\n');save(sf,split);check_split(str(ef),str(sf))
        pin=s007_static_controls.static_control(str(ef),str(sf))
        family=set(completion_k33(n));independent=set()
        for a in itertools.combinations(range(n),3):
            for b in itertools.combinations([v for v in range(n) if v not in a],3):
                if min(a)<min(b):independent.add(tuple(sorted(tuple(sorted((u,v))) for u in a for v in b)))
        assert family==independent and len(family)==10*math.comb(n,6)
        assert all(not set(es)<=set(map(tuple,layer)) for es in family for layer in pin['completion_edges'])
        rows.append(dict(n=n,edges=es,split=split,pin=pin,independent_K33_count=len(family)))
    h=json.loads(Path('validation/S007/heavy_search.json').read_text())[1]
    sf=TMP/'K6I6.split.json';save(sf,h['split'])
    rows.append(dict(n=12,pin=s007_static_controls.static_control(h['edgefile'],str(sf)),grade='inherited_input_new_model_pin'))
    save(ROOT/'controls.json',dict(verdict='PASS',rows=rows))
    print('PASS n13/n14 primary pins/rotations/independent K33 and K6I6 pin',flush=True)

def search():
    assert json.loads((ROOT/'controls.json').read_text())['verdict']=='PASS'
    rows=[]
    for tag,size,cycle in [('P4-I9',4,False),('C5-I9',5,True)]:
        n=size+9;es={(v,v+1) for v in range(size-1)}|{(u,v) for u in range(size) for v in range(size,n)}
        if cycle:es.add((0,size-1))
        es=sorted(es);ef=ROOT/(tag+'.edges');ef.write_text(''.join(f'{u} {v}\n' for u,v in es),newline='\n')
        prefix=TMP/tag;run=run_logged([sys.executable,'tools/s010_local_cover.py',str(ef),str(prefix),'900','--lex'],920,ROOT/(tag+'.search.log'))
        p=Path(str(prefix)+'.result.json');meta=json.loads(p.read_text()) if p.exists() else {}
        rows.append(dict(tag=tag,n=n,m=len(es),D=6*n-12-len(es),edgefile=str(ef),edge_sha256=sha(ef),
                         run=run,search=meta,prefix=str(prefix),verdict='PROVISIONAL_UNVERIFIED'))
        save(ROOT/'provisional.json',rows);print(tag,'provisional',meta.get('verdict','UNKNOWN'),flush=True)

def accept():
    assert json.loads(Path('validation/S010/BASELINE_PASS.json').read_text())['verdict']=='PASS'
    assert json.loads((ROOT/'controls.json').read_text())['verdict']=='PASS'
    from s010_local_cover import LocalCover
    import s009_run
    from check_layers import main as check_split,certify_layer
    from check_rotation import check
    from biplanar_cnf import read_edges
    import networkx as nx
    rows=[]
    for row in json.loads((ROOT/'provisional.json').read_text()):
        tag=row['tag'];prefix=Path(row['prefix']);ef=row['edgefile'];meta=row['search'];row['verdict']='UNKNOWN'
        if row['run']['returncode']==0 and meta.get('verdict')=='UNSAT':
            rec=s009_run.certificate(ef,prefix,ROOT,'tools/s010_local_cover.py',LocalCover)
            row.update(certificate=rec,verdict=rec['verdict'])
        elif row['run']['returncode']==0 and meta.get('verdict')=='SAT_CHECKED':
            split=json.loads(Path(str(prefix)+'.split.json').read_text());check_split(ef,str(prefix)+'.split.json')
            size=4 if tag.startswith('P4') else 5
            col=([0,1,0,1]+[2]*9) if size==4 else ([0,1,0,1,2]+[3]*9)
            assert len(col)==row['n'] and all(col[a]!=col[b] for a,b in read_edges(ef))
            rotations=[]
            for key in ('E1','E2'):
                certify_layer(row['n'],split[key]);g=nx.Graph();g.add_nodes_from(range(row['n']));g.add_edges_from(split[key])
                ok,emb=nx.check_planarity(g);assert ok
                comps=[]
                for component in nx.connected_components(g):
                    labels=sorted(component)
                    if len(labels)==1:comps.append(dict(isolated=labels));continue
                    rel={v:i for i,v in enumerate(labels)};es=[tuple(sorted((rel[a],rel[b]))) for a,b in split[key] if a in component]
                    rot={str(rel[v]):[rel[u] for u in emb.neighbors_cw_order(v)] for v in labels}
                    comps.append(dict(labels=labels,rotation=rot,independent_sphere=check(len(labels),es,rot)))
                rotations.append(comps)
            row.update(verdict='BIPLANAR_EXACT_CHI'+str(max(col)+1),V=list(range(row['n'])),split=split,rotations=rotations,
                       proper_colouring=col,chi=max(col)+1,lower_proof='P4 edge requires2 colours, or odd C5 requires3; every joined independent-side vertex needs an additional colour.')
        # Cover.save records lex/cuts but no StrongCover static field. Preserve that actual schema.
        d=json.loads(Path(str(prefix)+'.cuts.json').read_text())
        c=LocalCover(read_edges(ef),d['lex'],d.get('short_links',False));c.cuts=d['cuts']
        last=Path(str(prefix)+'.last.audit.cnf');c.write_cnf(last)
        from s005_search import compress
        dest=ROOT/'search'/tag
        archive=str(dest)+'.partial.cnf.gz'
        if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
            archive=str(dest)+'.cnf.gz';assert last.read_bytes()==gzip.decompress(Path(archive).read_bytes())
        else:compress(last,archive)
        c.cuts=[];initial=Path(str(prefix)+'.initial.audit.cnf');c.write_cnf(initial)
        assert initial.read_bytes()==Path(str(prefix)+'.initial.cnf').read_bytes()
        ia=str(dest)+'.initial.cnf.gz';compress(initial,ia)
        for suffix in ('.cuts.json','.result.json','.split.json'):
            p=Path(str(prefix)+suffix)
            if p.exists():shutil.copyfile(p,str(dest)+suffix)
        row['cnf_package']=dict(grade='FULL_CNF_CHECKED_DRAT' if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED' else 'PARTIAL_NECESSARY_CNF_NOT_A_REFUTATION',
            static=c.static,raw_sha256=sha(last),archive=archive,archive_sha256=sha(archive),
            initial_raw_sha256=sha(initial),initial_archive=ia,initial_archive_sha256=sha(ia),
            metadata_grade='ACTUAL_COVER_LEX_CUT_SCHEMA_STATIC_DERIVED_DURING_COLD_PACKAGING')
        rows.append(row);save(ROOT/'results.json',rows);print(tag,'FINAL',row['verdict'],flush=True)

if __name__=='__main__':
    ROOT.mkdir(parents=True,exist_ok=True);(ROOT/'search').mkdir(exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
    mode=sys.argv[1]
    if len(sys.argv)>2 and sys.argv[2]=='worker':globals()[mode]();raise SystemExit
    record=ROOT/(mode+'_observed_launch.json');assert not record.exists()
    files=sorted(str(p).replace('\\','/') for p in Path('tools').glob('*.py'))+['campaigns/CAM-0011.md','validation/S007/heavy_search.json']
    snap=ROOT/'launch_snapshots'/mode;snap.mkdir(parents=True)
    for f in files:
        if f.endswith('.py'):snap.joinpath(Path(f).name+'.txt').write_bytes(Path(f).read_bytes())
    cap={'controls':920,'search':1960,'accept':14400}[mode];cmd=[sys.executable,'tools/s010_local.py',mode,'worker']
    save(record,dict(grade='OBSERVED_BEFORE_LAUNCH',as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=cmd,
                     cap=cap,sha256={f:sha(f) for f in files},native=json.loads(Path('validation/S010/environment.json').read_text())['native_sha256']))
    r=run_logged(cmd,cap,ROOT/(mode+'_driver.log'));save(ROOT/(mode+'_command.json'),r);print(mode,r,flush=True);assert r['returncode']==0
