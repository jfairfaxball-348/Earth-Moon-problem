"""Conditional complete K7-I5 detector on the fixed clique-blowup corpus."""
import datetime,gzip,hashlib,itertools,json,sys
from pathlib import Path
import networkx as nx
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
from blowup_graph import blowup
from biplanar_cnf import read_edges
import s009_run
from s009_heavy_evidence import effective_heavy
ROOT=Path('validation/S009')

def allocations(weights,left,index=0,prefix=()):
    if index==len(weights):
        if left==0:yield prefix
        return
    for x in range(min(weights[index],left)+1):
        yield from allocations(weights,left-x,index+1,prefix+(x,))

def detector(g6,w):
    g=nx.from_graph6_bytes(g6.encode());n=len(w);offset=list(itertools.accumulate([0]+w))
    checks=0
    for mask in range(1,1<<n):
        used=[v for v in range(n) if mask>>v&1]
        if not all(g.has_edge(u,v) for u,v in itertools.combinations(used,2)):continue
        if len(used)>7 or sum(w[v] for v in used)<7:continue
        for xs in allocations([w[v] for v in used],7):
            if any(x==0 for x in xs):continue # This mask represents EXACT positive support.
            checks+=1
            clique=[offset[v]+j for v,x in zip(used,xs) for j in range(x)]
            common=[offset[v]+j for v,x in zip(used,xs) for j in range(x,w[v])]
            common +=[offset[v]+j for v in range(n) if v not in used and all(g.has_edge(v,u) for u in used) for j in range(w[v])]
            if len(common)>=5:return dict(verdict='MAP',mapping=dict(enumerate(clique+common[:5])),allocations_checked=checks)
    return dict(verdict='NO_K7I5_SUBGRAPH_IN_FIXED_BLOWUP',allocations_checked=checks)

def controls():
    def code(g):return nx.to_graph6_bytes(g,header=False).decode().strip()
    for weights,base,expected in [([7]+[1]*5,nx.star_graph(5),True),
                                 ([6]+[1]*6,nx.star_graph(6),False),
                                 ([7]+[1]*5,nx.empty_graph(6),False),
                                 ([8]+[1]*4,nx.star_graph(4),True)]:
        g6=code(base);r=detector(g6,weights);assert (r['verdict']=='MAP')==expected
        if expected:
            es=set(blowup(g6,weights)[0]);m=r['mapping']
            src=list(itertools.combinations(range(7),2))+[(a,b) for a in range(7) for b in range(7,12)]
            assert all(tuple(sorted((m[u],m[v]))) in es for u,v in src)
    rows=[]
    for row in json.loads(Path('validation/S009/controls.json').read_text())['results']:
        tag=f"control-{row['index']:02d}" if 'index' in row else 'control-'+row['tag']
        ef=Path('artifacts/tmp/S009/replay')/(tag+'.edges') if 'index' in row else Path(f"validation/S003/splits/{row['tag']}.edges")
        es=read_edges(str(ef));g=nx.Graph(es);found=False;checked=0
        # Completely independent labelled-clique generator for positive-planar controls.
        for clique in nx.enumerate_all_cliques(g):
            if len(clique)>7:break
            if len(clique)!=7:continue
            checked+=1;common=set(g)-set(clique)
            for v in clique:common&=set(g[v])
            if len(common)>=5:found=True;break
        assert not found,tag
        rows.append(dict(tag=tag,seven_cliques_checked=checked,no_local_obstruction=True))
    assert len(rows)==23;save(ROOT/'local_transfer_controls.json',dict(symbolic_blowup_examples=4,actual_planar_controls=rows,verdict='PASS'))

