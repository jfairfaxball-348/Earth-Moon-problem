"""One preregistered post-queue source filter recovery; no concurrent heavy job."""
import json,os,sys,time,hashlib,subprocess,shutil,ctypes
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s026_supervision import atomic_json,run_step
from s026_check_source import graph
OUT=ROOT/'artifacts/tmp/S026-filter-recovery';OUT.mkdir(exist_ok=True)
os.environ['EMP_CADICAL']=str(ROOT/'artifacts/tmp/S004/cadical.exe')
os.environ['EMP_DRAT_TRIM']=str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert read(ROOT/'artifacts/tmp/S026-local/QUEUE.json')['status']=='QUEUE_FINISHED_NOT_A_SESSION_CLOSEOUT'
 assert read(ROOT/'artifacts/tmp/S026-audit/AUDIT.json')['status']=='FINISHED_WITH_EXPLICIT_PER_CASE_VERDICTS'
 import msvcrt
 lock=(ROOT/'artifacts/tmp/S026-local/RUN.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
 atomic_json(OUT/'SOURCE.json',dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256={str(p.relative_to(ROOT)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'tools/s026_containment.py',ROOT/'tools/s026_check_source.py',ROOT/'tools/s026_supervision.py']}))
 smoke=run_step([sys.executable,str(ROOT/'scripts/cloud_smoke.py')],2400,OUT/'smoke.log',OUT/'RUN_JOURNAL.jsonl',memory_kib=11*1024*1024)
 assert smoke['returncode']==0
 shutil.copyfile(ROOT/'artifacts/tmp/cloud_smoke/RESULT.json',OUT/'SMOKE.json')
 assert read(OUT/'SMOKE.json')['verdict']=='PASS'
 source=read(ROOT/'validation/S026/source/SUMMARY.json')
 r=next(x for x in source['candidates'] if x['name']=='P29-B14-0001')
 old=[x['tag'] for x in read(ROOT/'validation/S025/C5_CERTIFICATES.json') if x.get('certified')]
 new=[p.parent.name[3:] for p in sorted((ROOT/'artifacts/tmp/S026-local').glob('C5-*/SUMMARY.json')) if read(p)['verdict']=='NONBIPLANAR_CERTIFIED']
 output={'candidate':r,'cases':[],'verdict':'UNKNOWN'}
 try:
  for tag in new+old:
   d=OUT/tag;d.mkdir(exist_ok=True)
   atomic_json(d/'INPUT.json',dict(g6=r['g6'],w=r['w'],candidate=r['name'],tag=tag))
   edge=(ROOT/'artifacts/tmp/S026-local'/('C5-'+tag)/'graph.edges') if tag in new else ROOT/'validation/S025/certs'/('C5-'+tag+'.edges')
   assert graph('Dhc',list(map(int,tag)))=={tuple(map(int,x.split())) for x in edge.read_text().splitlines() if x.strip()}
   step=run_step([sys.executable,str(ROOT/'tools/s026_containment.py'),'decide',str(d/'INPUT.json'),str(d)],45,d/'run.log',OUT/'RUN_JOURNAL.jsonl',memory_kib=11*1024*1024)
   case=read(d/'RESULT.json') if step['returncode']==0 and (d/'RESULT.json').exists() else {'verdict':'UNKNOWN'}
   output['cases'].append(dict(tag=tag,process=step,**case))
   if case['verdict']=='CONTAINS_EXPLICIT_CHECKED':
    output.update(verdict='NONBIPLANAR_BY_CERTIFIED_SUBGRAPH',obstruction=tag,vertex_map=case['vertex_map']);break
   atomic_json(OUT/'SUMMARY.json',output)
  else:
   if output['cases'] and all(c['verdict']=='AVOIDS_DRAT_VERIFIED' for c in output['cases']):output['verdict']='AVOIDS_ALL_CERTIFIED_REQUIRES_CANDIDATE_STAGE'
  atomic_json(OUT/'SUMMARY.json',output);print(json.dumps({'filter_recovery':output['verdict'],'cases':len(output['cases'])}),flush=True)
 finally:
  ctypes.windll.kernel32.SetThreadExecutionState(0x80000000);lock.close()
if __name__=='__main__':main()
