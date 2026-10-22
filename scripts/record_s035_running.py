"""Archive accepted Windows launch evidence; leave S035 explicitly running."""
from datetime import datetime,timezone
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_regions import report,sha
from s035_windows import atomic_json,COMPILER_BIN
AREA=ROOT/'artifacts/tmp/S035';OUT=ROOT/'validation/S035';SESSION=ROOT/'sessions/S035'

def main():
    live=report(AREA/'campaign');cfg=json.loads((AREA/'campaign/CONFIG.json').read_text())
    assert live['status']=='RUNNING' and live['controller_process_alive'] and len(live['active'])==cfg['workers']
    assert cfg['workers']>=2 and cfg['deadline'] is None
    entry='4eac1237723134f1d1924938f476a06287aab919'
    assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]==entry
    OUT.mkdir(exist_ok=True)
    for name in ('SMOKE','ENVIRONMENT','HARDWARE','INPUT_AUDIT','NATIVE_CONTROLS','SCHEDULER_CONTROLS','IMPORT_AUDIT','BENCHMARKS','BENCHMARK_MERGE','SOLVER_CONCURRENCY'):
        shutil.copy2(AREA/(name+'.json'),OUT/(name+'.json'))
    shutil.copy2(AREA/'native/BUILD.json',OUT/'BUILD.json')
    shutil.copy2(AREA/'campaign/CONFIG.json',OUT/'REGISTERED_CONFIG.json')
    atomic_json(OUT/'LAUNCH_SNAPSHOT.json',live)
    atomic_json(OUT/'ENTRY.json',dict(session='S035',entry_main=entry,entry_tree='8d2f866cd9536552532ddb7099e4d6642fd08bba',entry_parent='236d97e8c142b8fdf8d124f02f9c1b754693002f',open_prs=[],hosted_entry_run=39734774448,hosted_entry_job=119677789511,hosted_entry_conclusion='success',recorded_utc=datetime.now(timezone.utc).isoformat(),status='RUNNING_NOT_CLOSED'))
    import psutil
    atomic_json(OUT/'RUNTIME_DEPENDENCIES.json',dict(psutil_version=version('psutil'),psutil_files={str(p):sha(p) for p in Path(psutil.__file__).parent.glob('*.pyd')},compiler_runtime_dlls={str(p):sha(p) for p in COMPILER_BIN.glob('*.dll')},python_executable=sys.executable,python_executable_sha256=sha(sys.executable)))
    with tarfile.open(OUT/'native.tar.gz','w:gz') as tf:
        for name in ('bipsat_s032.exe','bipsat_s032.cpp','BUILD.json','build.log'):
            tf.add(AREA/'native'/name,arcname='native/'+name)
        tf.add(ROOT/'validation/S032/start/THIRD_PARTY_NOTICES.md',arcname='THIRD_PARTY_NOTICES.md')
        for name in ('LICENSE','NOTICE.md'):
            tf.add(ROOT/'artifacts/tmp/S032/bipsat2'/name,arcname='bipsat2/'+name)
    controls=json.loads((AREA/'SCHEDULER_CONTROLS.json').read_text())
    with tarfile.open(OUT/'acceptance-and-benchmarks.tar.gz','w:gz') as tf:
        for name in ('controls-v2','replay','benchmark-1','benchmark-2','benchmark-3'):
            tf.add(AREA/name,arcname=name)
        tf.add(Path(controls['controls_directory']),arcname='scheduler-controls')
        for name in ('SOLVER_SAMPLES.jsonl','storage-control.drat.gz','storage-control.ARCHIVE.json'):
            tf.add(AREA/name,arcname=name)
    for name in ('REGIONS.json','CONTROLLER.json','GUARDIAN.json','JOURNAL.jsonl'):
        (OUT/(name+'.gz')).write_bytes(gzip.compress((AREA/'campaign'/name).read_bytes(),mtime=0))
    state_path=ROOT/'authoritative/STATE.json';state=json.loads(state_path.read_text(encoding='utf-8'))
    state['active_session'].update(status='RUNNING',workers=cfg['workers'],runtime_status_authority='artifacts/tmp/S035/campaign/GUARDIAN.json',running_handoff='sessions/S035/RUNNING.md',deadline=None)
    state['next_session_priority']='S035 RUNNING: inspect actual guardian/PIDs/checkpoints; do not duplicate. No fixed cutoff. S036 not authorised.'
    atomic_json(state_path,state)
    running=f'''# S035 RUNNING - Windows multiple workers

Owner invoked exactly S035 on22 October2026 and confirms laptop power/wifi/no-sleep.
Fresh full271+retained/fresh K9,1024n5/K33/positive24, all2672984 inherited clause
occurrences, exact bijective mapping/256-region partition,16 inherited Windows
DRAT replays, STOP/crash/orphan/proof/storage controls PASS. Measured genuine
1/2/3-worker trials completed; all outputs merged and retained. Selected{cfg['workers']}
workers from checked-region throughput and memory headroom. See validation/S035/.

No overall campaign timeout.600..1800s visits preserve semantic cuts/checkpoints;
private CDCL learning is not saved between visits. At most{cfg['workers']} active native,
proof or checker processes under worker slots, below-normal priority.6GiB sampled
aggregate private cap,2GiB per-worker cap,2GiB available-memory floor,10GiB disk
reserve,2GiB per-attempt raw proof cap,40GiB campaign/64GiB total S035 disk budgets.
Partial/completed proofs compressed losslessly with restore/hash verification.
Core thermal sensors unavailable; no thermal guarantee. Sleep inhibition is released
on clean stop; unexpected guardian death is detected by the controller.

Status: `.venv/Scripts/python.exe scripts/s035_campaign.py status`
STOP: `.venv/Scripts/python.exe scripts/s035_campaign.py stop`

Live authority is artifacts/tmp/S035/campaign/GUARDIAN.json,CONTROLLER.json,
REGIONS.json,JOURNAL.jsonl and attempt checkpoints. Check PID/create-time identities
before any restart; never duplicate a live worker. Guardian supervises resources,
recovers identified controller crashes and stops after repeated crashes. Read-only
status never launches work. Owner STOP, unsafe resources/processes, validated
candidate or fully closed encoded queue stops the campaign. On safety stop,
independently audit and close S035; never launch S036 automatically.

S035 is IN_PROGRESS, not complete. Last completed S034;9<=chi2<=12 unchanged;
S11m155/156 UNKNOWN, regular154 SOURCE_STATED, S10/S9/S8 NOT_RUN. Encoded closures
are not individual graph exclusions or whole-stratum proof; weights are not ETA.
All parked/publication/outreach/formalisation gates remain. At actual closeout,
archive every result, synchronize catalogues/ledgers/state, write identical complete
S036 future prompts, make ordinary non-force existing-main publication and verify
actual hosted jobs. No new branch/PR. D044 fallback requires same-job ubuntu-24.04
pinned setup and full smoke; historical runs38623187997,38623722547,38624616691,
38635879431 and validation/S011/SUMMARY.json/validation/S012 are provenance only.
'''
    (SESSION/'RUNNING.md').write_text(running,encoding='utf-8',newline='\n')
    def append(name,text):
        p=ROOT/name;p.write_text(p.read_text(encoding='utf-8')+'\n'+text+'\n',encoding='utf-8',newline='\n')
    append('docs/SESSION_LEDGER.md',f'| S035 |2026-10-22| D047/D074 owner Windows invocation; CAM0040 | Fresh Windows acceptance and genuine1/2/3-worker benchmarks PASS; sustained{cfg["workers"]} workers RUNNING | IN_PROGRESS; no S036 |')
    append('docs/DECISION_LOG.md','S035 invocation2026-10-22: owner says run next session, >90GB free and laptop on power/wifi without sleep. Exactly S035, existing main/no new branch/PR, genuine multiple workers after measured acceptance; no overall arbitrary cutoff and no S036 invocation.')
    append('docs/PHASE_GATE_LEDGER.md','S035 RUNNING: Windows acceptance/import/proof replays and real multiworker calibration PASS. Phase1 gate NOT PASSED; no headline advance. Sources/claims unchanged and synchronized.')
    append('docs/FAILURE_LEDGER.md','S035 setup: initial DLL PATH failure, Windows atomic-read sharing conflict and early heartbeat race were caught by synthetic controls and repaired before science. Fresh lifecycle/orphan controls PASS; failed fixture outputs retained. No mathematical verdict from failures.')
    append('campaigns/README.md',f'**CAM-0040 / S035 RUNNING:** Windows exact256-region continuation; measured1/2/3-worker trials, selected{cfg["workers"]} genuine workers. Owner STOP/safety guards, no fixed campaign cutoff.9..12 unchanged; no S036 execution.')
    files={}
    for p in [*OUT.iterdir(),*SESSION.glob('*.md')]:
        if p.is_file():files[p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
    atomic_json(SESSION/'RUNNING_MANIFEST.json',dict(status='RUNNING_NOT_CLOSED',files=files))
    print('S035 running evidence archived; sustained campaign continues independently',flush=True)

if __name__=='__main__':main()
