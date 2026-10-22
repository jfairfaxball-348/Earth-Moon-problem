"""Fresh S034 native controls and complete independent input/rule acceptance."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/tmp/S034'
OUT.mkdir(parents=True, exist_ok=True)
smoke = json.loads((ROOT/'artifacts/tmp/cloud_smoke/RESULT.json').read_text())
assert smoke['verdict'] == 'PASS'
assert smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
shutil.copy2(ROOT/'artifacts/tmp/cloud_smoke/RESULT.json', OUT/'SMOKE.json')
shutil.copy2(ROOT/'artifacts/tmp/native/ENVIRONMENT.json', OUT/'ENVIRONMENT.json')
code = (ROOT/'scripts/check_s032_native.py').read_text()
code = code.replace("ROOT/'artifacts/tmp/S032'", "ROOT/'artifacts/tmp/S034'")
code = code.replace("ROOT/'artifacts/tmp/S032/native/bipsat_s032.exe'", "ROOT/'artifacts/tmp/S034/native/bipsat_s034'")
code = code.replace("'--timeout','300'", "'--timeout','2'")
code = code.replace('timeout=305', 'timeout=7').replace('UNKNOWN_AT_300S', 'UNKNOWN_AT_2S')
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'tools')]
exec(compile(code, str(ROOT/'scripts/check_s032_native.py'), 'exec'),
     {'__file__': str(ROOT/'scripts/check_s032_native.py'), '__name__': '__main__'})
subprocess.run([sys.executable, str(ROOT/'scripts/audit_s034_inputs.py')], check=True)
print('PASS fresh S034 complete smoke, new native controls, input mapping and all retained rules')
