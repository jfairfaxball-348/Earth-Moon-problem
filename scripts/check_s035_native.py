"""Independent native solver controls and complete persisted-clause audit."""
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import time

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tools')]
from replay_s030_search import subdivision
from prepare_s032 import write_inst
from s025_check import check_split


def lemmas(path,n,pairs):
    if not path.exists():return 0
    count=0
    for line in path.open():
        c=list(map(int,line.split()));assert c and c[-1]==0
        c=c[:-1];assert c and all(-2*len(pairs)<=x<0 for x in c)
        assert len(set(c))==len(c)
        assert len({(-x-1)%2 for x in c})==1
        es=[pairs[(-x-1)//2] for x in c]
        assert all(0<=a<b<n for a,b in es)
        subdivision(es);count+=1
    return count


def main():
    out=ROOT/'artifacts/tmp/S035'/(sys.argv[1] if len(sys.argv)>1 else 'controls-v2');out.mkdir(exist_ok=True)
    os.environ['PATH']=str(ROOT/'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64/bin')+os.pathsep+os.environ['PATH']
    exe=ROOT/'artifacts/tmp/S035/native/bipsat_s032.exe'
    smoke=json.loads((out.parent/'SMOKE.json').read_text());assert smoke['verdict']=='PASS'
    start=time.monotonic();rows=[]
    def fixed(n,parts,name):
        pairs=list(it.combinations(range(n),2));parts=[set(map(tuple,p)) for p in parts]
        clauses=[[2*i+k+1 if e in parts[k] else -(2*i+k+1)] for i,e in enumerate(pairs) for k in (0,1)]
        path=out/(name+'.inst');write_inst(path,n,pairs,clauses,2*len(pairs))
        lemma=out/(name+'.lem');assert not lemma.exists()
        if '--reuse-fixed' in sys.argv:
            prior=out.parent/'controls-v2'
            assert path.read_bytes()==(prior/path.name).read_bytes()
            old=(prior/(name+'.log')).read_text()
            assert 's UNKNOWN' not in old
            assert re.search(r'^s (SATISFIABLE|UNSATISFIABLE)$',old,re.M)
            p=subprocess.CompletedProcess([],10 if 's SATISFIABLE' in old else 20,old,'')
            lemma=prior/(name+'.lem')
        else:
            p=subprocess.run([str(exe),str(path),'--timeout','10','--lemmas',str(lemma)],capture_output=True,text=True,timeout=15)
        (out/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8',newline='\n')
        expected=all(nx.check_planarity(nx.Graph(es))[0] for es in parts)
        assert p.returncode==(10 if expected else 20),(name,p.returncode,p.stdout,p.stderr)
        count=lemmas(lemma,n,pairs)
        if not expected:assert count>0
        return {'name':name,'expected_planar_layers':expected,'returncode':p.returncode,'checked_lemmas':count}
    # Exhaust every simple labelled graph on five vertices in one fixed layer.
    pairs=list(it.combinations(range(5),2))
    for mask in range(1024):
        row=fixed(5,[[e for i,e in enumerate(pairs) if mask>>i&1],[]],f'n5-{mask:04d}')
        if mask in (0,1023):rows.append(row)
    for seed in range(64):
        rng=random.Random(seed);pairs=list(it.combinations(range(6),2))
        labels=[rng.randrange(3) for _ in pairs]
        rows.append(fixed(6,[[e for e,k in zip(pairs,labels) if k==1],[e for e,k in zip(pairs,labels) if k==2]],f'n6-{seed:02d}'))
    rows.append(fixed(6,[[e for e in it.product(range(3),range(3,6))],[]],'K33'))
    p=json.loads((ROOT/'validation/S030/POSITIVE24.json').read_text())
    check_split(24,p['E1']+p['E2'],p['E1'],p['E2'])
    rows.append(fixed(24,[p['E1'],p['E2']],'positive24'))
    # A free K9 split exercises assignment notifications, backtracking and clauses.
    pairs=list(it.combinations(range(9),2));cs=[]
    for i in range(len(pairs)):cs.extend([[2*i+1,2*i+2],[-(2*i+1),-(2*i+2)]])
    pool=IDPool(start_from=2*len(pairs)+1)
    for k in (0,1):cs+=CardEnc.atmost([2*i+k+1 for i in range(len(pairs))],21,vpool=pool,encoding=EncType.totalizer).clauses
    cs.append([1]) # layer swap only; every split has an equivalent representative
    path=out/'K9.inst';write_inst(path,9,pairs,cs,pool.top)
    if '--reuse-k9' in sys.argv:
        prior=out.parent/'controls-v3'
        assert path.read_bytes()==(prior/'K9.inst').read_bytes()
        old=(prior/'K9.log').read_text()
        assert re.search(r'^s (UNKNOWN|UNSATISFIABLE)$',old,re.M)
        p=subprocess.CompletedProcess([],0 if 's UNKNOWN' in old else 20,old,'')
        lemma=prior/'K9.lem'
    else:
        lemma=out/'K9.lem'
        p=subprocess.run([str(exe),str(path),'--timeout','2','--lemmas',str(lemma)],capture_output=True,text=True,timeout=7)
    (out/'K9.log').write_text(p.stdout+p.stderr,encoding='utf-8',newline='\n')
    count=lemmas(lemma,9,pairs)
    assert p.returncode in (0,20) and count>0,(p.returncode,p.stdout,p.stderr)
    rows.append({'name':'free_K9','returncode':p.returncode,'checked_lemmas':count,
                 'verdict':'UNSAT_CONTROL_ONLY' if p.returncode==20 else 'UNKNOWN',
                 'coverage':'full partition universe encoded; no exhaustion from cap'})
    data={'status':'PASS' if p.returncode==20 else 'SCOPED_PASS_WITH_FREE_K9_UNKNOWN',
          'exhaustive_n5_fixed_graphs':1024,'random_n6_partitions':64,
          'prior_unconstrained_K9':'UNKNOWN_AT_60S; 94531 independently checked clauses; not a decision',
          'fixed_controls_reused_from':'controls-v2' if '--reuse-fixed' in sys.argv else None,
          'free_K9_reused_from':'controls-v3' if '--reuse-k9' in sys.argv else None,
          'positive24':'PASS','K33':'PASS','free_K9':'PASS' if p.returncode==20 else 'UNKNOWN_AT_2S','rows':rows,
          'native_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'seconds':time.monotonic()-start}
    (out.parent/'NATIVE_CONTROLS.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in data.items() if k!='rows'},indent=2))


if __name__=='__main__':main()
