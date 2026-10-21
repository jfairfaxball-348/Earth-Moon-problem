"""Fresh S032 full smoke, before every S032 scientific calculation."""
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s026_supervision import run_step,atomic_json

out=ROOT/'artifacts/tmp/S032';out.mkdir(parents=True,exist_ok=True)
os.environ['EMP_CADICAL']=str(ROOT/'artifacts/tmp/S004/cadical.exe')
os.environ['EMP_DRAT_TRIM']=str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe')
import pysolvers
env={'executor':'Codex desktop local Windows, S032 owner direct next-session invocation',
     'platform':platform.platform(),'python':sys.version,
     'packages':{k:version(k) for k in ('python-sat','networkx')},
     'pysolvers_sha256':hashlib.sha256(Path(pysolvers.__file__).read_bytes()).hexdigest(),
     'native':{k:{'path':os.environ[k],'sha256':hashlib.sha256(Path(os.environ[k]).read_bytes()).hexdigest()}
               for k in ('EMP_CADICAL','EMP_DRAT_TRIM')}}
atomic_json(out/'ENVIRONMENT.json',env)
r=run_step([sys.executable,str(ROOT/'scripts/cloud_smoke.py')],2400,
           out/'smoke.log',out/'JOURNAL.jsonl',memory_kib=11*1024*1024)
atomic_json(out/'GATE.json',r)
assert r['returncode']==0,r
s=json.loads((ROOT/'artifacts/tmp/cloud_smoke/RESULT.json').read_text())
assert s['verdict']=='PASS' and s['chromatic_rows_verified']==s['chromatic_cnf_byte_matches']==271
assert s['k9']['verified'] and s['solver_roundtrip']['fresh_proof_verified']
atomic_json(out/'SMOKE.json',s)
print('S032 fresh FULL271+K9 smoke PASS',flush=True)
