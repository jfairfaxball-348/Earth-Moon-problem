"""Install bounded resident admission after the genuine S035 memory pilot."""
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_windows import read_json,atomic_json
from s035_regions import report,sha

area=ROOT/'artifacts/tmp/S035/campaign';gate=ROOT/'artifacts/tmp/S035/resident-acceptance'
assert report(area)['status']=='STOPPED' and not report(area)['active']
assert read_json(gate/'ADMISSION_CONTROLS.json')['status']=='PASS'
controls=read_json(gate/'SCHEDULER_CONTROLS.json');assert controls['status']=='PASS'
for name,digest in controls['source_sha256'].items():assert sha(ROOT/name)==digest,name
shutil.copytree(ROOT/'validation/S035/resident',ROOT/'validation/S035/resident-pilot',dirs_exist_ok=False)
dest=ROOT/'validation/S035/resident-pilot'
for name in ('CONFIG.json','REGIONS.json','RESIDENT_CONTEXTS.json','JOURNAL.jsonl','STOPPED.json'):
    shutil.copy2(area/name,dest/('FINAL_'+name))
for name in ('RUNNING.md','RUNNING_MANIFEST.json'):shutil.copy2(ROOT/'sessions/S035'/name,dest/name)
cfg=read_json(area/'CONFIG.json')
cfg.update(execution_revision='S035_RESIDENT_V2',resident_max_contexts=4,resident_admission_bytes=1024**3,
    scheduling='Bounded resident batch; prioritize retained learning; cold regions remain queued until capacity opens')
for name in cfg['source_sha256']:cfg['source_sha256'][name]=sha(ROOT/name)
cfg['source_sha256']['scripts/reconfigure_s035_resident_batch.py']=sha(Path(__file__))
atomic_json(area/'CONFIG.json',cfg)
(area/'STOP').rename(area/'STOP.resident-pilot-memory-adjustment')
atomic_json(area/'CONTROLLER.json',dict(status='READY',deadline=None,workers=2,verdict='UNKNOWN'))
with (area/'resident-launcher.log').open('a') as log:
    p=subprocess.Popen([sys.executable,str(ROOT/'scripts/s035_resident_campaign.py'),'guard'],stdout=log,stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
print('Launched S035 resident V2 with two active slots and at most four retained contexts; PID',p.pid)
