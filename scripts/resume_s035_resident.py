"""S035 maintenance migration: keep ledger/evidence, replace execution policy only."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_windows import atomic_json,read_json
from s035_regions import sha,report,validate_partition

def main():
    runtime=ROOT/'artifacts/tmp/S035';area=runtime/'campaign';gate=runtime/'resident-acceptance'
    assert report(area)['status']=='STOPPED' and not report(area)['active']
    prior=ROOT/'validation/S035/pre-resident'
    assert read_json(prior/'ARCHIVE_VERIFICATION.json')['status']=='PASS_ALL_ORIGINAL_BYTES'
    controls=read_json(gate/'SCHEDULER_CONTROLS.json');retention=read_json(gate/'RETENTION_CONTROLS.json')
    assert controls['status']==retention['status']=='PASS'
    diagnostic=read_json(runtime/'phase-diagnostic/SUMMARY.json')
    cfg=read_json(area/'CONFIG.json');data=read_json(area/'REGIONS.json')
    native=runtime/'native-resident/bipsat_s032.exe';digest=sha(native)
    for name in ('NATIVE_CONTROLS_DEFAULT.json','NATIVE_CONTROLS_CONGRUENCE_DISABLED.json'):
        value=read_json(gate/name);assert value['native_sha256']==digest and value['exhaustive_n5_fixed_graphs']==1024
        assert value['K33']==value['positive24']=='PASS'
    assert controls['native_sha256']==retention['native_sha256']==digest
    for name,h in controls['source_sha256'].items():assert sha(ROOT/name)==h,name
    assert read_json(gate/'SMOKE.json')['verdict']=='PASS'
    assert all(c['claim'] is None for c in data['cells']) and validate_partition(cfg,data['cells'])
    # Original execution receipts remain unchanged in the snapshot and original validation tree.
    for name in ('CONFIG.json','REGIONS.json','GUARDIAN.json','CONTROLLER.json','STOPPED.json','JOURNAL.jsonl'):
        shutil.copy2(area/name,prior/('MAINTENANCE_'+name))
    for name in ('RUNNING.md','RUNNING_MANIFEST.json'):
        shutil.copy2(ROOT/'sessions/S035'/name,prior/name)
    cfg.update(native=str(native),native_sha256=digest,execution_revision='S035_RESIDENT_V1',
        controller_entry='scripts/s035_resident_campaign.py',workers=2,
        resident_turn_seconds=600,resident_pilot_turn_seconds=15,resident_proof_seconds=1800,
        resident_cache_private_bytes=5*1024**3,resident_available_floor_kib=2560*1024,
        disable_congruence=diagnostic['disable_congruence'],disable_random_walk=False,
        private_cdcl_policy='RAM_ONLY_PER_REGION_PRESERVED_ACROSS_TURNS; SEMANTIC_ONLY_AFTER_PROCESS_LOSS',
        migration_one_time_cdcl_loss='Prior executable has no export API; all semantic checkpoints and proof evidence preserved')
    names=['tools/s035_resident_engine.py','scripts/s035_resident_campaign.py','scripts/build_s035_resident_native.py',
           'scripts/resume_s035_resident.py','scripts/diagnose_s035_phases.py']
    for name in names:cfg['source_sha256'][name]=sha(ROOT/name)
    atomic_json(area/'CONFIG.json',cfg)
    atomic_json(area/'UPGRADE.json',dict(status='RESIDENT_UPGRADE_LAUNCH',utc_epoch=time.time(),
        original_config_sha256=sha(prior/'CONFIG.json'),new_config_sha256=sha(area/'CONFIG.json'),
        original_runtime_archive_verified=True,private_cdcl_retained_across_new_turns=True,no_S036=True))
    (area/'STOP').rename(area/'STOP.pre-resident-maintenance')
    atomic_json(area/'CONTROLLER.json',dict(status='READY',deadline=None,workers=2,verdict='UNKNOWN'))
    with (area/'resident-launcher.log').open('a') as log:
        p=subprocess.Popen([sys.executable,str(ROOT/'scripts/s035_resident_campaign.py'),'guard'],stdout=log,stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
    print(json.dumps(dict(launcher_pid=p.pid,workers=2,revision=cfg['execution_revision'],disable_congruence=cfg['disable_congruence'])),flush=True)

if __name__=='__main__':main()
