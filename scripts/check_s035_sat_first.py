"""Small non-computational SAT-priority regression checks; no native process."""
import importlib.util
import json
from pathlib import Path
import tempfile
import hashlib
import sys
import types
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sat_first',ROOT/'scripts/s035_sat_first_watch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.sat_signal('s SATISFIABLE\nv 1 -2 0\n')
assert m.sat_signal('{"reason":"OWNER_STOP","returncode":10}')
assert not m.sat_signal('s UNSATISFIABLE\n')
assert not m.sat_signal('c conflict count=10\nUNKNOWN')
with tempfile.TemporaryDirectory() as temporary:
    p=Path(temporary)/'attempts/cell-0000/visit';p.mkdir(parents=True)
    (p/'native.log').write_text('s SATISFIABLE\nv 1 0\n')
    (p/'native-RESULT.json').write_text(json.dumps(dict(returncode=10,reason='OWNER_STOP')))
    (p/'RESULT.json').write_text('{"status":"UNKNOWN"}')
    assert len(m.inspect(temporary))==2
    # Exercise alert-before-validation and failure priority without Windows APIs
    # or any real process. Failure must leave the prominent SAT alert intact.
    root=Path(temporary)
    (root/'GUARDIAN.json').write_text('{}')
    (root/'CONFIG.json').write_text('{}')
    (root/'RESIDENT_CONTEXTS.json').write_text('{"contexts":{}}')
    (p/'input.inst').write_text('preserved fixture input')
    def read(path):return json.loads(Path(path).read_text())
    def write(path,value):Path(path).write_text(json.dumps(value))
    def fail(*args):
        assert read(root/'SAT_ALERT.json')['ordinary_UNKNOWN_forbidden']
        raise ValueError('fixture independent validator rejects assignment')
    windows=types.SimpleNamespace(read_json=read,atomic_json=write,live_identity=lambda *a:False)
    regions=types.SimpleNamespace(checkpoint=lambda *a:None,sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest())
    engine=types.SimpleNamespace(independent_sat=fail,materialise=lambda *a,**k:None)
    with patch.dict(sys.modules,{'s035_windows':windows,'s035_regions':regions,'s035_engine':engine,'psutil':types.SimpleNamespace()}):
        alert=m.handle(root,m.inspect(root))
    assert alert['status']=='SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW'
    assert alert['verification'][0]['status']=='SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED'
    assert (root/'STOP').exists() and (p/'input.inst').read_text()=='preserved fixture input'
print('PASS SAT marker/exit 10 dominates UNKNOWN or stop reason; no solver launched')
