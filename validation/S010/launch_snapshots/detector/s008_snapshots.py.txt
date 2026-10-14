"""Retain exact executed adapters, verified against their observed launch hashes."""
import json
import shutil
from pathlib import Path
from s005_replay import sha
from s007_run import save

specs=[('validation/S008/replay_adapter_launch.json','validation/S008/replay_adapter_snapshot.py.txt'),
       ('validation/S008/baseline_launch_hash.json','validation/S008/baseline_snapshot.py.txt'),
       ('validation/S008/tree/certificate_adapter_launch.json','validation/S008/tree/certificate_adapter_snapshot.py.txt'),
       ('validation/S008/tree/search_adapter_launch.json','validation/S008/tree/search_adapter_snapshot.py.txt')]
rows=[]
for record,dest in specs:
    r=json.loads(Path(record).read_text());assert sha(r['path'])==r['sha256']
    shutil.copyfile(r['path'],dest)
    assert sha(dest)==r['sha256']
    rows.append(dict(observed_launch_record=record,snapshot=dest,sha256=r['sha256'],
        snapshot_grade='CAPTURED_AFTER_LAUNCH_MATCHES_OBSERVED_PRELAUNCH_HASH'))
save('validation/S008/adapter_snapshot_audit.json',rows)
print('PASS4 executed adapter snapshots match observed launch hashes')
