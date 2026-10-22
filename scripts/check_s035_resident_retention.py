"""Real native identity/CDCL retention, paused CPU, immutable deltas and eviction controls."""
import json
from pathlib import Path
import re
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from verify_s035_resident_scheduler import fixture
from s035_resident_engine import Campaign,recover
from s035_regions import claim,sha,live_identity
from s035_windows import atomic_json,read_json,tree_sample
OUT=ROOT/'artifacts/tmp/S035/resident-acceptance'

def main():
    root=OUT/('retention-'+str(time.time_ns()))
    area,cfg=fixture(root,n=9,seconds=90)
    cfg.update(resident_turn_seconds=6,disable_congruence=True,disable_random_walk=False)
    atomic_json(area/'CONFIG.json',cfg)
    campaign=Campaign(area)
    try:
        first=claim(area,0);campaign.visit(first)
        ctx=read_json(area/'RESIDENT_CONTEXTS.json')['contexts']['0'];assert ctx['state']=='PARKED'
        worker=ctx['worker'];pid=worker['pid'];before=tree_sample(pid)['cpu']
        time.sleep(.5);assert tree_sample(pid)['cpu']-before<.05
        rows=read_json(area/'REGIONS.json')['accepted_cuts'];assert rows
        original=[(r['path'],r['sha256']) for r in rows]
        log=Path(ctx['directory'])/'native.log'
        before_conflicts=[int(x) for x in re.findall(r'conflicts=(\d+)',log.read_text())][-1]
        second=claim(area,0);campaign.visit(second)
        ctx2=read_json(area/'RESIDENT_CONTEXTS.json')['contexts']['0']
        assert ctx2['worker']['pid']==pid and ctx2['worker']['start_ticks']==worker['start_ticks'] and ctx2['turns']==2
        after_conflicts=[int(x) for x in re.findall(r'conflicts=(\d+)',log.read_text())][-1]
        assert after_conflicts>=before_conflicts>0
        for path,digest in original:assert sha(path)==digest
        # Budget pressure may evict RAM state, but never the immutable semantic evidence.
        campaign.config['resident_cache_private_bytes']=1
        campaign.evict_if_needed()
        assert not campaign.contexts and not live_identity(pid,worker['start_ticks'])
        assert read_json(area/'RESIDENT_CONTEXTS.json')['contexts']=={}
        for path,digest in original:assert sha(path)==digest
        value=dict(status='PASS',same_pid_and_create_time_across_turns=True,turns=2,
            paused_cpu_seconds_under_005=True,conflicts_before=before_conflicts,conflicts_after=after_conflicts,
            original_delta_hashes_unchanged=True,memory_eviction_kills_only_parked_identity=True,
            semantic_checkpoints_retained=True,native_sha256=sha(cfg['native']),directory=str(area))
        atomic_json(OUT/'RETENTION_CONTROLS.json',value);print(json.dumps(value),flush=True)
    finally:recover(area)

if __name__=='__main__':main()
