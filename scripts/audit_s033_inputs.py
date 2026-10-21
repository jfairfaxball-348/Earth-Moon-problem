"""Restore frozen inputs without overwriting work, then independently audit all."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"artifacts/tmp/S032";out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/"validation/S032/start/INPUTS.json").read_text())
assert manifest["variables"]==17976 and manifest["base_clauses"]==336030
for name,h in manifest["sha256"].items():
    target=out/name
    if not target.exists():
        with gzip.open(ROOT/"validation/S032/start"/(name+".gz"),"rb") as source,target.open("xb") as dest:
            shutil.copyfileobj(source,dest)
    assert hashlib.sha256(target.read_bytes()).hexdigest()==h, "Existing runtime input differs; refusing overwrite"
inputs=out/"INPUTS.json"
if inputs.exists():assert json.loads(inputs.read_text())==manifest
else:inputs.write_text(json.dumps(manifest,indent=2)+"\n")
campaign=out/"campaign";campaign.mkdir(exist_ok=True)
rules=campaign/"learned.lem"
if not rules.exists():
    with gzip.open(ROOT/"validation/S032/stopped/learned.lem.gz","rb") as source,rules.open("xb") as dest:
        shutil.copyfileobj(source,dest)
assert hashlib.sha256(rules.read_bytes()).hexdigest()=="6e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177"
subprocess.run([sys.executable,str(ROOT/"scripts/audit_s033_fast.py")],check=True)
