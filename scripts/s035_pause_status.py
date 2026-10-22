"""Read-only pause status. Never launch, recover, resume or terminate a process."""
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s035_windows import read_json,live_identity,tree_sample
area=ROOT/'artifacts/tmp/S035/campaign';pause=read_json(area/'OWNER_PAUSE.json')
import psutil
rows=[]
for p in pause['processes']:
    alive=live_identity(p['pid'],p['start_ticks'])
    rows.append(dict(**p,identity_alive=alive,suspended=alive and psutil.Process(p['pid']).status()==psutil.STATUS_STOPPED))
before={p['pid']:tree_sample(p['pid'])['cpu'] for p in rows if p['identity_alive']};time.sleep(.2)
for p in rows:
    if p['identity_alive']:p['cpu_delta']=tree_sample(p['pid'])['cpu']-before[p['pid']]
print(json.dumps(dict(status='OWNER_PAUSED',stop_latched=(area/'STOP').exists(),processes=rows,all_surviving_processes_suspended=all(not p['identity_alive'] or p['suspended'] for p in rows),ram_retention='Only while the same suspended native identities survive',semantic_recovery='validation/S035/pause/RUNTIME_INVENTORY.json',no_heavy_work_authorized=True),indent=1))
