"""Small independent controls for telemetry and proof-backed region accounting."""
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_s032 import write_inst
from check_s032_native import lemmas
from s032_coverage import partition, weight, formula, check, report
import networkx as nx


def main():
    start=time.monotonic()
    out=ROOT/'artifacts/tmp/S032'/(sys.argv[1] if len(sys.argv)>1 else 'progress-controls');out.mkdir(exist_ok=False)
    os.environ['PATH']=str(ROOT/'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64/bin')+os.pathsep+os.environ['PATH']
    exe=ROOT/'artifacts/tmp/S032/native-progress/bipsat_s032.exe'
    rows=[]
    def fixed(n,parts,name):
        pairs=list(itertools.combinations(range(n),2));parts=list(map(set,parts))
        clauses=[[2*i+k+1 if e in parts[k] else -(2*i+k+1)] for i,e in enumerate(pairs) for k in (0,1)]
        inst=out/(name+'.inst');write_inst(inst,n,pairs,clauses,2*len(pairs))
        lp=out/(name+'.lem')
        p=subprocess.run([str(exe),str(inst),'--timeout','5','--lemmas',str(lp)],capture_output=True,text=True,timeout=10)
        expected=all(nx.check_planarity(nx.Graph(es))[0] for es in parts)
        assert p.returncode==(10 if expected else 20),(name,p.stdout,p.stderr)
        count=lemmas(lp,n,pairs)
        if not expected:assert count>0
        (out/(name+'.log')).write_text(p.stdout+p.stderr)
        if name in ['n5-0','n5-1023','K33','positive24']:rows.append(dict(name=name,returncode=p.returncode,checked_rules=count))
    pairs=list(itertools.combinations(range(5),2))
    for mask in range(1024):fixed(5,[[e for i,e in enumerate(pairs) if mask>>i&1],[]],f'n5-{mask}')
    fixed(6,[list(itertools.product(range(3),range(3,6))),[]],'K33')
    positive=json.loads((ROOT/'validation/S030/POSITIVE24.json').read_text())
    fixed(24,[list(map(tuple,positive['E1'])),list(map(tuple,positive['E2']))],'positive24')
    # Bounded free-K9 stress specifically exercises periodic internal telemetry.
    src=ROOT/'artifacts/tmp/S032/controls-v3/K9.inst';lp=out/'K9.lem'
    p=subprocess.run([str(exe),str(src),'--timeout','2','--lemmas',str(lp)],capture_output=True,text=True,timeout=10)
    (out/'K9.log').write_text(p.stdout+p.stderr)
    assert p.returncode in (0,20) and 'S032_LOGIC conflicts=' in p.stdout,p.stdout
    import re
    logic=re.findall(r'S032_LOGIC conflicts=(\d+) decisions=(\d+) propagations=(\d+)',p.stdout)
    assert len(logic)>=2 and int(logic[-1][0])>0 and int(logic[-1][1])>0,logic
    k9=lemmas(lp,9,list(itertools.combinations(range(9),2)))
    # Tiny three-edge projection: all m1/m2 sets (six); two false pins leave one.
    toy=out/'toy';toy.mkdir();base=toy/'base.cnf'
    base.write_text('p cnf 3 2\n-1 0\n-2 0\n')
    cells=partition([1,2,3],{},2,1,2)
    assert [int(c['weight']) for c in cells]==[1,2,2,1]
    assert sum(int(c['weight']) for c in cells)==weight(3,0,1,2)==6
    d=dict(files={'base':str(base)},sha256={'base':hashlib.sha256(base.read_bytes()).hexdigest()},
        cells=cells,variables=3,base_clauses=2,retained_clauses=0,total_region_weight='6',
        raw_edge_set_count='6',include_retained_rules=False,meaning='toy projection',warning='control only')
    (toy/'coverage.json').write_text(json.dumps(d))
    check(toy,1,10);report(toy)
    checked=json.loads((toy/'REPORT.json').read_text())
    assert checked['proof_closed_region_weight']=='2' and checked['unresolved_region_weight']=='4'
    check(toy,0,10)
    td=json.loads((toy/'coverage.json').read_text())
    assert td['cells'][0]['status']=='RELAXATION_SAT_NOT_A_PLANAR_WITNESS'
    # A damaged certificate cannot contribute to the reported coverage.
    proof=next(Path(p) for p in td['cells'][1]['certificate'] if p.endswith('.drat'))
    old=proof.read_bytes();proof.write_bytes(old+b'corrupt')
    try:
        try:report(toy)
        except AssertionError:pass
        else:raise AssertionError('damaged proof accepted')
    finally:proof.write_bytes(old)
    result=dict(status='PASS',native_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
        exhaustive_n5=1024,K33='PASS',positive24='PASS',telemetry='PASS',rows=rows,
        free_K9='UNKNOWN_AT_2S' if p.returncode==0 else 'UNSAT_CONTROL_ONLY',free_K9_checked_rules=k9,
        toy_disjoint_weights_and_checked_UNSAT='PASS',toy_SAT_not_counted_as_closed='PASS',
        damaged_proof_rejected=True,seconds=time.monotonic()-start,
        whole_stratum_certified=False,witness_established=False)
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
