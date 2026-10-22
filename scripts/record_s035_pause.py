"""Record owner-directed S035 pause; no closeout, process action or launch."""
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s035_windows import atomic_json,read_json
from s035_regions import sha
OUT=ROOT/'validation/S035/pause';SESSION=ROOT/'sessions/S035'

PROMPT='''# S035 â€” SAT-first resumption and nine-region diagnostic (OWNER INVOCATION REQUIRED)

This prompt resumes S035 only when the owner explicitly supplies it for execution.
S035 is PAUSED, not completed. S036 and all later sessions are not authorised.
Use this existing repository/main; no new project, branch, PR or force push.

1. Read AGENTS.md, authoritative/STATE.json, sessions/S035/PAUSE.md,
   NINE_REGION_DIAGNOSTIC.md, RESIDENT_UPGRADE_PLAN.md and validation/S035/pause/.
   Reconcile remote main, actual hosted jobs and local edits. Do not automatically
   launch or recover a guardian. The prior guardian/controller JSON says RUNNING
   because it is frozen: OWNER_PAUSE.json and authoritative PAUSED take priority.

2. SAT FIRST: inspect SAT_AUDIT.json and rescan all native logs, exit-code10
   results and candidate files. Run scripts/s035_sat_first_watch.py --once.
   Any SAT signal takes precedence over UNKNOWN, stop reasons and ordinary
   progress. Preserve the complete assignment, exact input/recipe, logs, sources
   and hashes; suspend the campaign immediately and independently validate CNF,
   both planar layers, disjoint union, alpha<=3, order28, degree/edge domain and
   a proper colouring. Report a potentially valid witness prominently. Difficulty
   alone implies neither SAT nor UNSAT. Do not promote before full domain review.

3. Use scripts/s035_pause_status.py. Twelve original processes were suspended,
   not killed; four native contexts retain RAM CDCL only while their PID/create
   identities survive. STOP remains latched. NEVER blindly remove STOP, resume
   the old guardian or call legacy recover: legacy STOP/recover uses taskkill /F.
   The native has no cooperative exit handler. Resolve this lifecycle blocker and
   validate a non-forcing pause/exit path on small controls before heavy work.
   A same-process RAM resume also requires explicit identity-aware handling of
   suspend counts, frozen wall deadlines and queued claims; no safe one-command
   RAM resume is currently supplied. Do not discard it to simplify recovery.

4. Durable semantic recovery: verify every runtime.tar.xz part and joined SHA,
   then python scripts/archive_s035_pause.py --verify. Use python scripts/restore_s035_pause.py --output C:\EM-S035-recovery
   to restore original objects and logical paths into a NEW directory. The
   script never launches a worker and verifies all restored hashes. Restore referenced
   S034 raw proof files with scripts/restore_s034.py --output <new-dir> --proofs
   from the committed, hash-verified validation/S034/campaign.tar.xz. Never
   overwrite live suspended work. Restore dependencies.tar.xz into a NEW root using DEPENDENCIES.json
   hashes for S032 base/seed, Windows checker and required runtime DLLs. Rebase only registered prefixes with hash checks.
   Restore gzip containers with pinned zlib1.3.1/level1; all original compressed
   and raw proof hashes were checked. The original pre-resident gzip container
   remains local; all its member bytes are independently stored in the pause
   archive. Operational live lock bytes are excluded and never copied to recovery.

5. Exact unresolved IDs: 0,1,3,7,15,31,63,127,255. All UNKNOWN; no pending UNSAT
   proofs or verification backlog at pause. RAM contexts: 0,7,127,255. Cold queue:
   1,3,15,31,63. Historical private_cdcl_retained flags on cold rows are stale;
   use the actual resident context map. Keep 247 independently proof-closed encoded
   regions. Standalone fresh DRAT plus independent checker gates every new closure.

6. Before any new heavy computation, commit/push diagnostic and SAT/lifecycle
   improvements and verify remote main. Run the SAT-first supervisor outside the
   guardian tree BEFORE future workers, preserving prominent SAT_ALERT.json even
   if validation fails. Test candidate interruption, validation failure and STOP
   races; do not rely solely on successful native return handling. Use targeted
   comparisons per region; avoid identical capped proof regeneration or blind
   restarts. Keep congruence disabled and random walk default unless a registered
   comparison justifies change. Four resident admissions including reservations,
   two executing slots, 600s fair turns; no repeated cache churn.

7. Retain 6GiB aggregate/2GiB per-worker private caps, 2GiB RAM floor,
   10GiB disk reserve, 2GiB raw-proof attempt cap and 40GiB campaign/64GiB S035
   budgets. Soft resident targets:5GiB/2.5GiB available RAM. Thermal unavailable.
   Respect fresh owner runtime instructions. Keep all checkpoints and evidence.
   S11 remains UNKNOWN;9<=chi2<=12. Encoded region closures are not graph or whole
   stratum exclusions. Preserve parked/publication/outreach/Lean gates.
'''

