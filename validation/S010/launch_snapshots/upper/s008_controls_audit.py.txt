"""Independent finite clause-family enumeration and supervised truth repeat."""
import itertools
import json
import math
import shutil
import sys
from pathlib import Path
from s005_search import run_logged
from s005_replay import sha
from s007_run import save
from s008_cover import obstructions

ROOT=Path('validation/S008')
save(ROOT/'controls_audit_launch_hashes.json',{p:sha(p) for p in (
    'tools/s008_controls_audit.py','tools/s008_run.py','tools/s008_cover.py','tools/s005_search.py')})
for name in ('new_clause_controls.json','controls_launch_hashes.json'):
    shutil.copyfile(ROOT/name,ROOT/('initial_'+name))
rows=[]
for idx,row in enumerate(json.loads(Path('validation/S007/static_truth_controls.json').read_text())):
    n=row['n'];edges={tuple(e) for es in row['completion_edges'] for e in es}
    brute=set()
    for six in itertools.combinations(range(n),6):
        for first in itertools.combinations(six[1:],2):
            a=(six[0],)+first;b=tuple(v for v in six if v not in a)
            cross=tuple(sorted(tuple(sorted((u,v))) for u in a for v in b))
            if set(cross)<=edges:brute.add(cross)
    generated=list(obstructions(n,sorted(edges)))
    k5=[es for kind,es in generated if kind=='K5']
    k33=[es for kind,es in generated if kind=='K33']
    assert len(k5)==math.comb(n,5) and len(k33)==len(set(k33)) and set(k33)==brute
    rows.append(dict(index=idx,n=n,K5=len(k5),K33=len(k33),independent_family_comparison='PASS'))
save(ROOT/'independent_cut_enumeration.json',rows)
run=run_logged([sys.executable,'tools/s008_run.py','controls'],920,ROOT/'supervised_controls.log')
save(ROOT/'supervised_controls_command.json',run)
assert run['returncode']==0 and len(json.loads((ROOT/'new_clause_controls.json').read_text()))==27
assert (ROOT/'initial_new_clause_controls.json').read_bytes()==(ROOT/'new_clause_controls.json').read_bytes()
print('PASS23 independently enumerated obstruction families;27 supervised truth/rotation controls')
