"""Package completed S033 acceptance; never starts S034 or rewrites S032."""
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"validation/S033"
AREA=ROOT/"artifacts/tmp/S033"
def load(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2)+"\n")
def append(p,text):
    s=p.read_text()
    if text.strip() not in s:p.write_text(s+"\n"+text+"\n")
smoke=load(OUT/"SMOKE.json");controls=load(OUT/"NATIVE_CONTROLS.json")
audit=load(OUT/"INPUT_AUDIT.json");life=load(OUT/"LIFECYCLE.json");diag=load(OUT/"DIAGNOSTIC.json")
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271
assert audit["status"]==life["status"]=="PASS"
assert controls["native_sha256"]==diag["native_sha256"]
assert diag["status"]=="FINISHED_UNKNOWN" and diag["returncode"]==20
assert diag["proof_backing"]["baseline_cell128"]["status"]=="UNSAT_DRAT_VERIFIED"
summary={"session":"S033","mobile_verdict":"PHONE_READY_VALIDATED","architecture":"aarch64","phone_model":"SM-S921B","platform":"Android16 / Termux / Debian13 proot","full_smoke":"PASS_271_PLUS_RETAINED_AND_FRESH_K9","native_sha256":controls["native_sha256"],"native_controls":controls["status"],"free_native_K9":"UNKNOWN_AT_2S","rules":2579937,"input_audit":"PASS","input_audit_seconds":audit["seconds"],"audit_networkx_comparison_controls":audit["networkx_comparison_controls"],"lifecycle":"PASS","diagnostic_status":diag["status"],"diagnostic_wall_seconds":diag["wall_seconds"],"diagnostic_cpu_seconds":diag.get("cpu_seconds"),"diagnostic_peak_rss_kib":diag["peak_rss_kib"],"thermal":"UNAVAILABLE; no thermal/throttling guarantee","caps":{"workers":1,"native_wall_max_seconds":30,"rss_kib":1048576,"disk_reserve_bytes":4*1024**3},"S11_m155_156":"UNKNOWN","S10":"NOT_RUN","S9":"NOT_RUN","S8":"NOT_RUN","range":{"lower":9,"upper":12},"witness_established":False,"certified_strata":[],"S034_executed":False,"windows_support":"build scripts retained; Windows execution not tested on ARM64","rollback":"ordinary git revert of S033 commit; preserve later work"}
write(OUT/"SUMMARY.json",summary)
# Preserve actual generated engine, native bytes and licensing; no old artifacts altered.
with tarfile.open(OUT/"native.tar.gz","w:gz") as t:
    for name in ("bipsat_s032.cpp","bipsat_s033","BUILD.json","build.log"):
        t.add(AREA/"native"/name,arcname="native/"+name)
    for name in ("LICENSE","NOTICE.md"):
        t.add(AREA/"bipsat2"/name,arcname="bipsat2/"+name)
    t.add(ROOT/"validation/S032/start/THIRD_PARTY_NOTICES.md",arcname="THIRD_PARTY_NOTICES.md")
with tarfile.open(OUT/"controls-and-diagnostics.tar.gz","w:gz") as t:
    for name in ("controls-v2","coverage-base"):
        t.add(AREA/name,arcname=name)
    for p in AREA.glob("diagnostic-*"):
        if p.is_dir():t.add(p,arcname=p.name)
    for p in AREA.glob("*-controller.log"):t.add(p,arcname=p.name)
    for name in ("coverage.json","REPORT.json","cell-0128.json"):
        p=AREA/"coverage-full"/name
        if p.exists():t.add(p,arcname="coverage-full/"+name)
scripts=["scripts/build_s033_native.py","scripts/check_s033_phone.py","scripts/s033_phone.py","scripts/s033_coverage.py","scripts/audit_s033_inputs.py","scripts/audit_s033_fast.py","scripts/check_s033_lifecycle.py","scripts/check_s033_diagnostic.py","scripts/check_s033_records.py","scripts/close_s033_records.py","scripts/cloud_setup.sh","scripts/s032_coverage.py","scripts/s033_coverage_core.py","tools/s026_supervision.py","scripts/build_s032_native.py","scripts/check_s032_native.py","scripts/replay_s030_search.py","tools/s032_subdivision.hpp"]
with tarfile.open(OUT/"source-bytes.tar.gz","w:gz") as t:
    for name in scripts:t.add(ROOT/name,arcname=name)
