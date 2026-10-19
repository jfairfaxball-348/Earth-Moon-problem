"""S030 entry gate, no scientific search before fresh full smoke PASS."""
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s026_supervision import run_step, atomic_json

out = ROOT / 'artifacts/tmp/S030'
out.mkdir(parents=True, exist_ok=True)
os.environ['EMP_CADICAL'] = str(ROOT / 'artifacts/tmp/S004/cadical.exe')
os.environ['EMP_DRAT_TRIM'] = str(ROOT / 'artifacts/tmp/S004/drat-trim-mingw.exe')
env = {'executor': 'Codex desktop local Windows, owner invoked S030',
       'platform': platform.platform(), 'python': sys.version,
       'packages': {x: version(x) for x in ('python-sat', 'networkx')},
       'native': {k: {'path': v, 'sha256': hashlib.sha256(Path(v).read_bytes()).hexdigest()}
                  for k, v in os.environ.items() if k in ('EMP_CADICAL', 'EMP_DRAT_TRIM')}}
atomic_json(out / 'ENVIRONMENT.json', env)
r = run_step([sys.executable, str(ROOT / 'scripts/cloud_smoke.py')], 2400,
             out / 'smoke.log', out / 'JOURNAL.jsonl', memory_kib=11*1024*1024)
atomic_json(out / 'GATE.json', r)
assert r['returncode'] == 0, r
res = json.loads((ROOT / 'artifacts/tmp/cloud_smoke/RESULT.json').read_text())
assert res['verdict'] == 'PASS' and res['chromatic_rows_verified'] == 271, res.keys()
atomic_json(out / 'SMOKE.json', res)
print('Full S030 271+K9 smoke PASS', flush=True)
