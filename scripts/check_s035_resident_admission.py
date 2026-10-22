"""A full resident batch must reuse retained contexts rather than cycle through cold ones."""
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from verify_s035_resident_scheduler import fixture
from s035_resident_engine import Campaign
from s035_regions import release,recover
from s035_windows import atomic_json

area,cfg=fixture(ROOT/'artifacts/tmp/S035/resident-acceptance'/('admission-'+str(time.time_ns())))
campaign=Campaign(area)
campaign.contexts={str(i):dict(state='PARKED',cell=i) for i in range(4)}
cells=[]
try:
    for i in range(4):
        c=campaign.claim_resident(i);assert c['id'] in range(4);cells.append(c)
    assert len({c['id'] for c in cells})==4
    assert campaign.claim_resident(5) is None,'Cold fifth context must not displace retained learning'
    for c in cells:release(area,c['id'],c['claim']['token'])
    c=campaign.claim_resident(0)
    assert c['id'] in range(4)
    release(area,c['id'],c['claim']['token'])
    atomic_json(ROOT/'artifacts/tmp/S035/resident-acceptance/ADMISSION_CONTROLS.json',dict(status='PASS',
        batch_limit=4,only_resident_contexts_claimed_when_full=True,claimed_reservations_counted=True,
        cold_fifth_context_not_admitted=True,directory=str(area)))
    print('PASS bounded resident admission prevents cache-size-plus-one thrashing')
finally:recover(area)
