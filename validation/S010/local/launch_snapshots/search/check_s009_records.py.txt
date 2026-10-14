"""Independent standard-library label expansion and accepted certificate-chain audit."""
import datetime,gzip,hashlib,json,sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
from s009_heavy_evidence import effective_heavy
ROOT=Path('validation/S009')

def graph6_edges(code):
    assert not code.startswith('>>')
    data=[ord(c)-63 for c in code];n=data[0];assert 0<=n<=8 and all(0<=x<64 for x in data[1:])
    bits=[(x>>shift)&1 for x in data[1:] for shift in range(5,-1,-1)]
    assert len(bits)>=n*(n-1)//2
    edges=set();pos=0
    for b in range(1,n):
        for a in range(b):
            if bits[pos]:edges.add((a,b))
            pos+=1
    return n,edges

def labelled(row):
    code,w,_=row;n,base=graph6_edges(code);assert len(w)==n and all(x>0 for x in w)
    bag=[i for i,x in enumerate(w) for _ in range(x)]
    edges={(a,b) for a in range(len(bag)) for b in range(a+1,len(bag))
           if bag[a]==bag[b] or tuple(sorted((bag[a],bag[b]))) in base}
    return len(bag),edges

def file_edges(path):
    return {tuple(map(int,line.split())) for line in Path(path).read_text().splitlines() if line.strip()}

def proof_chain(rec,prefix):
    assert rec['solve']['returncode']==20 and rec['check']['returncode']==0
    assert rec['core_check']['returncode']==0 and rec['cold_retained_check']['returncode']==0
    assert sha(rec['archive'])==rec['archive_sha256']
    raw=gzip.decompress(Path(rec['archive']).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==rec['archive_raw_sha256']
    assert hashlib.sha256(gzip.decompress(Path(str(prefix)+'.cnf.gz').read_bytes())).hexdigest()==rec['cnf_sha256']
    for suffix in ('.check.log','.trim.log','.core.check.log','.cold.check.log'):
        assert 's VERIFIED' in Path(str(prefix)+suffix).read_text()

def lower_chain(rec,edges,n):
    idx=rec['index'];c=rec['ten_colouring'];assert len(c)==n and all(0<=x<10 for x in c)
    assert all(c[u]!=c[v] for u,v in edges)
    inherited=json.loads(Path('validation/S004/chi10_results.json').read_text())[idx]
    assert rec['cnf_sha256']==inherited['bag']['cnf_sha256'] and rec['proof_sha256']==inherited['bag']['drat_sha256']
    assert rec['command']['returncode']==0 and 's VERIFIED' in (ROOT/f'accepted-chi-row{idx}.check.log').read_text()

def worker():
    from blowup_graph import blowup
    corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    graphs={}
    for i,r in enumerate(corpus):
        n,edges=labelled(r);assert edges==set(blowup(*r[:2])[0]);graphs[i]=(n,edges)
    full=json.loads((ROOT/'full/results.json').read_text());sources={}
    for row in full:
        idx=row['target']['index'];n,edges=graphs[idx];t=row['target']
        assert (n,len(edges))==(t['n'],t['m']) and 6*n-12-len(edges)==t['D']==2
        assert file_edges(t['edgefile'])==edges and sha(t['edgefile'])==t['edge_sha256']
        if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
            proof_chain(row['certificate'],ROOT/'full/search'/f'cover-row{idx}')
            lower_chain(row['fresh_chromatic'],edges,n);sources[idx]=edges
    heavy,heavy_record,heavy_prefix=effective_heavy()
    se={(a,b) for a in range(7) for b in range(a+1,7)}|{(a,b) for a in range(7) for b in range(7,12)}
    assert file_edges(heavy['edgefile'])==se and sha(heavy['edgefile'])==heavy['edge_sha256']
    colours=list(range(7))+[7]*5;clique=list(range(8))
    assert all(colours[a]!=colours[b] for a,b in se)
    assert {(a,b) for a in clique for b in clique if a<b}<=se
    save(ROOT/'LOCAL_EXACT_CHI8.json',dict(num_vertices=12,edges=sorted(se),coloring=colours,
        chromatic_number=8,clique_lower=clique,
        lower_proof='Every proper colouring of a K8 gives its eight pairwise-adjacent vertices eight distinct colours.',
        biplanarity=heavy['verdict'],not_a_headline_lower_bound_witness=True))
    if heavy['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
        proof_chain(heavy['certificate'],heavy_prefix);sources['K7-I5']=se
    checked=[]
    for name in ('transfer_acceptance_rows.json','new_transfer_acceptance.json','local_transfer_acceptance.json'):
        p=ROOT/name
        if not p.exists():continue
        for row in json.loads(p.read_text()):
            if row['verdict']!='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED':continue
            source=row['source'];target=row['target'];n,edges=graphs[target]
            if source=='K7-I5':ss=sources[source]
            elif source in sources:ss=sources[source]
            else:ss=graphs[source][1];assert source in json.loads(Path('validation/S008/SUMMARY.json').read_text())['excluded_indices']
            m={int(k):int(v) for k,v in row['mapping'].items()};ns=12 if source=='K7-I5' else graphs[source][0]
            assert set(m)==set(range(ns)) and len(set(m.values()))==ns and all(0<=v<n for v in m.values())
            assert all(tuple(sorted((m[u],m[v]))) in edges for u,v in ss)
            assert file_edges(row['edgefile'])==edges and sha(row['edgefile'])==row['edge_sha256']
            lower_chain(row['fresh_chromatic'],edges,n)
            checked.append(dict(source=source,target=target,source_edges=len(ss),labels=ns))
    save(ROOT/'INDEPENDENT_RECORD_AUDIT_PASS.json',dict(verdict='PASS',independent_graph6_pairwise_expansions=271,
        direct_sources=[str(s) for s in sources],accepted_transfers_checked=checked,
        partials_not_promoted=True,shared_native_checker_dependency=True))
    print('PASS independent271 label expansions and all accepted native/colour/map chains',flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker();raise SystemExit
    p=ROOT/'record_audit_observed_launch.json';assert not p.exists()
    files=['tools/check_s009_records.py','tools/s005_search.py','tools/blowup_graph.py',
           'validation/S009/full/results.json','validation/S009/heavy/result.json','campaigns/CAM-0010.md']
    cmd=[sys.executable,'tools/check_s009_records.py','worker']
    save(p,dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sha256={f:sha(f) for f in files},grade='OBSERVED_BEFORE_LAUNCH'))
    r=run_logged(cmd,3600,ROOT/'record_audit_driver.log');save(ROOT/'record_audit_command.json',r)
    print(r,flush=True);assert r['returncode']==0
