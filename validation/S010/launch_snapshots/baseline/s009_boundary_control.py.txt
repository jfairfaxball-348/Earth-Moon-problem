"""Actual12-vertex positive boundary control for the local necessary model."""
import datetime,itertools,json,sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
ROOT=Path('validation/S009');TMP=Path('artifacts/tmp/S009/boundary_control')

def worker():
    import s007_static_controls
    from s009_heavy_cover import HeavyCover
    from biplanar_cnf import read_edges
    from check_layers import main as check_split
    source=next(r for r in json.loads(Path('validation/S007/heavy_search.json').read_text()) if r['tag']=='K6-I6')
    assert source['verdict']=='BIPLANAR_CONTROL'
    ef=source['edgefile'];es=read_edges(ef)
    expected=sorted(set(itertools.combinations(range(6),2))|{(a,b) for a in range(6) for b in range(6,12)})
    assert es==expected and sha(ef)==source['edge_sha256']
    split=source['split'];sf=TMP/'K6-I6.split.json';save(sf,split);check_split(ef,str(sf))
    col=list(range(6))+[6]*6;assert all(col[a]!=col[b] for a,b in es)
    assert set(itertools.combinations(range(7),2))<=set(es)
    s007_static_controls.StrongCover=HeavyCover
    pin=s007_static_controls.static_control(ef,str(sf));assert pin['n']==12 and pin['static']['distinct_faces_enabled'] is False
    assert pin['static']['completion_K33_count']==9240
    save(ROOT/'boundary_control.json',dict(n=12,m=51,D=9,edges=es,split=split,
        proper7_colouring=col,K7_clique_lower=list(range(7)),pin=pin,verdict='PASS_BIPLANAR_EXACT_CHI7'))
    print('PASS K6-I6: actual12v/51e split/rotations/chi7 and full all-completionK33 primary pins',flush=True)

if __name__=='__main__':
    TMP.mkdir(parents=True,exist_ok=True)
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker();raise SystemExit
    record=ROOT/'boundary_control_observed_launch.json';assert not record.exists()
    files=['tools/s009_boundary_control.py','tools/s009_heavy_cover.py','tools/s007_static_controls.py',
           'tools/s005_search.py','validation/S007/heavy_search.json','validation/S007/heavy/K6-I6.edges','campaigns/CAM-0010.md']
    cmd=[sys.executable,'tools/s009_boundary_control.py','worker']
    save(record,dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sha256={f:sha(f) for f in files},grade='OBSERVED_BEFORE_LAUNCH'))
    r=run_logged(cmd,920,ROOT/'boundary_control.log');save(ROOT/'boundary_control_command.json',r)
    print(r,flush=True);assert r['returncode']==0
