"""Post-candidate structural audit; UNKNOWN subgraphs never transfer negatives."""
import json,os,sys,subprocess,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from s026_supervision import run_step,atomic_json
from s026_check_source import graph
OUT=ROOT/'artifacts/tmp/S026-filter-recovery/pending-profile'
os.environ['EMP_CADICAL']=str(ROOT/'artifacts/tmp/S004/cadical.exe');os.environ['EMP_DRAT_TRIM']=str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert (ROOT/'artifacts/tmp/S026-filter-recovery/CANDIDATE_STAGE.json').exists()
 import msvcrt
 lock=(ROOT/'artifacts/tmp/S026-local/RUN.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 OUT.mkdir(exist_ok=True)
 try:
  atomic_json(OUT/'SOURCE.json',dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256={str(p.relative_to(ROOT)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'tools/s026_containment.py',ROOT/'tools/s026_check_source.py',ROOT/'tools/s026_supervision.py']}))
  src=ROOT/'artifacts/tmp/S026-filter-recovery/candidate/SMOKE.json';assert read(src)['verdict']=='PASS';shutil.copyfile(src,OUT/'SMOKE.json')
  # Same environment and unchanged algorithm as the candidate's fresh smoke.
  r=read(ROOT/'artifacts/tmp/S026-filter-recovery/SUMMARY.json')['candidate'];result={'candidate':r['name'],'transfer_policy':'NO_NEGATIVE_TRANSFER_FROM_UNKNOWN_C5','cases':[]}
  for tag in ['23435','24344','24425','33344','33434']:
   d=OUT/tag;d.mkdir(exist_ok=True);atomic_json(d/'INPUT.json',dict(g6=r['g6'],w=r['w'],candidate=r['name'],tag=tag))
   assert graph('Dhc',list(map(int,tag)))=={tuple(map(int,x.split())) for x in (ROOT/'artifacts/tmp/S026-local'/('C5-'+tag)/'graph.edges').read_text().splitlines() if x.strip()}
   step=run_step([sys.executable,str(ROOT/'tools/s026_containment.py'),'decide',str(d/'INPUT.json'),str(d)],45,d/'run.log',OUT/'RUN_JOURNAL.jsonl',memory_kib=11*1024*1024)
   c=read(d/'RESULT.json') if step['returncode']==0 and (d/'RESULT.json').exists() else {'verdict':'UNKNOWN'}
   result['cases'].append(dict(tag=tag,process=step,**c));atomic_json(OUT/'SUMMARY.json',result)
  print(json.dumps({'pending_profile':[(c['tag'],c['verdict']) for c in result['cases']]}),flush=True)
 finally:lock.close()
if __name__=='__main__':main()