state_path=ROOT/"authoritative/STATE.json";state=load(state_path)
assert state["last_completed_session"] in ("S032","S033")
state.update(as_of="2026-10-21",last_completed_session="S033",recommended_next_session="S034",next_session_is_future_unexecuted=True,latest_session_branch="main",latest_session_entry_main="0155145c4b164e4f6ca85cac351d13047dd71bc4",next_session_priority="S034 FUTURE: real bounded solver session after fresh full phone acceptance and practical budget; D071 exact region scheduling; initially ONE worker.")
state["s033_environment"]=summary
state["headline_status"]="OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S033"
state["open_obligations"]=["S034 FUTURE/UNEXECUTED; no automatic solver campaign. Fresh same-phone acceptance and practical finite campaign budget required.","S11 m155/156 UNKNOWN; regular154 SOURCE_STATED, finite RUP branches only.","S10/S9 NOT_RUN; delta>=9 conditional on SRC0037; unconditional S8 NOT_RUN.","All parked queues/publication/formalisation gates unchanged;9<=chi2<=12. Thermal readings unavailable."]
state["latest_session_integration"]={"status":"DIRECT_MAIN_COMMIT_PUSH_TO_BE_VERIFIED_AFTER_COMMIT","entry_main":"0155145c4b164e4f6ca85cac351d13047dd71bc4","authority":"D072 same-main/no-PR override"}
write(state_path,state)
shutil.copyfile(ROOT/"sessions/S033/S034_FUTURE_PROMPT.md",ROOT/"authoritative/NEXT_SESSION_PROMPT.md")
close=("# S033 closeout — PHONE_READY_VALIDATED\n\n"
"The real guarded S032 bipsat2 engine compiled and ran on Samsung SM-S921B, aarch64 Debian13/proot, Android16. Full phone-local271/271 CNF byte-identity and independent DRAT plus retained/fresh K9 PASS. All1024 n5 fixed graphs,64 n6 partitions,K33 and positive24 PASS. Free native K9 remains UNKNOWN at2s.\n\n"
"All2579937 retained clauses and exact336030-clause/17976-variable mapping independently audited. Hash/size preserved:189309949 bytes,SHA2566e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177. The unfinished NetworkX audit was stopped for performance; a separate adjacency validator was cross-checked against NetworkX before completing EVERY clause. No partial audit counted.\n\n"
"Real-native bounded completion, STOP, SIGTERM, duplicate-worker rejection and unexpected controller-kill/recovery PASS; all outcomes UNKNOWN. Proof-backed cell128 diagnostic includes all retained clauses. Baseline cell128 standalone CaDiCaL DRAT was independently checked; this is inherited encoder/symmetry closure, not a new graph result. Diagnostic wall/CPU/RSS/disk values are in validation/S033/DIAGNOSTIC.json.\n\n"
"One-worker diagnostics only,30s maximum native wall,1GiB observed tree RSS,4GiB disk reserve. Thermal sensors and Termux version were unavailable; no thermal/throttling or unattended-runtime guarantee. Android may kill background work; wake lock does not prevent every kill. No S032 restart or S034 execution. Classical9<=chi2<=12; S11m155/156 UNKNOWN; regular154 SOURCE_STATED; S10/S9/S8 NOT_RUN. No witness/stratum/novelty/formalisation/publication advance.\n\n"
"Windows builders and archived binaries retained. Windows execution could not be tested on ARM64. Phone guide:docs/S033_PHONE_GUIDE.md; rollback with ordinary git revert, preserving subsequent work. Complete commands/source/input/native hashes, logs, source snapshots and actual native bytes are permanent under validation/S033. Fresh K9 proof matches the existing archived bytes exactly; FRESH_K9.json records the permanent content reference.\n\n"
"D072 main-only/no-PR override applies. Entry main0155145c4b164e4f6ca85cac351d13047dd71bc4,tree e440c71427b62cabf848e5fce8f062b734d75049; zero open PRs, entry hosted validate SUCCESS (run39659084174/job119427051632); protection UNKNOWN HTTP401. Commit/push and post-push hosted identities must be verified live after the authored commit. No invented PR/merge.\n\n"
"S034 is FUTURE/UNEXECUTED. Its complete prompt is identical in authoritative/NEXT_SESSION_PROMPT.md and sessions/S033/S034_FUTURE_PROMPT.md. D044 alternate runner:ubuntu-24.04,pinned setup plus full same-job smoke; permanent validation/S011/SUMMARY.json and S012 evidence; historical runs38623187997,38623722547,38624616691,38635879431 do not validate the phone.\n")
(ROOT/"sessions/S033/CLOSEOUT.md").write_text(close)
append(ROOT/"docs/SESSION_LEDGER.md","| S033 | 2026-10-21 | D047 invocation, D072 ARM64 phone setup; existing main | PHONE_READY_VALIDATED: real native build, full271+K9 smoke,1024n5/K33/positive24, full rules/mapping audit, STOP/signal/kill recovery; no math advance | Complete; S034 FUTURE/UNEXECUTED |")
append(ROOT/"docs/DECISION_LOG.md","S033 execution (2026-10-21,D072/D047): owner invoked phone setup with run next session. Validated existing guarded solver on ARM64; direct main/no PR, reversible compatibility changes, no S034 execution or scientific scope change.")
append(ROOT/"docs/PHASE_GATE_LEDGER.md","S033 (2026-10-21): PHONE_READY_VALIDATED environment only. Phase1 lower-bound gate NOT PASSED; no witness or stratum decision;9<=chi2<=12. Parked/publication/formalisation gates unchanged.")
append(ROOT/"docs/FAILURE_LEDGER.md","S033 environment observations: bubblewrap cannot start in proot because of host-mount layout; authorized direct commands used. Missing Debian venv package installed. Frozen S032 coverage script restored exactly; tested POSIX equivalent lives in s033_coverage_core.py. Observed normal-exit/RSS sampling race fixed and lifecycle/full-input diagnostics repeated. Slow incomplete NetworkX archive audit replaced by independently cross-checked adjacency audit, then all clauses checked. Thermal/Termux-version readings unavailable. Native freeK9 capped UNKNOWN; no mathematical negative inferred.")
append(ROOT/"campaigns/README.md","S033: environment validation only (no new search campaign). PHONE_READY_VALIDATED; full evidence validation/S033. CAM-0038 remains OWNER_STOPPED_UNKNOWN; S034 solver work is FUTURE/UNEXECUTED.")
header="# S033 completed — ARM64 phone validated (2026-10-21)\n\nPHONE_READY_VALIDATED: real guarded native build, full271+retained/fresh K9 smoke,1024n5/K33/positive24, full retained-rule/mapping audit and STOP/signal/kill recovery PASS. Free native K9 UNKNOWN at2s. Thermal readings unavailable; short one-worker diagnostics only. Classical9<=chi2<=12; S11 UNKNOWN, S10/S9/S8 NOT_RUN. S034 is FUTURE/UNEXECUTED and requires fresh owner invocation. D072 same-main/no-PR and rollback rules continue. See sessions/S033/CLOSEOUT.md and docs/S033_PHONE_GUIDE.md.\n\n"
p=ROOT/"AGENTS.md"
if not p.read_text().startswith("# S033 completed"):p.write_text(header+p.read_text())
p=ROOT/"authoritative/START_HERE.md"
if not p.read_text().startswith("# S033 completed"):p.write_text(header+p.read_text())
p=ROOT/".github/workflows/scaffold.yml";s=p.read_text()
if "check_s033_records.py" not in s:s+="      - name: Validate S033 ARM64 environment evidence integrity\n        run: python scripts/check_s033_records.py\n"
p.write_text(s)
files={}
for p in [*OUT.rglob("*"),* (ROOT/"sessions/S033").glob("*.md")]:
    if p.is_file():files[str(p.relative_to(ROOT))]={"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
write(ROOT/"sessions/S033/MANIFEST.json",{"purpose":"immutable S033 environment evidence; not new mathematics","files":files})
print(json.dumps(summary,indent=2))
