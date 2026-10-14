"""Gate later stages on the FINAL complete cold baseline, without editing it."""
import datetime,json,sys,time
from pathlib import Path
from s005_search import run_logged
from s007_run import save
from s005_replay import sha
ROOT=Path('validation/S009')
mode=sys.argv[1]
commands={'heavy':[sys.executable,'tools/s009_stage.py','heavy_accept'],
          'full':[sys.executable,'tools/s009_launch.py','full']}
record=ROOT/(mode+'_baseline_queue_observed.json');assert not record.exists()
save(record,dict(command=commands[mode],as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    gate='baseline driver exited0 AND final cold_S008_full3',
    sha256={p:sha(p) for p in ('tools/s009_after_baseline.py','tools/s009_stage.py','tools/s009_launch.py','tools/s009_run.py')}))
begin=time.monotonic()
while True:
    p=ROOT/'baseline_driver_command.json'
    if p.exists():
        r=json.loads(p.read_text());assert r['returncode']==0,r
        b=json.loads((ROOT/'BASELINE_PASS.json').read_text());assert b['cold_S008_full']==3
        break
    assert time.monotonic()-begin<10800,'Final baseline did not complete in registered outer budget'
    time.sleep(0.5)
print('Final cold gate PASS; starting',mode,flush=True)
r=run_logged(commands[mode],6650 if mode=='heavy' else 14500,ROOT/(mode+'_baseline_queue.log'))
save(ROOT/(mode+'_baseline_queue_command.json'),r);print(mode,r,flush=True);assert r['returncode']==0
