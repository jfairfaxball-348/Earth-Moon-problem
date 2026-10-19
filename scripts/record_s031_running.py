"""Truthful running-state and durable start evidence; never a session closeout."""
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/tmp/S031';DEST=ROOT/'validation/S031/start'


def write(p,data):
    p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    c=json.loads((OUT/'CONTROLLER.json').read_text())
    p=json.loads((OUT/'search/PROGRESS.json').read_text())
    assert c['status']=='SEARCH_RUNNING' and p['status']=='RUNNING'
    assert p['source_sha256']==hashlib.sha256((ROOT/'tools/s031_incremental.py').read_bytes()).hexdigest()
    DEST.mkdir(parents=True,exist_ok=True)
    for name in ('ENVIRONMENT.json','GATE.json','SMOKE.json','CONTROLS.json','CONTROLS_PROCESS.json',
                 'S030_REPLAY.json','CONTROLLER.json','LAUNCH.json'):
        shutil.copy2(OUT/name,DEST/name)
    shutil.copy2(OUT/'search/PROGRESS.json',DEST/'INITIAL_PROGRESS.json')
    for name in ('FETCH_RECEIPTS.json','ARTICLE_COMPARISON.json'):
        shutil.copy2(OUT/'prior-art'/name,DEST/name)
    # Preserve diagnostic receipts and source bytes as separate provenance.
    for name in ('CONTROLLER.json','LAUNCH.json'):
        d=DEST/'startup-v1';d.mkdir(exist_ok=True)
        shutil.copy2(OUT/'startup-v1'/name,d/name)
    d=DEST/'startup-v1/search';d.mkdir(parents=True,exist_ok=True)
    shutil.copy2(OUT/'startup-v1/search/RESULT.json',d/'RESULT.json')
    src=DEST/'source-bytes';src.mkdir(exist_ok=True)
    for s in (OUT/'source-bytes').glob('*.py'):
        (src/(s.name+'.gz')).write_bytes(gzip.compress(s.read_bytes(),mtime=0))
    state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
    assert state['last_completed_session']=='S030'
    state['next_session_is_future_unexecuted']=False
    state['active_session']={'id':'S031','status':'IN_PROGRESS_LONG_RUN',
        'authority':'docs/D065_LONG_RUN_AUTHORIZATION.md','branch':'codex/S031-persistent-op1b',
        'entry_main':'dd802686215781cbc35aa86ea14c54369aaec7e5',
        'started_utc':c['started_utc'],'controller_pid':c['pid'],'worker_pid':p['pid'],
        'runtime_directory':'artifacts/tmp/S031','running_handoff':'sessions/S031/RUNNING.md',
        'followup_automation_id':'earth-moon-long-run-continuation',
        'scheduled_interval_hours':2,'worker_cap_seconds':28800,
        'last_completed_session_still':'S030','scientific_status':'NO_NEW_CERTIFIED_STRATUM_OR_WITNESS'}
    state['standing_continuation_authorization']={'decision':'D065',
        'successive_sessions_authorized':True,'stop_conditions':['owner revocation','context exhausted','usage allowance exhausted'],
        'preserve_session_scopes_and_publication_gates':True}
    write(ROOT/'authoritative/STATE.json',state)
    manifest={'scope':'running launch snapshot only; no S031 closeout',
              'recorded_utc':datetime.now(timezone.utc).isoformat(),'artifact_sha256':{}}
    for path in DEST.rglob('*'):
        if path.is_file():
            b=path.read_bytes();manifest['artifact_sha256'][path.relative_to(ROOT).as_posix()]={
                'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    write(ROOT/'sessions/S031/START_MANIFEST.json',manifest)
    print('Recorded S031 IN_PROGRESS; S030 remains last completed; no final session commit claimed')


if __name__=='__main__':main()
