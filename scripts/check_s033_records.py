"""Portable S033 evidence integrity; does not replace same-phone native replay."""
import gzip
import hashlib
import json
import tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text())
manifest=read("sessions/S033/MANIFEST.json")
for name,row in manifest["files"].items():
    p=ROOT/name
    assert p.stat().st_size==row["bytes"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row["sha256"],name
s=read("validation/S033/SUMMARY.json")
smoke=read("validation/S033/SMOKE.json")
c=read("validation/S033/NATIVE_CONTROLS.json")
a=read("validation/S033/INPUT_AUDIT.json")
l=read("validation/S033/LIFECYCLE.json")
d=read("validation/S033/DIAGNOSTIC.json")
assert s["mobile_verdict"]=="PHONE_READY_VALIDATED"
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==smoke["chromatic_cnf_byte_matches"]==271
assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
assert c["exhaustive_n5_fixed_graphs"]==1024 and c["random_n6_partitions"]==64
assert c["K33"]==c["positive24"]=="PASS" and c["free_K9"]=="UNKNOWN_AT_2S"
assert a["status"]=="PASS" and a["bijective_renaming_checked"]
assert a["base_clauses"]==336030 and a["variables"]==17976 and a["independently_checked_native_clauses"]==2579937
assert a["lemma_sha256"]=="6e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177"
assert l["status"]=="PASS" and len(l["rows"])==4 and l["coverage_SIGTERM_cleanup"]
assert all(r["record"]["verdict"]=="UNKNOWN" for r in l["rows"])
assert d["retained_rules_in_input"]==2579937 and d["verdict"]=="UNKNOWN"
assert d["proof_backing"]["baseline_cell128"]["status"]=="UNSAT_DRAT_VERIFIED"
assert c["native_sha256"]==d["native_sha256"]==s["native_sha256"]
with tarfile.open(ROOT/"validation/S033/native.tar.gz") as archive:
    assert hashlib.sha256(archive.extractfile("native/bipsat_s033").read()).hexdigest()==c["native_sha256"]
with tarfile.open(ROOT/"validation/S033/controls-and-diagnostics.tar.gz") as archive:
    for name,h in d["proof_backing"]["baseline_cell128"]["certificate"].items():
        relative=name.split("/artifacts/tmp/S033/",1)[1]
        assert hashlib.sha256(archive.extractfile(relative).read()).hexdigest()==h

assert s["S11_m155_156"]=="UNKNOWN" and all(s[k]=="NOT_RUN" for k in ("S10","S9","S8"))
assert not s["witness_established"] and not s["S034_executed"]
assert s["range"]=={"lower":9,"upper":12}
f=read("validation/S033/FRESH_K9.json")
assert hashlib.sha256(gzip.decompress((ROOT/f["permanent_identical_bytes_archive"]).read_bytes())).hexdigest()==f["fresh_solver_proof_sha256"]
prompt=(ROOT/"sessions/S033/S034_FUTURE_PROMPT.md").read_bytes()
state=read("authoritative/STATE.json")
if state["last_completed_session"]=="S033":
    assert state["recommended_next_session"]=="S034" and state["next_session_is_future_unexecuted"]
    assert prompt==(ROOT/"authoritative/NEXT_SESSION_PROMPT.md").read_bytes()
executed=(ROOT/"sessions/S033/EXECUTED_PROMPT.md").read_bytes()
assert hashlib.sha1(b"blob "+str(len(executed)).encode()+b"\0"+executed).hexdigest()==read("docs/D072_S033_PHONE_TEST_DIRECTIVE.json")["active_prompt_git_blob_sha"]
print("PASS S033 mobile evidence integrity; same-environment replay still required for future science")