def main():
    OUT.mkdir(exist_ok=True)
    for name in ('RUNNING_MANIFEST.json','RUNNING.md','RESEARCH.md','ADVERSARIAL.md'):
        dest=OUT/('BEFORE_PAUSE_'+name)
        if not dest.exists():shutil.copy2(SESSION/name,dest)
    for name in ('OWNER_PAUSE.json','REGIONS.json','RESIDENT_CONTEXTS.json','GUARDIAN.json','CONTROLLER.json','CONFIG.json'):
        shutil.copy2(ROOT/'artifacts/tmp/S035/campaign'/name,OUT/name)
    (SESSION/'RESUME_PROMPT.md').write_text(PROMPT,encoding='utf-8',newline='\n')
    (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').write_text(PROMPT,encoding='utf-8',newline='\n')
    pause='''# S035 OWNER PAUSED â€” preservation and SAT priority

Owner stopped computation on22 October2026. All12 campaign processes are
identity-verified SUSPENDED with zero measured CPU; they have NOT exited. STOP
is latched and the heartbeat is PAUSED. No heavy work restarted. This is an
S035 pause and handover, not session completion or an S036 invocation.

The legacy STOP/checkpoint path calls taskkill /F and the native binary has no
cooperative exit handler. Obeying the owner's no-force instruction required
non-destructive OS suspension before STOP. The four native RAM contexts retain
CDCL/activities/search state; that state is NOT serialized and is lost if those
processes terminate or the laptop reboots. Durable geometric rules, formulas,
proofs and checkpoints remain recoverable. No original evidence was deleted.

Read-only current status: `.venv/Scripts/python.exe scripts/s035_pause_status.py`.
Frozen GUARDIAN/CONTROLLER RUNNING fields and active claims are historical, not
permission to compute. Do not resume them, remove STOP or run legacy recover.
Lifecycle repair and its controls are the first operational restart blocker.

No scientific SAT/candidate was found in the scientific log/exit-code audit.
All nine unresolved IDs are0,1,3,7,15,31,63,127,255; no pending UNSAT proof or
checker backlog.247 encoded regions remain independently proof-closed.
See NINE_REGION_DIAGNOSTIC.md and validation/S035/pause/SAT_AUDIT.json.

Future SAT-first external supervisor: scripts/s035_sat_first_watch.py. It never
launches workers; on a SAT marker, exit10 or candidate, it preserves a prominent
SAT_ALERT, suspends the guardian tree, latches STOP and attempts independent
candidate validation. A validation failure stays a SAT review alert, never an
ordinary UNKNOWN. Its small marker/race regression passes; real interruption
and lifecycle acceptance are explicitly required before future heavy work.

Recovery inventory/archive/verification: validation/S035/pause/. The archive
preserves every selected original file byte via content-addressed objects,
exact gzip reconstruction and hash-pinned committed S034 proof references.
Original pre-upgrade container remains local; every member is separately archived.
Live advisory lock bytes are excluded (not scientific evidence). Keep original
launch, pre-upgrade byte-verification and resident pilot records unchanged.
The full restart instructions are in RESUME_PROMPT.md, identical to the active
authoritative prompt.9<=chi2<=12; S11 UNKNOWN; all publication/Lean gates remain.
'''
    (SESSION/'PAUSE.md').write_text(pause,encoding='utf-8',newline='\n')
    nine=read_json(OUT/'NINE_REGIONS.json')['regions']
    text='# Nine unresolved regions at owner pause\n\nAll are UNKNOWN search regions; none has a pending UNSAT proof or checker backlog.\nCounters are the final retained process value, or the largest observed historical value for cold regions. They are not comparable solve-speed measures.\n\n| ID | Paused state | Conflicts | Decisions | Propagations | Proof attempts |\n|---:|---|---:|---:|---:|---:|\n'
    for r in nine:
        c=r['current_counters'] or r['largest_recorded_conflicts'] or dict(conflicts=0,decisions=0,propagations=0)
        text+=f'| {r["id"]} | {r["pause_state"]} | {c["conflicts"]} | {c["decisions"]} | {c["propagations"]} | {r["proof_attempts"]} |\n'
    text+='''
The former flat counters were congruence inprocessing, not evidence of a
mathematical barrier. Equal90s comparison:4216 versus1003623 conflicts with
congruence disabled; both UNKNOWN. Cold restarts lost private CDCL; the resident
V1 pilot also evicted contexts under memory pressure. V2 retained four identities
through repeated turns without eviction/restart churn. Their increasing conflict,
decision and propagation counters demonstrate active search, not eventual success.
The remaining bottleneck is algorithmic search; a mathematical explanation is
unknown. No resource cap or proof verification backlog explains the current nine.

For0,7,127,255 preserve RAM identities before any recovery; compare phase time,
conflict rates per active CPU second and new geometric cuts on equal inputs.
For1,3,15,31,63 restore semantic state only when capacity opens; current V2 did
not execute those cold regions. Their smaller historical counters do not show a
current stall. Test region-specific branching/inprocessing changes under a
registered comparison. Do not infer SAT from difficulty or closure from solver
UNSAT alone. Make cooperative stop and SAT-first handling mandatory first.

Historical stale retained flags on cold rows are recorded in NINE_REGIONS.json.
The old records are preserved; actual context membership determines RAM retention.
'''
    (SESSION/'NINE_REGION_DIAGNOSTIC.md').write_text(text,encoding='utf-8',newline='\n')
    state=read_json(ROOT/'authoritative/STATE.json');state['active_session'].update(status='PAUSED',workers=0,processes_exited=False,all_processes_suspended=True,runtime_status_authority='artifacts/tmp/S035/campaign/OWNER_PAUSE.json',running_handoff='sessions/S035/PAUSE.md',owner_resume_required=True,maintenance=False)
    state['next_session_priority']='S035 owner-paused: SAT-first audit, cooperative lifecycle repair and nine-region diagnosis before any owner-authorised resume. No S036.'
    state['s035_owner_pause']=dict(status='PAUSED',proof_closed_regions=247,unresolved_ids=[r['id'] for r in nine],ram_regions=[0,7,127,255],cold_regions=[1,3,15,31,63],SAT_audit='NO_SCIENTIFIC_SAT_OR_CANDIDATE_FOUND',durable_CDCL_snapshot=False,heartbeat='PAUSED',recovery='validation/S035/pause/RUNTIME_INVENTORY.json')
    atomic_json(ROOT/'authoritative/STATE.json',state)
    header='# S035 OWNER PAUSED (22 October2026)\n\nPreservation/SAT-first owner directive supersedes running instructions below.\nAll campaign processes are SUSPENDED, STOP latched; no heavy computation or\nS036 is authorised. Use scripts/s035_pause_status.py and sessions/S035/PAUSE.md.\nDo not call legacy recover/STOP or blindly resume guardian: those paths force\nterminate processes. RAM learning survives only in the suspended identities.\nRead the identical authoritative/S035 RESUME prompt before future work.\n\n'
    for name in ('AGENTS.md','authoritative/START_HERE.md','sessions/S035/RUNNING.md'):
        p=ROOT/name;t=p.read_text(encoding='utf-8')
        if not t.startswith('# S035 OWNER PAUSED'):p.write_text(header+t,encoding='utf-8',newline='\n')
    for name,line in {
        'docs/DECISION_LOG.md':'S035 owner pause: preservation first; no forced termination; SAT discoveries absolute priority; nine-region diagnostics and verified main publication before any further heavy computation. S036 not invoked.',
        'docs/FAILURE_LEDGER.md':'S035 lifecycle blocker: legacy STOP/recover taskkill /F and no native cooperative exit; non-destructive suspension used. RAM CDCL cannot be serialized. Cold private_cdcl_retained flags stale; actual context map authoritative. No SAT/proof promotion.',
        'docs/PHASE_GATE_LEDGER.md':'S035 PAUSED:247 encoded DRAT closures, nine UNKNOWN; SAT-first/lifecycle acceptance required before resume;9..12 and all separate gates unchanged.',
        'docs/SESSION_LEDGER.md':'S035 PAUSED by owner:12 processes suspended, four RAM contexts retained, nine UNKNOWN; durable archive/recovery; no new search, no S036.',
        'campaigns/README.md':'CAM-0040 / S035 OWNER_PAUSED:247 encoded proof closures; unresolved0,1,3,7,15,31,63,127,255. SAT-first/lifecycle diagnostic handover; no auto-resume.',
        'sessions/S035/RESEARCH.md':'Owner pause2026-10-22: no overlooked scientific SAT in recorded scientific logs; all nine remain native search UNKNOWN, no pending proofs. See pause audit and per-region diagnostic. No new graph/stratum/headline claim.',
        'sessions/S035/ADVERSARIAL.md':'Owner preservation audit: OS suspension preserves RAM but is not process exit or durable CDCL. Legacy STOP force-kills; cooperative lifecycle blocked. SAT exit10 can otherwise be hidden by a stop reason; prospective external supervisor preserves a prominent alert before independent validation. No heavy resumption.'
    }.items():
        p=ROOT/name;t=p.read_text(encoding='utf-8')
        if line not in t:p.write_text(t+'\n'+line+'\n',encoding='utf-8',newline='\n')
    print('Recorded PAUSED authority and identical S035 resumption prompts; no computation launched')

if __name__=='__main__':main()
