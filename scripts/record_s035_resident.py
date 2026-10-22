"""Retain both launch generations and archive the S035 upgrade validation."""
import gzip
import json
from pathlib import Path
import shutil
import sys
import tarfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_windows import atomic_json,read_json
from s035_regions import sha,report

def main():
    runtime=ROOT/'artifacts/tmp/S035';gate=runtime/'resident-acceptance';out=ROOT/'validation/S035/resident';out.mkdir(exist_ok=True)
    cfg=read_json(runtime/'campaign/CONFIG.json');live=report(runtime/'campaign')
    assert live['status']=='RUNNING' and live['controller_process_alive']
    for name in ('SMOKE.json','NATIVE_CONTROLS_DEFAULT.json','NATIVE_CONTROLS_CONGRUENCE_DISABLED.json',
                 'SCHEDULER_CONTROLS.json','RETENTION_CONTROLS.json','ADMISSION_CONTROLS.json'):
        shutil.copy2(gate/name,out/name)
    shutil.copy2(runtime/'native-resident/BUILD.json',out/'BUILD.json')
    shutil.copy2(runtime/'campaign/CONFIG.json',out/'REGISTERED_CONFIG.json')
    shutil.copy2(runtime/'phase-diagnostic/SUMMARY.json',out/'DIAGNOSTIC.json')
    atomic_json(out/'LAUNCH_SNAPSHOT.json',live)
    atomic_json(out/'RESIDENT_LIVE_SNAPSHOT.json',read_json(runtime/'campaign/RESIDENT_CONTEXTS.json'))
    with tarfile.open(out/'native-and-sources.tar.gz','w:gz') as tf:
        for name in ('bipsat_s032.exe','bipsat_s032.cpp','solver-phase.cpp','BUILD.json','build.log'):
            tf.add(runtime/'native-resident'/name,arcname='native/'+name)
        for name in cfg['source_sha256']:tf.add(ROOT/name,arcname=name)
        tf.add(ROOT/'validation/S032/start/THIRD_PARTY_NOTICES.md',arcname='THIRD_PARTY_NOTICES.md')
    with tarfile.open(out/'controls-and-diagnostics.tar.gz','w:gz') as tf:
        for name in ('controls-v3','controls-v4'):
            tf.add(gate/name,arcname=name)
        control=read_json(gate/'SCHEDULER_CONTROLS.json');tf.add(Path(control['controls_directory']),arcname='scheduler-controls')
        control=read_json(gate/'RETENTION_CONTROLS.json');tf.add(Path(control['directory']),arcname='retention-control')
        # Large native input is exactly reconstructible from REGISTERED recipe and its hash.
        for name in ('phase-diagnostic','phase-diagnostic-overlap-aborted'):
            for p in sorted((runtime/name).rglob('*')):
                if p.is_file() and p.name!='shared-input.inst':tf.add(p,arcname=name+'/'+p.relative_to(runtime/name).as_posix())
    (out/'REGIONS.json.gz').write_bytes(gzip.compress((runtime/'campaign/REGIONS.json').read_bytes(),mtime=0))
    path=ROOT/'authoritative/STATE.json';state=read_json(path)
    state['active_session'].update(execution_revision=cfg['execution_revision'],controller_entry='scripts/s035_resident_campaign.py',
        private_cdcl_policy='Retained in RAM per region between scheduled turns; semantic-only recovery after process loss',
        diagnostic='Optional congruence simplification disabled after measured comparison' if cfg['disable_congruence'] else 'Instrumented phase comparison retained; default options kept',
        maintenance=False)
    atomic_json(path,state)
    session=ROOT/'sessions/S035'
    old=(session/'RUNNING.md').read_text(encoding='utf-8')
    header='''# S035 resident solver upgrade ACTIVE

The owner explicitly requested investigation of flat counters and preservation of
useful learning within S035. The controller now uses per-region resident native
processes, paused/resumed with unchanged PID/create-time identity. CDCL clauses,
activities and search state remain in RAM across fair600s turns; initial15s turns
validate actual resume. No Boolean learning is shared between regions. Audited
geometric delta blocks are immutable and shared normally. RAM is not a durable
crash checkpoint: process loss still falls back to preserved semantic evidence.

Flat counters were observed inside CaDiCaL congruence simplification (mode2052).
See validation/S035/resident/DIAGNOSTIC.json for the equal90s comparison and
registered option selection. Fresh full271+K9 and both native option-control sets,
same-PID retention, paused CPU, immutable cut deltas, memory eviction, STOP/crash,
orphan and damaged-proof controls passed. All pre-upgrade runtime bytes were
archived/roundtrip-verified; no old checkpoint or proof archive was deleted.

Resident cache target5GiB, available RAM target2.5GiB; hard aggregate6GiB and
per-worker2GiB caps and existing disk/proof budgets remain. Memory-driven parked
context eviction is logged and preserves semantic checkpoints. Two active worker
slots; additional parked contexts consume RAM but no scheduled CPU.
V2 bounds admission to at most four resident regions, counts in-flight claims,
and reuses retained contexts before admitting a cold fifth region. This avoids
the cache churn observed while initially piloting all nine contexts. Regions
outside the resident batch remain UNKNOWN and queued until an admission opens.

Current status: `.venv/Scripts/python.exe scripts/s035_resident_campaign.py status`
STOP: `.venv/Scripts/python.exe scripts/s035_resident_campaign.py stop`
Runtime authority also includes RESIDENT_CONTEXTS.json. Never start duplicate
workers. S035 remains IN_PROGRESS;9<=chi2<=12 and all proof gates unchanged.
S036 is not invoked. The following original launch handoff is historical.

'''
    (session/'RUNNING.md').write_text(header+old,encoding='utf-8',newline='\n')
    files={}
    for p in [*out.iterdir(),session/'RESIDENT_UPGRADE_PLAN.md']:
        if p.is_file() and p.name!='MANIFEST.json':files[p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
    atomic_json(out/'MANIFEST.json',dict(status='S035_RUNNING_RESIDENT_UPGRADE',files=files))
    # Current index is explicit about revision; the original manifest remains intact.
    index=read_json(session/'RUNNING_MANIFEST.json')
    index.update(revision='RESIDENT_UPGRADE',previous_manifest='validation/S035/pre-resident/RUNNING_MANIFEST.json')
    for p in (session/'RUNNING.md',out/'MANIFEST.json'):
        index['files'][p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
    atomic_json(session/'RUNNING_MANIFEST.json',index)
    print('Archived resident upgrade evidence; original launch and pre-upgrade bytes preserved',flush=True)

if __name__=='__main__':main()
