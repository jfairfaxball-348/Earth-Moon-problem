"""Two independent exact arithmetic checks for the all-order mixed-charge proof."""
import datetime,itertools,json,sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
ROOT=Path('validation/S009')
TYPES=[('K8-end',7,13,4),('C11-end',10,7,4),('C9-end',8,3,2),('C9-whole',9,5,3),('C7-whole',7,1,1)]
SCALE=1365

def worker():
    rows=[];vectors=0
    for q in range(16):
        cap=q+12
        rewards=[SCALE*c*min(q,d)//d for _,w,d,c in TYPES]
        assert all(SCALE*c*min(q,d)%d==0 for _,w,d,c in TYPES)
        best=-1;witness=None;admissible=0
        for rs in itertools.product(range(4),repeat=5):
            vectors+=1
            if sum(w*r for (_,w,_,_),r in zip(TYPES,rs))>cap:continue
            admissible+=1;score=sum(v*r for v,r in zip(rewards,rs))
            if score>best:best=score;witness=rs
        # Independently ordered capacity recursion; no copied multiplicity enumeration.
        dp=[0]*(cap+1)
        for capacity in range(cap+1):
            for (_,weight,_,_),reward in zip(TYPES,rewards):
                if weight<=capacity:dp[capacity]=max(dp[capacity],dp[capacity-weight]+reward)
        assert best==dp[cap] and best<=SCALE*q
        rows.append(dict(q=q,capacity=cap,best_scaled=best,scale=SCALE,
            witness_multiplicities=witness,admissible_vectors=admissible,independent_knapsack_scaled=dp[cap]))
    save(ROOT/'mixed_charge_controls.json',dict(types=TYPES,scale=SCALE,q_domain=[0,15],
        multiplicity_domain=[0,3],cartesian_vectors_checked=vectors,rows=rows,
        verdict='PASS',large_q='ANALYTIC_NOT_ENUMERATED'))
    print('PASS16384 finite vectors and16 independent integer knapsacks',flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker();raise SystemExit
    p=ROOT/'mixed_charge_observed_launch.json';assert not p.exists()
    files=['tools/s009_mixed_charge.py','tools/s005_search.py','tools/s005_replay.py','campaigns/CAM-0010.md']
    cmd=[sys.executable,'tools/s009_mixed_charge.py','worker']
    snap=ROOT/'launch_snapshots/mixed_charge';snap.mkdir(parents=True,exist_ok=True)
    for f in files:(snap/(Path(f).name+'.txt')).write_bytes(Path(f).read_bytes())
    save(p,dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sha256={f:sha(f) for f in files},types=TYPES,scale=SCALE,grade='OBSERVED_BEFORE_LAUNCH'))
    r=run_logged(cmd,200,ROOT/'mixed_charge_driver.log');save(ROOT/'mixed_charge_command.json',r)
    print(r,flush=True);assert r['returncode']==0
