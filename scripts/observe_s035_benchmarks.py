"""Read-only process sampling distinguishes real SAT solvers from proof checkers."""
import json
from pathlib import Path
import sys
import time
import psutil
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'artifacts/tmp/S035'
sys.path.insert(0,str(ROOT/'tools'))
from s035_windows import atomic_json

def main():
    started=time.monotonic();peaks={}
    with (AREA/'SOLVER_SAMPLES.jsonl').open('a') as log:
        while time.monotonic()-started<900:
            rows=[]
            for p in psutil.process_iter(['pid','name','cmdline','create_time','cpu_times']):
                try:
                    if p.info['name'].lower() not in ('bipsat_s032.exe','cadical.exe','drat-trim-mingw.exe'):continue
                    command=' '.join(p.info['cmdline'] or [])
                    for count in (1,2,3):
                        if str(AREA/f'benchmark-{count}').lower() in command.lower():
                            rows.append(dict(benchmark=count,pid=p.pid,name=p.info['name'],create_time=p.info['create_time'],cpu=p.info['cpu_times'].user+p.info['cpu_times'].system));break
                except (psutil.Error,AttributeError):pass
            for count in (1,2,3):
                group=[r for r in rows if r['benchmark']==count]
                value=peaks.setdefault(str(count),dict(solvers=0,checkers=0,all_slots=0))
                value['solvers']=max(value['solvers'],sum(r['name'].lower()!='drat-trim-mingw.exe' for r in group))
                value['checkers']=max(value['checkers'],sum(r['name'].lower()=='drat-trim-mingw.exe' for r in group))
                value['all_slots']=max(value['all_slots'],len(group))
            log.write(json.dumps(dict(utc_epoch=time.time(),processes=rows))+'\n');log.flush()
            atomic_json(AREA/'SOLVER_CONCURRENCY.json',peaks)
            results=AREA/'BENCHMARKS.json'
            if results.exists() and json.loads(results.read_text()).get('status')=='PASS':break
            time.sleep(.5)

if __name__=='__main__':main()
