"""Immutable prelaunch hashes/snapshots and externally supervised workers."""
import datetime, json, sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save

mode=sys.argv[1]
root=Path('validation/S009');tmp=Path('artifacts/tmp/S009')
root.mkdir(exist_ok=True);tmp.mkdir(parents=True,exist_ok=True)
record=root/(mode+'_observed_launch.json')
assert not record.exists(), 'Never overwrite observed launch provenance'
files=sorted(set(str(p).replace('\\','/') for p in Path('tools').glob('s009*.py')) |
    {'tools/s007_run.py','tools/s005_replay.py','tools/s005_search.py','tools/s006_run.py',
     'tools/s008_cover.py','tools/s008_tree.py','tools/s007_cover.py','tools/triangulation_cover.py',
     'tools/check_layers.py','tools/check_rotation.py','tools/blowup_graph.py','tools/blowup_chi_cnf.py',
     'validation/S003/survivors_alpha_ge3.json','validation/S004/chi10_results.json',
     'validation/S008/SUMMARY.json','campaigns/CAM-0010.md'})
native=json.loads(Path('validation/S008/environment.json').read_text())['native_sha256']
for name,expected in native.items():assert sha(Path('artifacts/tmp/S004')/name)==expected
snap=root/'launch_snapshots'/mode;snap.mkdir(parents=True,exist_ok=True)
hashes={p:sha(p) for p in files}
for p in files:
    if p.endswith('.py'):(snap/(Path(p).name+'.txt')).write_bytes(Path(p).read_bytes())
caps={'baseline':10800,'injection_controls':200,'transfer':320,'prepare':200,
      'full':14400,'heavy_controls':920,'heavy':6600,'upper':200,'audit':3600}
cmd=[sys.executable,'tools/s009_run.py',mode]
save(record,dict(as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    command=cmd,hard_cap=caps[mode],sha256=hashes,native_sha256=native,
    snapshots=str(snap),grade='OBSERVED_BEFORE_LAUNCH'))
result=run_logged(cmd,caps[mode],root/(mode+'_driver.log'))
save(root/(mode+'_driver_command.json'),result)
print(mode,result,flush=True)
assert result['returncode']==0