def detect():
    source,record,prefix=effective_heavy();assert source['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'
    rec=source['certificate']
    assert rec['solve']['returncode']==20 and rec['check']['returncode']==0
    assert rec['core_check']['returncode']==0 and rec['cold_retained_check']['returncode']==0
    assert sha(rec['archive'])==rec['archive_sha256']
    assert hashlib.sha256(gzip.decompress(Path(rec['archive']).read_bytes())).hexdigest()==rec['archive_raw_sha256']
    assert hashlib.sha256(gzip.decompress(Path(str(prefix)+'.cnf.gz').read_bytes())).hexdigest()==rec['cnf_sha256']
    assert sha(source['edgefile'])==source['edge_sha256']
    for suffix in ('.check.log','.trim.log','.core.check.log','.cold.check.log'):
        assert 's VERIFIED' in Path(str(prefix)+suffix).read_text()
    controls()
    corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text());rows=[]
    src=read_edges(source['edgefile']);assert len(src)==56
    for i,r in enumerate(corpus):
        d=detector(*r[:2]);es,_=blowup(*r[:2]);d.update(index=i,g6=r[0],w=r[1],n=sum(r[1]),m=len(es))
        if d['verdict']=='MAP':
            m=d['mapping'];assert len(set(m.values()))==12 and set(m)==set(range(12))
            assert all(tuple(sorted((m[u],m[v]))) in set(es) for u,v in src)
            d['independent_source_edges_checked']=56
        rows.append(d);save(ROOT/'local_transfer_detection.json',rows)
    print('Local detector271 complete;',sum(r['verdict']=='MAP' for r in rows),'maps',flush=True)

def accept():
    heavy,source_record,_=effective_heavy();assert heavy['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'
    assert json.loads((ROOT/'BASELINE_PASS.json').read_text())['cold_S008_full']==3
    old=set(json.loads(Path('validation/S008/SUMMARY.json').read_text())['excluded_indices'])
    rows=[];consecutive=0;(ROOT/'local_transfer_targets').mkdir(exist_ok=True)
    for d in json.loads((ROOT/'local_transfer_detection.json').read_text()):
        if d['verdict']!='MAP' or d['index'] in old:continue
        row=dict(d,verdict='UNKNOWN')
        if consecutive>=2:row['reason']='NOT_RUN after two consecutive FINAL checker failures'
        else:
            try:
                es,_=blowup(d['g6'],d['w']);src=read_edges(str(ROOT/'targets/K7-I5.edges'))
                m={int(k):v for k,v in d['mapping'].items()}
                assert set(m)==set(range(12)) and len(set(m.values()))==12
                assert all(tuple(sorted((m[u],m[v]))) in set(es) for u,v in src)
                ef=ROOT/'local_transfer_targets'/f"row{d['index']}.edges";ef.write_text(''.join(f'{u} {v}\n' for u,v in es),newline='\n')
                row.update(edgefile=str(ef),edge_sha256=sha(ef),fresh_chromatic=s009_run.lower(d['index']),
                    source='K7-I5',source_proof=str(source_record),target=d['index'],
                    verdict='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED')
            except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
            consecutive=consecutive+1 if row['verdict']=='UNKNOWN' else 0
        rows.append(row);save(ROOT/'local_transfer_acceptance.json',rows)
        print('Local transfer',d['index'],row['verdict'],flush=True)
    if not rows:save(ROOT/'local_transfer_acceptance.json',[])

if __name__=='__main__':
    mode=sys.argv[1]
    if len(sys.argv)>2 and sys.argv[2]=='worker':globals()[mode]();raise SystemExit
    observed=ROOT/('local_'+mode+'_observed_launch.json');assert not observed.exists()
    _,source_record,_=effective_heavy()
    files=['tools/s009_local_transfer.py','tools/s009_heavy_evidence.py','tools/s009_run.py','tools/s005_search.py','tools/blowup_graph.py',
           str(source_record),'validation/S003/survivors_alpha_ge3.json','campaigns/CAM-0010.md']
    snap=ROOT/'launch_snapshots'/('local_'+mode);snap.mkdir(parents=True,exist_ok=True)
    for f in files:(snap/(Path(f).name+'.txt')).write_bytes(Path(f).read_bytes())
    native=json.loads((ROOT/'environment.json').read_text())['native_sha256']
    for name,exp in native.items():assert sha(Path('artifacts/tmp/S004')/name)==exp
    cmd=[sys.executable,'tools/s009_local_transfer.py',mode,'worker']
    save(observed,dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sha256={p:sha(p) for p in files},native_sha256=native,grade='OBSERVED_BEFORE_LAUNCH'))
    r=run_logged(cmd,320 if mode=='detect' else 7200,ROOT/('local_'+mode+'_driver.log'))
    save(ROOT/('local_'+mode+'_command.json'),r);print(mode,r,flush=True);assert r['returncode']==0
