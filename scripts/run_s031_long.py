"""Detached S031 serial controller: sleep request, limits, provenance, proof gate.

Launch hidden with Start-Process. It never closes a session or starts S032.
"""
from datetime import datetime,timezone
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT/'tools'))
from s026_supervision import atomic_json,run_step

OUT=ROOT/'artifacts/tmp/S031'
MEM=11*1024*1024


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # CREATE_NEW_PROCESS_GROUP / hidden launcher is supplied by Start-Process.
    sleep_requested=False
    if os.name=='nt':
        sleep_requested=bool(ctypes.windll.kernel32.SetThreadExecutionState(0x80000001))
    source_names=['tools/s031_incremental.py','tools/s031_check.py','tools/s030_op1b.py',
                  'tools/s026_supervision.py','scripts/run_s031_long.py','scripts/s031_controls.py',
                  'scripts/replay_s030_search.py','scripts/run_s031_gate.py']
    state={'session':'S031','pid':os.getpid(),'status':'STARTING','started_utc':datetime.now(timezone.utc).isoformat(),
           'source_sha256':{p:sha(ROOT/p) for p in source_names},
           'sleep_inhibition_requested':sleep_requested,'memory_cap_kib':MEM,
           'worker_cap_seconds':28800,'worker_search_seconds':28680,
           'followup_automation':'earth-moon-long-run-continuation','proof_caps_seconds':14400,
           'session_closed':False,'witness_established':False}
    def save(phase):
        state['status']=phase;state['updated_utc']=datetime.now(timezone.utc).isoformat()
        atomic_json(OUT/'CONTROLLER.json',state)
    try:
        assert json.loads((OUT/'SMOKE.json').read_text())['verdict']=='PASS'
        assert json.loads((OUT/'CONTROLS.json').read_text())['status']=='PASS'
        assert shutil.disk_usage(ROOT).free>10*1024**3
        snapshots=OUT/'source-bytes';snapshots.mkdir(exist_ok=True)
        for name in source_names:
            shutil.copy2(ROOT/name,snapshots/(state['source_sha256'][name]+'.py'))
        save('SEARCH_RUNNING')
        cmd=[sys.executable,str(ROOT/'tools/s031_incremental.py'),'--cap','28680']
        if '--resume' in sys.argv:cmd.append('--resume')
        result=run_step(cmd,28800,OUT/'worker.log',OUT/'LONG_JOURNAL.jsonl',memory_kib=MEM)
        state['worker_process']=result
        target=OUT/'search/RESULT.json'
        if result['returncode']!=0 or not target.exists():
            save('WORKER_STOPPED_UNKNOWN_REVIEW_REQUIRED');return
        science=json.loads(target.read_text());state['worker_result']=science
        if science['stop_reason']!='INCREMENTAL_UNSAT_PENDING_NATIVE_PROOF':
            save('WITNESS_CANDIDATE_REVIEW_REQUIRED' if science['witness_candidate'] else 'SEARCH_FINISHED_UNKNOWN_REVIEW_REQUIRED')
            return
        native=ROOT/'artifacts/tmp/S004/cadical.exe';checker=ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'
        cnf=OUT/'search/final.cnf';proof=OUT/'search/final.native.drat'
        save('NATIVE_PROOF_RUNNING')
        r=run_step([str(native),str(cnf),str(proof)],14400,OUT/'native-proof.log',OUT/'LONG_JOURNAL.jsonl',memory_kib=MEM)
        state['native_process']=r
        if r['returncode']!=20:
            save('NATIVE_REPLAY_NOT_VERIFIED_UNKNOWN');return
        state['native_cnf_sha256']=sha(cnf);state['native_drat_sha256']=sha(proof)
        save('PROOF_CHECK_RUNNING')
        q=run_step([str(checker),str(cnf),str(proof)],14400,OUT/'native-check.log',OUT/'LONG_JOURNAL.jsonl',memory_kib=MEM)
        state['checker_process']=q
        verified=q['returncode']==0 and 'VERIFIED' in (OUT/'native-check.log').read_text()
        save('UNSAT_DRAT_VERIFIED_PENDING_INDEPENDENT_DOMAIN_REVIEW' if verified else 'PROOF_CHECK_FAILED_UNKNOWN')
    except Exception as e:
        state['error']=repr(e);save('CONTROLLER_ERROR_UNKNOWN');raise
    finally:
        state['finished_utc']=datetime.now(timezone.utc).isoformat()
        if sleep_requested:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        state['sleep_inhibition_released']=sleep_requested
        atomic_json(OUT/'CONTROLLER.json',state)


if __name__=='__main__':main()
