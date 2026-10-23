"""Install audited S035 closeout and the owner-invoked S036 long-search handover."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/S035/closeout'

def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,s):(ROOT/p).write_text(s,encoding='utf-8',newline='\n')
def js(p,v):write(p,json.dumps(v,indent=2)+'\n')
def append(p,s):write(p,(ROOT/p).read_text(encoding='utf-8')+'\n'+s+'\n')
def freeze(p):
    data=(ROOT/p).read_bytes();h=hashlib.sha256(data).hexdigest()
    q=ROOT/'validation/S035/thread-repair/frozen-source'/(h+'.bytes')
    if not q.exists():q.write_bytes(data)

def main():
    audit=read('validation/S035/closeout/AUDIT.json')
    receipt=read('validation/S035/closeout/DELTA_VERIFICATION.json')
    assert audit['proof_closed_regions']==247 and receipt['status']=='PASS_ACTUAL_RESTORE_ALL_DELTA_FILE_HASHES'
    assert read('validation/S035/closeout/SAT_RESCAN.json')['hits']==[]
    state=read('authoritative/STATE.json')
    assert state['last_completed_session']=='S034'
    for p in ['sessions/S035/INPUT.md','sessions/S035/RESEARCH.md','sessions/S035/ADVERSARIAL.md']:
        freeze(p)
    js('validation/S035/closeout/ENTRY_STATE.json',state)
    control=ROOT/'artifacts/tmp/S035/campaign/RESUME_CONTROL'
    for p in control.rglob('*'):
        if p.is_file() and p.suffix!='.lock':
            dest=OUT/'resume-control'/p.relative_to(control);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    prompt='''# S036 — SAT-first repair, targeted nine-region diagnostics and sustained search

FUTURE / UNEXECUTED. Supplying this prompt, or saying "run next session" in this
repository, invokes S036 only under D047. Do not execute S037. Work in
C:\\Earth-Moon-problem on existing main; ordinary non-force commits/pushes,
no new project, branch or PR under D074. Begin work immediately when invoked;
the objective includes starting and verifying a real long search after gates pass.

1. Read AGENTS.md, authoritative/STATE.json, sessions/S035/CLOSEOUT.md,
   FINAL_DIAGNOSTIC.md and RECOVERY_HANDOVER.md, validation/S035/closeout evidence,
   THREAD_REPAIR.md and the current RESUME_CONTROL records. Verify live remote
   main, exact PID/create-time/thread identities, source/native/input hashes,
   STOP latches and all archive receipts before process action. S035 is closed.
   Do not mistake its old RUNNING headers or expired leases for live authority.

2. SAT FIRST: scan all scientific roots, historical logs, candidate files and
   native exit records before UNKNOWN handling. Preserve complete assignment,
   immutable input/recipe, logs/sources/hashes before validation; safely suspend
   surviving native identities and report any potentially valid witness prominently.
   Independently validate CNF, order28, alpha<=3, registered degree/edge domain,
   disjoint planar layers/union and proper colouring using tools/s035_sat_validation.py.
   Failed validation stays SAT review. A feasible colouring is not a lower bound.

3. Repair the observed operational failure before sustained launch: the SAT
   scanner raised PermissionError opening RESUME_CONTROL/ADOPTION.json at
   2026-10-23 08:43:46-48 UTC. The guard paused all originals and exited; generic
   controller reason hid WATCHER_FAILURE. Add bounded Windows sharing retries to
   scanner stat/open/hash, commit scan-cache entries only after successful reads,
   keep complete cross-block SAT detection and fail closed on exhausted retries.
   Add real concurrent replacement/locked-read controls, SAT-during-retry and
   permanent-failure controls; preserve the original traceback and old source bytes.
   Establish fresh SAT/lifecycle acceptance and publish changes before heavy work.

4. Diagnose each UNKNOWN region separately:0,1,3,7,15,31,63,127,255.
   Four original RAM contexts0,7,127,255 may survive; five cold regions1,3,15,31,63
   have semantic recovery only. Preserve all surviving RAM; never force-kill,
   evict, duplicate or blindly resume. Original legacy controls and STOP stay
   frozen; classified ntdll!TppWorkerThread helpers never resume. Reuse only exact
   original native threads after fresh controlled acceptance. If identity is lost,
   preserve failure evidence and recover semantic state into a new registered
   S036 execution area; do not claim private CDCL recovery. Keep S035 artifacts immutable.

5. Register a genuinely changed, equal-input/active-CPU diagnostic strategy:
   preserve resident CDCL between turns, disable the measured harmful congruence
   simplifier and keep random walk default initially. Record per-region conflicts,
   decisions, propagations, geometric deltas, memory, native exits and proof stage.
   Investigate historical exit1 in15/31 and cold-region starvation. Compare bounded
   region-specific branching/inprocessing options before adopting one. Do not
   repeat identical short restarts or capped proofs without a changed strategy.
   Only independently audited geometric clauses may cross regions; arbitrary
   resident CDCL clauses are neither portable shared axioms nor certificates.

6. Fresh Windows acceptance requires full271 plus retained/fresh K9 smoke and
   pinned native/lifecycle/SAT/proof controls. Then start sustained search with
   two active slots/four resident contexts and600s fair turns; retain learning
   through UNKNOWNs and milestones with no arbitrary overall cutoff. Prove actual
   advancing counters and a full turn rotation, not just successful process launch.
   Cold admission or a third slot requires a registered capacity/fairness plan and
   measured safety; eight logical CPUs do not imply eight safe resident workers.
   Fresh standalone DRAT and independent checker gate every encoded closure;
   native UNSAT alone remains UNKNOWN. Preserve pending proofs and checkpoints.

7. Hard limits:6GiB aggregate private,2GiB per worker,2GiB available RAM floor,
   10GiB free disk reserve,2GiB raw proof per attempt,40GiB campaign/64GiB total
   session storage. Target5GiB cache/2.5GiB available RAM. Budget S035 archives
   and new S036 artifacts together when checking disk; pause before limits.
   Restore/hash-verify compression before removing raw duplicates. Thermal sensors
   unavailable; no thermal guarantee. Owner confirmed power/wifi/no-sleep earlier;
   verify actual conditions and guards. Stop only on owner instruction, safety,
   failure/blocker, validated candidate or complete certified encoded queue.

8. Baseline:247/256 encoded regions proof-closed, nine UNKNOWN; S11 m155/156
   UNKNOWN, regular154 SOURCE_STATED, S10/S9/S8 NOT_RUN,9<=chi2<=12.
   Encoded closures are neither individual graph exclusions nor whole-stratum
   proof. Preserve parked/publication/outreach/Lean gates. No SAT inference from
   difficulty, novelty guarantee, percent-to-solution or ETA. Keep synced records,
   exact recovery recipes and ordinary main publication. D044 fallback is pinned
   ubuntu-24.04 setup plus full271+K9 smoke in the SAME hosted job; permanent
   examples validation/S011/SUMMARY.json and validation/S012 evidence, historical
   runs38623187997/38623722547/38624616691/38635879431. Verify actual job steps;
   scaffold integrity is not mathematical replay or fresh environment acceptance.
   At closeout install identical complete S037 FUTURE prompts and print the full
   prompt with verified GitHub links. Do not start S037 automatically. Scheduled
   S035 heartbeat is disabled at closeout. After verified sustained S036 launch,
   establish two-hour status check-ins, including unchanged status, following the
   owner's monitoring preference; never auto-restart paused work. Independent
   SAT/safety supervision is mandatory between check-ins.
'''
    write('sessions/S035/S036_FUTURE_PROMPT.md',prompt)
    write('authoritative/NEXT_SESSION_PROMPT.md',prompt)
    close='''# S035 closeout — owner-stopped after SAT-supervisor read failure

S035 is COMPLETED_OWNER_STOP_UNKNOWN on23 October2026. No S036 computation
was started. All twelve original identities survive suspended, including the
four native contexts0,7,127,255; exact thread identities/counts and zero CPU
were rechecked. Private CDCL survives only in those live RAM images, not in a
durable checkpoint. Controller9880 and watcher3292 have exited. Both STOP
latches stay present; no forced termination, rearm, replacement or reset occurred.

The underlying stop was WATCHER_FAILURE, not mathematical stagnation: scanner
open('rb') raised PermissionError on RESUME_CONTROL/ADOPTION.json. Original
watcher traceback, GUARD_PAUSE and controller/journal evidence are preserved.
Windows concurrent file replacement is a plausible cause, not proven attribution.
The scan code lacked bounded open retries and advanced its cache before reading;
repair and acceptance are required before the next sustained run. The guard
successfully preserved the processes; generic OWNER_OR_SUPERVISOR_PAUSE masked
the underlying failure. Last preservation journal is08:43:48 UTC /09:43:48 BST.

247 encoded regions remain proof-closed and nine UNKNOWN. Initial Windows
acceptance independently replayed imported16 proofs; original successful checker
receipts for all247 were retained. Final audit reconstructed all247 exact formula
hashes and verified proof/archive and checker-log hashes. This was not a fresh
second DRAT replay. No new certificate was promoted during final closeout.
All accepted S035 geometric occurrences were independently subdivision-audited;
four entire retained geometric journals were separately audited. These overlap
earlier prefixes and are not globally unique/new counts. SAT rescan found no
scientific SAT/candidate/exit10 signal. No whole stratum or graph exclusion,
chi>=10 witness, ETA or headline advance:9<=chi2<=12, S11 UNKNOWN.

Recovery is layered: original byte-verified pause archive and dependencies,
external S034 archive, then verified closeout runtime-delta.tar.xz. Every changed
or additional runtime file was actually restored to a new root and hash-checked;
DELTA_INVENTORY.json maps unchanged files to original archives. No originals were
deleted. Advisory lock files are excluded explicitly; do not restore stale leases.
Original pre-upgrade container remains local and all its member bytes are also
preserved in the base archive. See RECOVERY_HANDOVER.md and exact receipts.

The owner requests a targeted long search in the next invoked S036. Its first
tasks are SAT-first audit, watcher sharing repair/controls, per-region strategy
and fresh Windows acceptance, then an actual supervised sustained launch. A new
chat alone does not improve search. Long-run learning retention and all nine
region diagnostics are required. No search is restarted during this closeout.

Existing main/no branch/no PR under D074. Ordinary non-force commit/push and
actual hosted validation are verified after publication; CI is packaging and
governance, not new proof replay. Sources unchanged; CLM-0121 records the finite
internal audit. Parked queues, outreach, publication and Lean remain gated.
'''
    write('sessions/S035/CLOSEOUT.md',close)
    a=read('artifacts/tmp/S035/campaign/RESUME_CONTROL/ADOPTION.json')
    ctx=read('validation/S035/closeout/CONTEXTS.json')['contexts']
    old=read('validation/S035/closeout/NINE_REGIONS.json')['regions']
    rows=['# S035 final nine-region diagnostic','',
          '| ID | Recovery state | Last conflicts | Proof/check backlog |',
          '|---:|---|---:|---|']
    for row in old:
        current=next((c for c in ctx if c['cell']==row['id']),None)
        counts=current['counters'] if current else row['largest_recorded_conflicts']
        rows.append(f"| {row['id']} | {'Suspended original RAM context' if current else 'Cold; semantic recovery'} | {counts['conflicts'] if counts else 'unavailable'} | None; UNKNOWN |")
    rows+=['','Native counters are last logged values, not exact at-stop instruction counts.',
        'Retained contexts completed multiple600s turns without new PID creation. The',
        'resumption stopped operationally at the SAT scanner PermissionError; it did',
        'not demonstrate exhaustion or a mathematical barrier. Cold1/3/63 had historical',
        'V1 memory eviction;15/31 had historical exit1 without adequate attribution.',
        'All five cold regions were unsearched by the sustained four-resident controller.',
        'No unresolved region has pending native UNSAT, proof generation or checker backlog.',
        '', 'Priority: repair watcher sharing/cache, retain the four RAM contexts, audit',
        'geometric additions, measure region-specific changes on identical inputs per',
        'active CPU second, attribute native exits and avoid indefinite cold starvation.',
        'Do not infer SAT from difficulty. No evidence currently justifies eight workers.']
    write('sessions/S035/FINAL_DIAGNOSTIC.md','\n'.join(rows)+'\n')
    write('sessions/S035/RECOVERY_HANDOVER.md','''# S035 recovery handover

Do not restart automatically. Invoke S036 using the paired complete prompt.
Read validation/S035/closeout/PROCESS_SNAPSHOT.json and live thread identities;
RAM learning survives only while exact original suspended processes survive.
Do not use legacy STOP/recover, remove original STOP, resume helpers or kill
anything. Existing controller/watcher are gone; no continuous active guard is
claimed for this closed paused run. Recheck RAM/disk before any new work.

Portable semantic recovery: use scripts/restore_s035_preserved.py to restore
the existing base pause archive/dependencies into a NEW root with bounded
descriptors and explicit path rebasing. Consult its --help; the previous full
restore passed and must not be overwritten. Resolve base runtime.tar.xz from
committed verified parts with tools/s035_archive_parts.py; external S034 proof
bytes are validation/S034/campaign.tar.xz. Then overlay only files labelled
CLOSEOUT_DELTA in validation/S035/closeout/DELTA_INVENTORY.json from the adjacent
runtime-delta.tar.xz, checking each size/SHA256 and safe relative destination.
Delta storage labels BASE_PAUSE_ARCHIVE and EXTERNAL_S034_ARCHIVE refer to the
original exact-byte inventories, not to current live copies. Original pre-upgrade
container is retained locally; its expanded member bytes are in the base archive.
No lock/lease/PID file is runnable authority in a restored directory. Rebase
recipes without altering frozen originals. Never claim archive restores CDCL RAM.

DELTA_VERIFICATION.json records an actual fresh-root restoration and all changed
file hashes, not just archive readability. Base ARCHIVE_VERIFICATION.json and
resume/full-restore receipts remain immutable. New geometric journals have
PREFIX_AUDIT.json receipts; deduplicate/register immutable blocks before sharing.
This closeout does not edit historical REGIONS, resident context or certificate
ledgers. New S036 claims must be written into a separate execution ledger.
''')
    state['as_of']='2026-10-23';state['last_completed_session']='S035'
    state['recommended_next_session']='S036';state['next_session_is_future_unexecuted']=True
    completed=state.pop('active_session');completed.update(status='COMPLETED_OWNER_STOP_UNKNOWN',all_processes_suspended=True,
        processes_exited=False,owner_resume_required=True,resumption_authorized=False,controller_alive=False,watcher_alive=False)
    state['s035_completed_runtime']=completed
    state['s035_science']=dict(proof_closed_regions=247,unresolved_ids=a['unresolved_ids'],verdict='UNKNOWN',
        whole_stratum_certified=False,witness=None,bounds=[9,12],audit='validation/S035/closeout/AUDIT.json')
    state['headline_status']='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S035'
    state['next_session_priority']='S036 FUTURE/UNEXECUTED: SAT-first watcher repair, targeted nine-region diagnostics, acceptance then real sustained search.'
    state['open_obligations']=[state['next_session_priority'],'S11 m155/156 UNKNOWN;247 encoded closures and nine UNKNOWN are not graph/stratum closure.',
        'Four suspended original RAM contexts survive only while exact processes survive; no durable CDCL snapshot.',
        'Regular154 SOURCE_STATED; S10/S9/S8 NOT_RUN; parked/publication/outreach/Lean gates unchanged;9<=chi2<=12.']
    state['latest_session_entry_main']='bef7b0131d72e6147f32b4d2e0a7885388f5c39d'
    state['latest_session_integration']=dict(status='VERIFY_COMMIT_REMOTE_AND_ACTUAL_HOSTED_JOB_AFTER_PUBLICATION',
        entry_main=state['latest_session_entry_main'],authority='D074 existing-main owner closeout',branch='main',force=False)
    state['s035_closeout']=dict(status='COMPLETED_OWNER_STOP_UNKNOWN',cause='WATCHER_FAILURE_PERMISSIONERROR_ADOPTION_READ',
        heartbeat='DISABLED_AT_CLOSEOUT',private_cdcl_serialized=False,S036_executed=False)
    if 'CLM-0121' not in state['mathematical_results']:state['mathematical_results'].append('CLM-0121')
    js('authoritative/STATE.json',state)
    header='''# S035 CLOSED — S036 targeted long search FUTURE / UNEXECUTED (23 October2026)

Owner requested investigation/closeout and a next-session long-search prompt.
S035 stopped after SAT-watcher PermissionError on ADOPTION.json; all original
identities remain suspended and private learning is RAM-only. Controller/watcher
have exited; do not infer RUNNING from historical headers below. Read
sessions/S035/CLOSEOUT.md, FINAL_DIAGNOSTIC.md, RECOVERY_HANDOVER.md and the paired
authoritative/NEXT_SESSION_PROMPT.md / sessions/S035/S036_FUTURE_PROMPT.md.
No automatic resume, cold admission, helper/legacy wake or S036 execution in
this closeout. The next owner invocation authorises S036 repair/acceptance then
sustained search under its full prompt. S035 heartbeat disabled.9<=chi2<=12.

'''
    for p in ['AGENTS.md','authoritative/START_HERE.md','docs/SESSION_PROTOCOL.md']:
        write(p,header+(ROOT/p).read_text(encoding='utf-8'))
    append('sessions/S035/INPUT.md','Owner23Oct: investigate pause, close S035, commit/push and install S036 prompt to repair/diagnose then start a long search on its next invocation; no restart in closeout.')
    append('sessions/S035/RESEARCH.md',close)
    append('sessions/S035/ADVERSARIAL.md','Final closeout: native activity/conflict counts are not coverage. PermissionError sharing attribution is plausible, not proved. Original proof receipts were integrity-rechecked, not freshly replayed. Full journal counts overlap historical prefixes. RAM retention is not a durable crash snapshot. No SAT, graph/stratum decision or headline advance. No cold region was silently promoted.')
    append('docs/SESSION_LEDGER.md','| S035 |2026-10-23| CAM0040 owner closeout |247 encoded closures; nine UNKNOWN; watcher read failure; RAM preserved; lossless delta recovery | S036 targeted sustained search FUTURE/UNEXECUTED |')
    append('docs/FAILURE_LEDGER.md','S035 final failure: SAT scanner PermissionError opening RESUME_CONTROL/ADOPTION.json at08:43:46Z; WATCHER_FAILURE triggered non-forcing preservation. Generic controller label masked cause. Fix bounded stat/open/hash sharing retries and scan-cache commit-after-read; test SAT/retry and exhausted failures before S036 sustained launch. Creator/locking actor not established.')
    append('docs/DECISION_LOG.md','D075 (owner23Oct2026): investigate and close S035; preserve evidence and suspended RAM; ordinary existing-main push; install complete S036 targeted diagnostic/repair then long-search prompt. No S036 execution until next invocation; D074 same-main workflow continues.')
    append('docs/PHASE_GATE_LEDGER.md','S035 COMPLETED_OWNER_STOP_UNKNOWN:247 encoded closures/nine UNKNOWN; internal audit CLM-0121, Phase1 NOT PASSED;9..12 unchanged. S036 FUTURE/UNEXECUTED; publication/outreach/Lean unchanged.')
    write('campaigns/CAM-0040.md','# CAM-0040 — S035 COMPLETED_OWNER_STOP_UNKNOWN\n\n'+close)
    append('campaigns/README.md','CAM-0040 / S035 CLOSED23Oct2026:247 encoded proof closures/nine UNKNOWN; SAT-watcher read failure, original RAM contexts preserved suspended. S036 targeted repair/diagnostic long-search prompt queued, not executed.')
    claims=read('catalogue/CLAIMS.json')
    claim=dict(id='CLM-0121',status='COMPUTED_EXACT',sources=['SRC-0055'],claim='S035 final finite audit reconstructs247 encoded formula hashes and checks original independently verified proof/checker receipts; nine regions remain UNKNOWN.',
        notes='validation/S035/closeout/AUDIT.json and PREFIX_AUDIT.json. Accepted and retained geometric journal occurrences independently subdivision-audited; overlapping prefixes are not new unique clauses. No fresh final DRAT replay, individual graph exclusion, whole-stratum decision, SAT witness or headline advance. Source attribution method only;9<=chi2<=12. Lossless delta actual restore verified; private CDCL RAM is not serialized.')
    assert not any(c['id']==claim['id'] for c in claims);claims.append(claim);js('catalogue/CLAIMS.json',claims)
    append('catalogue/CLAIMS.md','## CLM-0121 — COMPUTED_EXACT\n\n'+claim['claim']+'\n\n'+claim['notes'])
    # Historical validators retain their complete old assertions against a pinned
    # entry-state snapshot; current closeout is checked separately.
    for p in ['scripts/check_s035_records.py','scripts/check_s035_resident_records.py','scripts/check_s035_resume_records.py']:
        freeze(p);s=(ROOT/p).read_text(encoding='utf-8')
        needle="state=read('authoritative/STATE.json')" if "state=read('authoritative/STATE.json')" in s else "state = read('authoritative/STATE.json')"
        s=s.replace(needle,needle+"\nif state['last_completed_session']=='S035':\n    state=read('validation/S035/closeout/ENTRY_STATE.json')")
        if p.endswith('check_s035_resume_records.py'):
            s=s.replace("assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S035'/mirror).read_bytes()", "if read('authoritative/STATE.json')['last_completed_session']!='S035':\n    assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S035'/mirror).read_bytes()")
        if p.endswith('check_s035_records.py'):
            s=s.replace("p=resolve(ROOT/name);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name", "p=resolve(ROOT/name)\n    if sha(p)!=row['sha256']:p=ROOT/'validation/S035/thread-repair/frozen-source'/(row['sha256']+'.bytes')\n    assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name")
        write(p,s)
    p='scripts/check_s035_thread_records.py';freeze(p);s=(ROOT/p).read_text(encoding='utf-8')
    s=s.replace("p=ROOT/name;assert p.stat().st_size ==", "p=ROOT/name;assert p.stat().st_size ==") # keep historical schema
    s=s.replace("p=ROOT/name;assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name", "p=ROOT/name\n if sha(p)!=row['sha256']:p=ROOT/'validation/S035/thread-repair/frozen-source'/(row['sha256']+'.bytes')\n assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name")
    write(p,s)
    print('Recorded S035 closeout and complete paired S036 prompt; S036 not executed')

if __name__=='__main__':main()
