"""Portable integrity of original-thread-only repair; no native execution."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read('validation/S035/thread-repair/MANIFEST.json')
for name,row in m['files'].items():
 p=ROOT/name
 if sha(p)!=row['sha256']:p=ROOT/'validation/S035/thread-repair/frozen-source'/(row['sha256']+'.bytes')
 assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
c=read('validation/S035/thread-repair/CONTROLS.json');assert c['status']=='PASS' and not c['scientific_processes_touched'] and c['forced_terminations']==0
for name,h in c['source_sha256'].items():assert sha(ROOT/name)==h,name
policy=read('validation/S035/thread-repair/THREAD_POLICY.json');assert policy['status']=='CLASSIFIED_HELPERS_REMAIN_SUSPENDED'
assert policy['symbol_evidence']['symbol']=='TppWorkerThread' and policy['symbol_evidence']['displacement']==0
for pid,p in policy['processes'].items():
 assert all(r['suspend_count']>0 for r in p['quarantined_threads'])
 if p['kind']=='NATIVE_ORIGINAL_THREAD_ONLY':assert len(p['threads'])-len(p['quarantined_threads'])==1
assert read('validation/S035/thread-repair/SAT_CONTROLS.json')['status']=='PASS'
print('PASS published original-native-only policy, helper quarantine and lifecycle/SAT controls; not a scientific result')
