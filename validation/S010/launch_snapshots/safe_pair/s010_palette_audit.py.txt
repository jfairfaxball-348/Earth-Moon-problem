"""Independent exact set-colour case check of the residual safe-pair implication."""
import datetime, itertools, sys
from pathlib import Path
from s005_search import run_logged
from s005_replay import sha
from s007_run import save
ROOT=Path('validation/S010')

def good(x,y,col):
    px={col[v] for v in x};py={col[v] for v in y}
    return len(px)<len(x) or len(py)<len(y) or px!=py

def worker():
    ground=set(range(5));sets=[{v for v in ground if mask>>v&1} for mask in range(32)]
    checks=antecedents=0
    for r in sets:
        outside=sorted(ground-r)
        for vector in itertools.product(range(3),repeat=len(outside)):
            col=dict(zip(outside,vector));final=col|{v:3 for v in r}
            for x,y in itertools.combinations(sets,2):
                if len(x)!=len(y):continue
                xr,yr=len(x&r),len(y&r);rx,ry=x-r,y-r
                safe=max(xr,yr)>=2 or xr!=yr or (xr==yr and xr<=1 and rx!=ry)
                residual_required=xr==yr and xr<=1 and rx!=ry
                pre=safe and (not residual_required or good(rx,ry,col))
                checks+=1
                if pre:assert good(x,y,final);antecedents+=1
    assert antecedents>0
    save(ROOT/'safe_pair_audit.json',dict(verdict='PASS',ground_order=5,outside_colours=3,unused_R_colour=3,
                                         pair_assignment_cases=checks,satisfied_antecedent_cases=antecedents,
                                         independent_R_existence='NOT_PROVED',domain='all unequal equal-size subset pairs, all R, all outside3 assignments'))
    print('PASS',checks,'residual palette cases;',antecedents,'antecedents',flush=True)

if __name__=='__main__':
    if len(sys.argv)>1:worker();raise SystemExit
    record=ROOT/'safe_pair_observed_launch.json';assert not record.exists()
    files=['tools/s010_palette_audit.py','research/S010_SIMULTANEOUS_EXTENSION.md','campaigns/CAM-0011.md','tools/s005_search.py']
    snap=ROOT/'launch_snapshots/safe_pair';snap.mkdir(parents=True)
    for f in files:snap.joinpath(Path(f).name+'.txt').write_bytes(Path(f).read_bytes())
    cmd=[sys.executable,'tools/s010_palette_audit.py','worker']
    save(record,dict(grade='OBSERVED_BEFORE_LAUNCH',as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=cmd,sha256={f:sha(f) for f in files}))
    r=run_logged(cmd,300,ROOT/'safe_pair_driver.log');save(ROOT/'safe_pair_command.json',r);print(r);assert r['returncode']==0
