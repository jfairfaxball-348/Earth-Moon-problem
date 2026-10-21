"""Proof-backed cell128 diagnostic on the real native engine; no new graph result."""
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/"artifacts/tmp/S033"
py=sys.executable
coverage=[py,str(ROOT/"scripts/s033_coverage.py")]
base=AREA/"coverage-base"
full=AREA/"coverage-full"
subprocess.run(coverage+["init","--base-only","--directory",str(base)],check=True,stdout=subprocess.DEVNULL)
subprocess.run(coverage+["check","--directory",str(base),"--cell","128","--seconds","15"],check=True,stdout=subprocess.DEVNULL)
ledger=json.loads((base/"coverage.json").read_text())
assert ledger["cells"][128]["status"]=="UNSAT_DRAT_VERIFIED"
subprocess.run(coverage+["init","--directory",str(full)],check=True,stdout=subprocess.DEVNULL)
subprocess.run(coverage+["export","--directory",str(full),"--cell","128"],check=True,stdout=subprocess.DEVNULL)
subprocess.run([py,str(ROOT/"scripts/s033_phone.py"),"run","--input",str(full/"cell-0128.inst"),"--seconds","30"],check=True,stdout=subprocess.DEVNULL)
r=json.loads((AREA/"PHONE.json").read_text())
r["proof_backing"]={"baseline_cell128":ledger["cells"][128],"meaning":"baseline encoder/symmetry UNSAT implies augmented input UNSAT; no new graph exclusion"}
r["retained_rules_in_input"]=2579937
(ROOT/"validation/S033/DIAGNOSTIC.json").write_text(json.dumps(r,indent=2)+"\n")
print(json.dumps(r,indent=2))
