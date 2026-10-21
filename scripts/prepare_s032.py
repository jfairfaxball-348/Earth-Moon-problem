"""Revalidate and bijectively remap S031 formula to optional-edge bipsat2.

Only variable names change. No encoder/coverage/symmetry restriction is added.
"""
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s030_op1b import encode
from s031_check import cut


def write_inst(path,n,pairs,clauses,nv):
    with path.open('w',encoding='utf-8',newline='\n') as f:
        f.write(f'p bipsat2 {n} {len(pairs)} {nv-2*len(pairs)} {len(clauses)}\n')
        for a,b in pairs:f.write(f'e {a} {b}\n')
        for c in clauses:f.write(' '.join(map(str,c))+' 0\n')


def main():
    out=ROOT/'artifacts/tmp/S032';out.mkdir(exist_ok=True)
    smoke=json.loads((out/'SMOKE.json').read_text());assert smoke['verdict']=='PASS'
    f,g,ls=encode(28,11,155,156,anchor=True,sorted_anchor=True)
    cuts=json.loads(gzip.decompress((ROOT/'validation/S031/search/CUTS.json.gz').read_bytes()))
    for c in cuts:cut(c,g,ls);f.append(c['clause'])
    f.to_file(str(out/'original.cnf'))
    original=gzip.decompress((ROOT/'validation/S031/search/final.cnf.gz').read_bytes())
    assert (out/'original.cnf').read_bytes()==original
    pairs=list(g);m=len(pairs);rename={}
    for i,e in enumerate(pairs):
        rename[g[e]]=2*m+i+1
        for k in (0,1):rename[ls[k][e]]=2*i+1+k
    rename.update({v:v for v in range(3*m+1,f.nv+1)})
    assert sorted(rename)==sorted(rename.values())==list(range(1,f.nv+1))
    remapped=[[rename[abs(x)]*(1 if x>0 else -1) for x in c] for c in f.clauses]
    write_inst(out/'S11.inst',28,pairs,remapped,f.nv)
    with (out/'base.cnf').open('w',encoding='utf-8',newline='\n') as h:
        h.write(f'p cnf {f.nv} {len(remapped)}\n')
        for c in remapped:h.write(' '.join(map(str,c))+' 0\n')
    data={'n':28,'pairs':pairs,'original_to_native':rename,'variables':f.nv,
          'base_clauses':len(remapped),'seed_cuts':len(cuts),
          'method':'bijective literal renaming only, no new restrictions',
          'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'original.cnf',out/'base.cnf',out/'S11.inst']}}
    (out/'INPUTS.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in data.items() if k not in ['pairs','original_to_native']},indent=2))


if __name__=='__main__':main()
