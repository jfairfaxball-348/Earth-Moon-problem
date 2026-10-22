"""Equal120s genuine1/2/3-worker trials; retain every scientific output."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_windows import atomic_json, tree_sample, memory_available, stop_group, process_identity
from s035_regions import sha, report, ledger
from s035_engine import audit_cuts
from prepare_s035 import prepared, write_area
AREA=ROOT/'artifacts/tmp/S035'

def collect_cuts(area,cfg):
    for p in area.glob('attempts/cell-*/*/new-cuts.lem'):
        row=audit_cuts(p,cfg,time.time()+3600)
        if row:
            with ledger(area) as data:
                if not any(r['sha256']==row['sha256'] for r in data['accepted_cuts']):data['accepted_cuts'].append(row)

def main():
    rows=[]
    for count in (1,2,3):
        cfg,data=prepared(count,time.time()+120)
        cfg.update(min_visit_seconds=90,max_visit_seconds=90)
        area=AREA/f'benchmark-{count}';write_area(area,cfg,data)
        start=time.monotonic();peak_private=peak_rss=peak_slots=peak_disk=0;minimum_available=2**63
        cpu={};next_snapshot=0
        with (area/'launcher.log').open('w') as log:
            p=subprocess.Popen([sys.executable,str(ROOT/'scripts/s035_campaign.py'),'guard','--directory',str(area)],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP)
        try:
            while p.poll() is None:
                sample=tree_sample(p.pid)
                peak_private=max(peak_private,sample['private']);peak_rss=max(peak_rss,sample['rss'])
                minimum_available=min(minimum_available,memory_available())
                try:
                    processes=[psutil.Process(p.pid),*psutil.Process(p.pid).children(recursive=True)]
                    for x in processes:
                        try:
                            c=x.cpu_times();key=(x.pid,x.create_time());cpu[key]=max(cpu.get(key,0),c.user+c.system)
                        except psutil.Error:pass
                    slots=sum(x.name().lower() in ('bipsat_s032.exe','cadical.exe','drat-trim-mingw.exe') for x in processes if x.is_running())
                    peak_slots=max(peak_slots,slots)
                except psutil.Error:pass
                if time.monotonic()>=next_snapshot:
                    peak_disk=max(peak_disk,sum(x.stat().st_size for x in area.rglob('*') if x.is_file()))
                    atomic_json(area/'MEASURE.json',dict(elapsed=time.monotonic()-start,peak_private_bytes=peak_private,peak_rss_bytes=peak_rss,minimum_available_kib=minimum_available,peak_genuine_worker_slots=peak_slots,cpu_seconds=sum(cpu.values()),peak_disk_bytes=peak_disk))
                    next_snapshot=time.monotonic()+10
                if time.monotonic()-start>180:
                    (area/'STOP').touch()
                if time.monotonic()-start>240:
                    stop_group(dict(pid=p.pid,start_ticks=process_identity(p.pid)));raise RuntimeError('Benchmark stop failed')
                time.sleep(.5)
        finally:
            if p.poll() is None:
                (area/'STOP').touch();p.wait(timeout=30)
        assert p.returncode==0,(area,p.returncode)
        collect_cuts(area,cfg)
        progress=report(area);state=json.loads((area/'STOPPED.json').read_text())
        assert not progress['active'] and state['reason']=='DEADLINE',state['reason']
        row=dict(workers=count,registered_wall_seconds=120,observed_wall_seconds=time.monotonic()-start,
            peak_private_bytes=peak_private,peak_rss_bytes=peak_rss,minimum_available_kib=minimum_available,
            peak_genuine_worker_slots=peak_slots,cpu_seconds=sum(cpu.values()),peak_disk_bytes=peak_disk,
            new_checked_cuts=progress['accepted_new_clauses']-93047,new_proof_closed_regions=progress['proof_closed_regions']-16,
            total_visits=progress['total_visits']-102,thermal='UNAVAILABLE_NO_THERMAL_GUARANTEE',status='COMPLETE_CALIBRATION_UNKNOWN',directory=str(area))
        rows.append(row);atomic_json(AREA/'BENCHMARKS.json',dict(status='IN_PROGRESS' if count<3 else 'PASS',rows=rows,private_cdcl_state_saved=False,mathematical_verdict='UNKNOWN'))
        print(json.dumps(row),flush=True)

if __name__=='__main__':main()
