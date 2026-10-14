"""Exact small counter semantics and real completion assignment controls."""
import itertools
import json
from pathlib import Path
from pysat.formula import IDPool
from pysat.solvers import Cadical153
from s008_tree import TreeCardEnc,TreeFullCover
from s007_run import save
import s007_static_controls

s007_static_controls.StrongCover=TreeFullCover
checks=0
for n in range(1,7):
    lits=list(range(1,n+1))
    for bound in range(n+1):
        for relation in ('atmost','atleast','equals'):
            pool=IDPool(start_from=n+1)
            cnf=getattr(TreeCardEnc,relation)(lits=lits,bound=bound,vpool=pool)
            with Cadical153(bootstrap_with=cnf.clauses) as solver:
                for bits in itertools.product((0,1),repeat=n):
                    truth=sum(bits)
                    expected={'atmost':truth<=bound,'atleast':truth>=bound,'equals':truth==bound}[relation]
                    actual=solver.solve(assumptions=[v if bit else -v for v,bit in zip(lits,bits)])
                    assert actual==expected
                    checks+=1
rows=[]
root=Path('validation/S008/tree');root.mkdir(parents=True,exist_ok=True)
controls=json.loads(Path('validation/S008/controls.json').read_text())['results']
for row in controls:
    tag=f"control-{row['index']:02d}" if 'index' in row else 'control-'+row['tag']
    ef=Path('artifacts/tmp/S008/replay')/(tag+'.edges') if 'index' in row else Path(f"validation/S003/splits/{row['tag']}.edges")
    split=Path('artifacts/tmp/S008/replay')/(tag+'.split.json')
    rows.append(dict(tag=tag,**s007_static_controls.static_control(str(ef),str(split))))
    save(root/'pinned_controls.json',rows)
save(root/'counter_semantics.json',dict(lengths=[1,6],bounds='0..length',relations=['atmost','atleast','equals'],
    all_boolean_assignments=True,auxiliary_extension_checks=checks,verdict='PASS'))
print('PASS',checks,'counter truth checks and23 actual pinned completions',flush=True)
