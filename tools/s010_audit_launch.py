"""Capture/supervise the final independent mathematical record audit."""
import datetime, sys
from pathlib import Path
from s005_search import run_logged
from s005_replay import sha
from s007_run import save
root=Path('validation/S010');record=root/'audit_observed_launch.json';assert not record.exists()
files=['tools/check_s010_records.py','tools/check_rotation.py','tools/s005_search.py','validation/S010/SUMMARY.json',
       'validation/S010/cold_replay.json','validation/S010/chromatic_cold_replay.json','validation/S010/local/results.json',
       'validation/S010/bipartite_detector.json','validation/S010/safe_pair_audit.json','catalogue/SOURCES.json','catalogue/CLAIMS.json',
       'catalogue/SOURCES.md','catalogue/CLAIMS.md','campaigns/CAM-0011.md']
snap=root/'launch_snapshots/audit';snap.mkdir(parents=True)
for f in files:
    if f.endswith('.py'):snap.joinpath(Path(f).name+'.txt').write_bytes(Path(f).read_bytes())
cmd=[sys.executable,'tools/check_s010_records.py']
save(record,dict(grade='OBSERVED_BEFORE_LAUNCH',as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 command=cmd,sha256={f:sha(f) for f in files}))
r=run_logged(cmd,3600,root/'audit_driver.log');save(root/'audit_command.json',r);print(r);assert r['returncode']==0
