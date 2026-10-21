"""One supervised native partial-planarity worker; no successor execution."""
import argparse
import ctypes
from datetime import datetime,timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s026_supervision import atomic_json,journal,windows_tree_bytes,kill_tree,run_step
from check_s032_native import lemmas


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='campaign')
    ap.add_argument('--cap',type=int,default=0,help='0 = no fixed wall limit (owner D069)');ap.add_argument('--resume-from')
    ap.add_argument('--diagnostic',action='store_true');a=ap.parse_args()
    assert a.cap>=0
    root=ROOT/'artifacts/tmp/S032';out=root/a.out
    out.mkdir(parents=True,exist_ok=False)
    lock=root/'ACTIVE.lock'
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    state={'session':'S032','pid':os.getpid(),'status':'STARTING',
           'started_utc':datetime.now(timezone.utc).isoformat(),
           'search_cap_seconds':a.cap or None,'external_cap_seconds':a.cap+120 if a.cap else None,
           'no_fixed_wall_limit':a.cap==0,'duration_authority':'D069 owner continue until stop',
           'proof_wall_limit_seconds':None if a.cap==0 else 14400,
           'memory_cap_kib':11*1024**2,'diagnostic':a.diagnostic,
           'input_sha256':sha(root/'S11.inst'),'native_sha256':sha(root/'native/bipsat_s032.exe'),
           'session_closed':False,'witness_established':False}
    controller=out/'CONTROLLER.json'
    def save(status):
        state['status']=status;state['updated_utc']=datetime.now(timezone.utc).isoformat()
        atomic_json(controller,state)
    sleep_requested=False;worker=None;proof_worker=None
    def snapshot():
        # The durable append-only journal is the semantic checkpoint. Hash a
        # bounded complete prefix without materialising an unbounded log in RAM.
        p=out/'learned.lem'
        if not p.exists():return
        limit=p.stat().st_size;remaining=limit;tail=b'';h=hashlib.sha256();length=0;count=0
        with p.open('rb') as f:
            while remaining:
                b=f.read(min(1024*1024,remaining));remaining-=len(b)
                if not b:break
                data=tail+b;end=data.rfind(b'\n')+1
                complete=data[:end];tail=data[end:]
                h.update(complete);length+=len(complete);count+=complete.count(b'\n')
        atomic_json(out/'CHECKPOINT.json',{'session':'S032','updated_utc':datetime.now(timezone.utc).isoformat(),
            'input_sha256':state['input_sha256'],'native_sha256':state['native_sha256'],
            'lemma_file':'learned.lem','complete_lemma_lines':count,'complete_lemma_bytes':length,
            'omitted_incomplete_tail_bytes':limit-length,'lemma_sha256':h.hexdigest(),
            'native_cdcl_state_saved':False,'verdict':'UNKNOWN',
            'note':'full fixed input plus this hashed complete prefix of append-only learned.lem; not an exhaustion certificate'})
    def proof_step(args,cap,name):
        nonlocal proof_worker
        start=time.monotonic();last=0;peak=0;reason=None
        with (out/(name+'.log')).open('w') as f:
            p=subprocess.Popen(args,stdout=f,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
            proof_worker=p
            state['proof_worker_pid']=p.pid;save(name.replace('-','_').upper()+'_RUNNING')
            while p.poll() is None:
                now=time.monotonic();used=windows_tree_bytes(os.getpid())//1024;peak=max(peak,used)
                if used>state['memory_cap_kib']:reason='MEMORY_CAPPED'
                if shutil.disk_usage(root).free<10*1024**3:reason='DISK_RESERVE_STOP'
                if (root/'STOP').exists():reason='OWNER_STOP'
                if cap and now-start>cap:reason='WALL_CAPPED'
                if reason:kill_tree(p);break
                if now-last>=30:
                    journal(out/'JOURNAL.jsonl','heartbeat',phase=name,pid=p.pid,seconds=now-start,private_tree_kib=used);last=now
                time.sleep(0.5)
        return {'command':args,'returncode':reason or p.returncode,'seconds':time.monotonic()-start,
                'peak_aggregate_private_kib':peak,'memory_cap_kib':state['memory_cap_kib']}
    try:
        assert json.loads((root/'SMOKE.json').read_text())['verdict']=='PASS'
        native_controls=json.loads((root/'NATIVE_CONTROLS.json').read_text())
        assert native_controls['status'] in ('PASS','SCOPED_PASS_WITH_FREE_K9_UNKNOWN')
        state['native_control_scope']=native_controls['status']
        assert json.loads((root/'NATIVE_CONTROLS.json').read_text())['native_sha256']==state['native_sha256']
        assert json.loads((root/'CONTROLS.json').read_text())['status']=='PASS'
        if a.cap==0:assert json.loads((root/'INFINITE_TIMEOUT_CONTROL.json').read_text())['status']=='PASS'
        if not a.diagnostic:assert json.loads((root/'DIAGNOSTIC_AUDIT.json').read_text())['status']=='PASS'
        assert shutil.disk_usage(root).free>10*1024**3
        names=['scripts/run_s032_native.py','scripts/build_s032_native.py','scripts/prepare_s032.py',
               'scripts/check_s032_native.py','tools/s032_subdivision.hpp','tools/s030_op1b.py',
               'tools/s031_check.py','scripts/replay_s030_search.py','tools/s026_supervision.py']
        state['source_sha256']={n:sha(ROOT/n) for n in names}
        runtime=ROOT/'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64/bin'
        state['runtime_sha256']={p.relative_to(ROOT).as_posix():sha(p) for p in [runtime/'libc++.dll',runtime/'libunwind.dll']}
        sources=root/'source-bytes';sources.mkdir(exist_ok=True)
        for n,h in state['source_sha256'].items():
            (sources/(h+Path(n).suffix)).write_bytes((ROOT/n).read_bytes())
        inputs=json.loads((root/'INPUTS.json').read_text())
        assert state['input_sha256']==inputs['sha256']['S11.inst']
        if a.resume_from:
            seed=ROOT/a.resume_from
            state['resumed_lemma_count']=lemmas(seed,28,[tuple(e) for e in inputs['pairs']])
            state['resumed_lemma_sha256']=sha(seed)
            shutil.copy2(seed,out/'learned.lem')
        env=os.environ.copy()
        env['PATH']=str(ROOT/'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64/bin')+os.pathsep+env['PATH']
        sleep_requested=bool(ctypes.windll.kernel32.SetThreadExecutionState(0x80000001))
        state['sleep_inhibition_requested']=sleep_requested
        command=[str(root/'native/bipsat_s032.exe'),str(root/'S11.inst'),'--timeout',str(a.cap) if a.cap else 'inf','--lemmas',str(out/'learned.lem')]
        start=time.monotonic();last=0;last_snapshot=0;peak=0;reason=None
        with (out/'worker.log').open('w') as log:
            worker=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
            state['worker_pid']=worker.pid;state['command']=command;save('SEARCH_RUNNING')
            atomic_json(out/'WORKER.json',{'pid':worker.pid,'controller_pid':os.getpid(),
                'started_utc':state['updated_utc'],'command':command,'native_sha256':state['native_sha256']})
            journal(out/'JOURNAL.jsonl','start',**state)
            while worker.poll() is None:
                now=time.monotonic();used=windows_tree_bytes(os.getpid())//1024;peak=max(peak,used)
                free=shutil.disk_usage(root).free
                if used>state['memory_cap_kib']:reason='MEMORY_CAPPED'
                if free<10*1024**3:reason='DISK_RESERVE_STOP'
                if (root/'STOP').exists():reason='OWNER_STOP'
                if a.cap and now-start>a.cap+120:reason='EXTERNAL_WALL_CAPPED'
                if reason:kill_tree(worker);break
                if now-last>=30:
                    with (out/'worker.log').open('rb') as f:
                        f.seek(max(0,f.seek(0,2)-65536));tail=f.read().decode(errors='replace')
                    progress=re.findall(r'c S032_PROGRESS .*',tail)
                    info={'pid':worker.pid,'seconds':round(now-start,3),'private_tree_kib':used,
                          'peak_private_tree_kib':peak,'free_disk_bytes':free,
                          'native_progress':progress[-1] if progress else None,'verdict':'UNKNOWN',
                          'updated_utc':datetime.now(timezone.utc).isoformat()}
                    atomic_json(out/'PROGRESS.json',info);journal(out/'JOURNAL.jsonl','heartbeat',**info);last=now
                if now-last_snapshot>=300:snapshot();last_snapshot=now
                time.sleep(0.5)
        elapsed=round(time.monotonic()-start,3);snapshot()
        state['worker_result']={'returncode':worker.returncode,'stop_reason':reason,
            'seconds':elapsed,'peak_aggregate_private_kib':peak,'free_disk_bytes':shutil.disk_usage(root).free}
        atomic_json(out/'RESULT.json',{**state['worker_result'],'S11_m155_156':'UNKNOWN',
            'S10':'NOT_RUN','S9':'NOT_RUN','S8':'NOT_RUN','whole_stratum_certified':False,
            'witness_established':False,'native_cdcl_state_saved':False})
        journal(out/'JOURNAL.jsonl','end',**state['worker_result'])
        if reason:save('STOPPED_UNKNOWN_REVIEW_REQUIRED');return
        if worker.returncode==10:save('WITNESS_CANDIDATE_REVIEW_REQUIRED');return
        if worker.returncode!=20:save('SEARCH_FINISHED_UNKNOWN_REVIEW_REQUIRED');return
        # The solver's bare UNSAT only requests independent full-formula replay.
        checked=lemmas(out/'learned.lem',28,[tuple(e) for e in inputs['pairs']])
        state['independent_lemma_count']=checked
        cnf=out/'final.cnf'
        with cnf.open('w',encoding='utf-8',newline='\n') as target:
            target.write(f"p cnf {inputs['variables']} {inputs['base_clauses']+checked}\n")
            with (root/'base.cnf').open() as source:
                next(source);shutil.copyfileobj(source,target)
            with (out/'learned.lem').open() as source:shutil.copyfileobj(source,target)
        proof=out/'final.native.drat';save('NATIVE_PROOF_RUNNING')
        state['native_process']=proof_step([str(ROOT/'artifacts/tmp/S004/cadical.exe'),str(cnf),str(proof)],0 if a.cap==0 else 14400,'native-proof')
        if state['native_process']['returncode']!=20:save('NATIVE_REPLAY_UNKNOWN');return
        state['cnf_sha256']=sha(cnf);state['proof_sha256']=sha(proof);save('PROOF_CHECK_RUNNING')
        state['checker_process']=proof_step([str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'),str(cnf),str(proof)],0 if a.cap==0 else 14400,'native-check')
        verified=state['checker_process']['returncode']==0 and 'VERIFIED' in (out/'native-check.log').read_text()
        save('DRAT_VERIFIED_PENDING_DOMAIN_REVIEW' if verified else 'PROOF_CHECK_FAILED_UNKNOWN')
    except Exception as e:
        if worker is not None and worker.poll() is None:kill_tree(worker)
        state['error']=repr(e);save('CONTROLLER_ERROR_UNKNOWN');raise
    finally:
        if worker is not None and worker.poll() is None:kill_tree(worker)
        if proof_worker is not None and proof_worker.poll() is None:kill_tree(proof_worker)
        state['finished_utc']=datetime.now(timezone.utc).isoformat()
        if sleep_requested:ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        state['sleep_inhibition_released']=sleep_requested
        atomic_json(controller,state);lock.unlink(missing_ok=True)


if __name__=='__main__':main()
