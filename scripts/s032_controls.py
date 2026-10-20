"""S032 fresh-gated independent archived replay and persistent-solver controls."""
import gzip
import itertools as it
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from pysat.solvers import Solver

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s026_supervision import atomic_json
from s030_op1b import encode,controls
from replay_s030_search import audit
from check_s030_math import naive_rup


def main():
    out=ROOT/'artifacts/tmp/S032';out.mkdir(parents=True,exist_ok=True)
    smoke=json.loads((out/'SMOKE.json').read_text())
    assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==271
    start=time.monotonic()
    archived=[audit(ROOT/f'validation/S030/{p}') for p in ('pilot','strong','sorted')]
    atomic_json(out/'S030_REPLAY.json',archived)
    target=out/'rup';target.mkdir(exist_ok=True)
    src=ROOT/'validation/S030/prior_art/paper59/regular'
    for name in ('encode.py','branch_formulas.py','verify_rup.py','regular566_rup.json'):
        shutil.copy2(src/name,target/name)
    r=subprocess.run([sys.executable,str(target/'verify_rup.py')],capture_output=True,text=True,timeout=120)
    (out/'rup-check.log').write_text(r.stdout+r.stderr,encoding='utf-8',newline='\n');assert r.returncode==0
    sys.path.insert(0,str(target))
    from branch_formulas import formula
    packet=json.loads((target/'regular566_rup.json').read_text())
    for row in packet['branches']:
        f=formula(row['q']);clauses=[f.clauses[i] for i in row['core_clause_indices']]
        for c in row['rup_additions']:
            assert naive_rup(clauses,c);clauses.append(c)
        assert clauses[-1]==[]
    n=0
    for degree in range(4):
        f,g,ls=encode(4,degree,0,6)
        with Solver(name='cadical300',bootstrap_with=f) as solver:
            for labels in it.product(range(3),repeat=6):
                es={e for (e,x),k in zip(g.items(),labels) if k}
                deg=[sum(v in e for e in es) for v in range(4)]
                expected=bool(es) and min(deg)>=degree and deg[0]==degree and labels[0]!=2
                ass=[]
                for (e,x),k in zip(g.items(),labels):
                    ass += [x if k else -x,ls[0][e] if k==1 else -ls[0][e],ls[1][e] if k==2 else -ls[1][e]]
                solver.conf_budget(2000);solver.dec_budget(20000)
                assert solver.solve_limited(assumptions=ass)==expected,(degree,labels)
                n+=1
    # Incrementally add contradictory clauses to one live instance; no restart.
    with Solver(name='cadical300',bootstrap_with=[[1,2]]) as solver:
        assert solver.solve();solver.add_clause([-1]);assert solver.solve()
        solver.add_clause([-2]);assert solver.solve() is False
    control_dir=out/'positive-controls';control_dir.mkdir(exist_ok=True)
    controls(control_dir)
    from s025_check import check_split
    p=json.loads((ROOT/'validation/S030/POSITIVE24.json').read_text())
    check_split(24,p['E1']+p['E2'],p['E1'],p['E2'])
    es={tuple(sorted(e)) for e in p['E1']+p['E2']}
    assert all(any(e in es for e in it.combinations(vs,2)) for vs in it.combinations(range(24),4))
    result={'status':'PASS','solver':'cadical300','persistent_n4_assignments':n,
            'incremental_clause_addition':'PASS','S030_models_replayed':sum(r['models_checked'] for r in archived),
            'S030_cut_audits':[r['cuts_checked'] for r in archived],
            'regular_rup':'THREE_BRANCHES_VERIFIED_TWICE; HAND_COVERAGE_NOT_REPROVED',
            'positive24':'PASS','known17_alpha2':'NOT_RETRIEVED; no theorem promoted',
            'seconds':time.monotonic()-start}
    atomic_json(out/'CONTROLS.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
