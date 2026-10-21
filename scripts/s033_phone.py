"""Bounded single-worker phone diagnostics; status/stop never launch a solver.

Every outcome remains UNKNOWN. Native output cannot certify a region.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import resource
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s026_supervision import atomic_json, linux_tree
AREA=ROOT/'artifacts/tmp/S033'

def identity(pid):
    return Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]

def terminate(record):
    try:
        if identity(record['worker_pid']) != record['worker_start_ticks']:
            return
        os.killpg(record['worker_pid'],signal.SIGTERM)
        time.sleep(.2)
        try: os.killpg(record['worker_pid'],signal.SIGKILL)
        except ProcessLookupError: pass
    except (FileNotFoundError,ProcessLookupError): pass

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['run','status','stop','recover'])
    ap.add_argument('--input',type=Path)
    ap.add_argument('--seconds',type=int,default=5)
    a=ap.parse_args();AREA.mkdir(parents=True,exist_ok=True)
    state_path=AREA/'PHONE.json';stop=AREA/'STOP'
    if a.action=='status':
        print(state_path.read_text() if state_path.exists() else 'No phone diagnostic recorded.');return
    if a.action=='stop':
        stop.touch();print('STOP requested; no certification implied.');return
    with (AREA/'ACTIVE.lock').open('a') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise SystemExit('A diagnostic controller is active; use stop.')
        if state_path.exists():
            old=json.loads(state_path.read_text())
            if old['status']=='RUNNING':
                terminate(old);old.update(status='RECOVERED_UNKNOWN',verdict='UNKNOWN')
                atomic_json(state_path,old)
        if a.action=='recover': return
        assert a.input and 1<=a.seconds<=30
        smoke=json.loads((ROOT/'artifacts/tmp/cloud_smoke/RESULT.json').read_text())
        assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==271
        assert smoke['chromatic_cnf_byte_matches']==271
        assert shutil.disk_usage(ROOT).free>=4*1024**3
        stop.unlink(missing_ok=True)
        run_dir=AREA/f'diagnostic-{time.time_ns()}';run_dir.mkdir()
        native=AREA/'native/bipsat_s033'
        native_hash=hashlib.sha256(native.read_bytes()).hexdigest()
        controls=json.loads((AREA/'NATIVE_CONTROLS.json').read_text())
        assert controls['status'] in ('PASS','SCOPED_PASS_WITH_FREE_K9_UNKNOWN')
        assert controls['native_sha256']==native_hash
        record={'status':'RUNNING','verdict':'UNKNOWN','input':str(a.input.resolve()),
            'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),
            'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
            'seconds_cap':a.seconds,'rss_cap_kib':1048576,'disk_reserve_bytes':4*1024**3,
            'directory':str(run_dir),'controller_pid':os.getpid(),'peak_rss_kib':0,
            'thermal':'UNAVAILABLE; no thermal safety claim','native_cdcl_state_saved':False}
        interrupted=[]
        def handler(signum,frame): interrupted.append(signum)
        for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):signal.signal(sig,handler)
        cpu_start=resource.getrusage(resource.RUSAGE_CHILDREN)
        start=time.monotonic();p=None;reason=None
        try:
            with (run_dir/'worker.log').open('w') as log:
                p=subprocess.Popen([str(native),str(a.input.resolve()),'--timeout',str(a.seconds),'--lemmas',str(run_dir/'learned.lem')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                record.update(worker_pid=p.pid,worker_start_ticks=identity(p.pid))
                atomic_json(state_path,record)
                while p.poll() is None:
                    try:
                        status=Path(f'/proc/{p.pid}/status').read_text()
                        assert 'VmRSS:' in status
                        _,rss=linux_tree(p.pid)
                        assert rss>0
                    except (OSError,AssertionError):
                        try:
                            p.wait(timeout=.2)
                        except subprocess.TimeoutExpired:
                            reason='RSS_UNAVAILABLE'
                        break
                    record['peak_rss_kib']=max(record['peak_rss_kib'],rss)
                    if interrupted or stop.exists():reason='OWNER_STOP'
                    elif rss>record['rss_cap_kib']:reason='RSS_CAPPED'
                    elif shutil.disk_usage(ROOT).free<record['disk_reserve_bytes']:reason='DISK_CAPPED'
                    elif time.monotonic()-start>a.seconds+2:reason='WALL_CAPPED'
                    if reason:break
                    record['elapsed_seconds']=time.monotonic()-start
                    atomic_json(state_path,record);time.sleep(.1)
        finally:
            if p is not None:
                if p.poll() is None:terminate(record)
                p.wait()
                record['returncode']=p.returncode
                cpu_end=resource.getrusage(resource.RUSAGE_CHILDREN)
                record['cpu_seconds']=(cpu_end.ru_utime+cpu_end.ru_stime)-(cpu_start.ru_utime+cpu_start.ru_stime)
            record.update(status=reason or 'FINISHED_UNKNOWN',verdict='UNKNOWN',wall_seconds=time.monotonic()-start,free_disk_bytes=shutil.disk_usage(ROOT).free)
            atomic_json(state_path,record);atomic_json(run_dir/'RESULT.json',record)
        print(json.dumps(record,indent=2))

if __name__=='__main__':main()
