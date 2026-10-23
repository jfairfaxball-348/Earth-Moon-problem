"""Real disposable Windows controls for frozen helper/original-thread isolation."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import hashlib
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
import s035_preserved_lifecycle as life
from s035_windows import atomic_json
WORKER=r'''
import ctypes,time,sys
from pathlib import Path
from ctypes import wintypes as W
p=Path(sys.argv[1]);code=int(sys.argv[2]);k=ctypes.WinDLL('kernel32');k.GetCurrentThreadId.restype=W.DWORD
(p/'MAIN_TID').write_text(str(k.GetCurrentThreadId()))
CALLBACK=ctypes.WINFUNCTYPE(None,ctypes.c_void_p,ctypes.c_void_p)
@CALLBACK
def worker(a,b):
 n=0
 while not (p/'EXIT').exists():
  n+=1;(p/'pool').write_text(str(n));time.sleep(.01)
k.TrySubmitThreadpoolCallback.argtypes=[CALLBACK,ctypes.c_void_p,ctypes.c_void_p];k.TrySubmitThreadpoolCallback.restype=W.BOOL
assert k.TrySubmitThreadpoolCallback(worker,None,None)
n=0
while not (p/'EXIT').exists():
 n+=1;(p/'main').write_text(str(n));time.sleep(.01)
sys.exit(code)
'''
def wait(predicate,seconds=5):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if predicate():return
  time.sleep(.01)
 raise AssertionError('Fixture timeout')
def start(path,code=0):
 path.mkdir();p=subprocess.Popen([sys._base_executable,'-c',WORKER,str(path),str(code)],creationflags=subprocess.CREATE_NO_WINDOW)
 wait(lambda:(path/'pool').exists() and (path/'main').exists())
 ident=life.identity(p.pid);rows=life.pause_identity(ident);main=int((path/'MAIN_TID').read_text());quarantine=[r for r in rows if r['tid']!=main];assert quarantine
 return dict(p=p,worker=ident,directory=path,rows=rows,quarantine=quarantine,main=main)
def finish(f):
 (f['directory']/'EXIT').touch()
 if f['p'].poll() is None:
  rows=life.pause_identity(f['worker']);life.resume_identity(f['worker'],rows,f['quarantine'])
 f['p'].wait(timeout=5)
def run():
 results=[]
 with tempfile.TemporaryDirectory(prefix='s035-thread-repair-') as td:
  root=Path(td);f=start(root/'isolation')
  try:
   import psutil
   psutil.Process(f['worker']['pid']).suspend()
   assert all(r['suspend_count']==2 for r in life.thread_counts(f['worker']))
   assert all(r['suspend_count']==2 for r in life.pause_identity(f['worker']))
   pool=(f['directory']/'pool').read_text();before=(f['directory']/'main').read_text()
   for turn in range(3):
    rows=life.thread_counts(f['worker']);damaged=copy.deepcopy(rows);damaged[0]['created_ticks']='0'
    try:life.resume_identity(f['worker'],damaged,f['quarantine']);raise AssertionError('wrong identity accepted')
    except life.LifecycleError:pass
    assert life.thread_counts(f['worker'])==rows
    with patch('psutil.Process.status',side_effect=AssertionError('Status heuristic forbidden')):
     life.resume_identity(f['worker'],rows,f['quarantine']);time.sleep(.12);rows=life.pause_identity(f['worker'])
    assert (f['directory']/'pool').read_text()==pool
    assert (f['directory']/'main').read_text()!=before;before=(f['directory']/'main').read_text()
   results.append('three same-identity turns: original progresses, helper frozen; status labels ignored')
   handle=life.ProcessHandle(f['worker']);finish(f);assert handle.poll()==0;handle.close()
  finally:
   if f['p'].poll() is None:finish(f)
  for code in (10,20):
   f=start(root/f'exit-{code}',code);h=life.ProcessHandle(f['worker']);finish(f);assert h.poll()==code;h.close()
  results.append('natural exits0/10/20 retained; no force termination')
  import s035_preserved_campaign as campaign
  area=root/'scheduler';control=area/'RESUME_CONTROL';control.mkdir(parents=True);(area/'STOP').touch()
  fixtures=[start(root/f'slot-{i}') for i in range(4)];contexts=[];policy=dict(status='CLASSIFIED_HELPERS_REMAIN_SUSPENDED',processes={})
  try:
   for i,f in enumerate(fixtures):
    (f['directory']/'native.log').write_text('c fixture\n');w=f['worker'];contexts.append(dict(cell=i,worker=w,directory=str(f['directory']),turns=0,active_seconds=0,state='PAUSED',quarantined_threads=f['quarantine'],input_sha256='fixture',native_sha256='fixture'))
    policy['processes'][str(w['pid'])]=dict(start_ticks=w['start_ticks'],kind='NATIVE_ORIGINAL_THREAD_ONLY',threads=f['rows'],quarantined_threads=f['quarantine'])
   atomic_json(control/'THREAD_POLICY.json',policy);planned=dict(contexts=contexts,original_processes=[f['worker'] for f in fixtures])
   with patch.object(campaign,'published_acceptance',lambda c:{}),patch.object(campaign,'plan',lambda a:copy.deepcopy(planned)),patch.object(campaign,'input_gates',lambda *a:{}),patch.object(campaign,'watcher',lambda c:life.identity(__import__('os').getpid())):
    campaign.run(area,control,pilot_seconds=8)
   a=json.loads((control/'ADOPTION.json').read_text());assert a['status']=='PAUSED' and not a['pause_errors'];assert all(c['turns']>=2 for c in a['contexts'])
   events=[json.loads(x) for x in (control/'JOURNAL.jsonl').read_text().splitlines()];active=set();peak=0
   for e in events:
    if e['kind']=='same_identity_resumed':active.add(e['cell']);peak=max(peak,len(active))
    if e['kind']=='fair_turn_paused':active.discard(e['cell'])
   assert peak==2
   results.append('real four-resident/two-slot scheduler, repeated turns, STOP preservation and frozen helpers')
   a['controller']=dict(pid=2147483000,start_ticks='0');a['watcher']=dict(pid=2147483001,start_ticks='0')
   atomic_json(control/'ADOPTION.json',a)
   with patch.object(campaign,'published_acceptance',lambda c:{}),patch.object(campaign,'plan',lambda a:copy.deepcopy(planned)):
    campaign.rearm_pilot(area,control)
   assert not (control/'STOP').exists() and (area/'STOP').exists()
   assert all(all(t['suspend_count']>0 for t in life.thread_counts(f['worker'])) for f in fixtures)
   results.append('classified rearm archives separate controls without any resume or original STOP mutation')
  finally:
   for f in fixtures:
    if f['p'].poll() is None:finish(f)
 import s035_preserved_campaign as campaign
 out=ROOT/'validation/S035/thread-repair/CONTROLS.json';atomic_json(out,dict(status='PASS',controls=results,scientific_processes_touched=False,forced_terminations=0,source_sha256=campaign.sources(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
 print('PASS',json.dumps(results),flush=True)
if __name__=='__main__':run()
