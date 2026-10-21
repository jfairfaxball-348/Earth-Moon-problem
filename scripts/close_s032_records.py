"""Package owner-stopped S032 and progress rebuild; never run a search or Git mutation."""
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

ROOT=Path(__file__).resolve().parents[1]
ENTRY='e3145c77a7350ebd2c8aa3197cf97bf5e626099f'
AREA=ROOT/'artifacts/tmp/S032'
DEST=ROOT/'validation/S032'
SESSION=ROOT/'sessions/S032'


def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(s,encoding='utf-8',newline='\n')


def dump(p,d):write(p,json.dumps(d,indent=2)+'\n')


def append(p,s):write(p,p.read_text(encoding='utf-8').rstrip()+'\n\n'+s.strip()+'\n')


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


PROMPT='''# S033 — owner-controlled, measurable S11 continuation (FUTURE / UNEXECUTED)

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

This is a handoff, not authorisation to run. D070 stopped S032 at the owner's
request. S033 requires a fresh owner invocation under D047; stop before S034.
Do not automatically resume S032 or revive its paused monitor. Preserve D042
lower-only scope and all parked/publication/outreach/registration/Lean gates.

Read live remote main, parents/tree, actual hosted jobs, open PRs/branches,
AGENTS, STATE, START_HERE, SESSION_PROTOCOL, D068/D069/D070 and all S032 records.
Reconcile live authority before writes. WIP history is backup only, never merge
or inherit it. Record executor. Verify actual processes and locks before launch.

S032 stopped2026-10-21T06:55:03Z after88133.828s wall time including an8h34m
battery-sleep interval. About15.9 CPU hours were observed before stop. No full
model was reported, no witness or stratum proof. S11 delta11/m155..156 UNKNOWN;
regular154 SOURCE_STATED with only three finite RUP branches replayed, hand
coverage not independently proved. S10/S9 NOT_RUN; delta>=9 conditional on
SRC-0037 and unconditional S8 still NOT_RUN. Classical9<=chi2<=12 unchanged.

Retained2579937 complete geometric clauses:162536 diagnostic seeds plus
2417401 campaign additions,189309949 bytes, zero incomplete tail. Uncompressed
SHA2566e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177.
All were independently checked by subdivision suppression; all336030 original
base clauses retained by checked bijective renaming of17976 variables. Read
validation/S032/stopped/CAMPAIGN_AUDIT.json and PRESERVATION.json, plus
validation/S032/SUMMARY.json and PACKAGE.json, sessions/S032/START_MANIFEST.json
and MANIFEST.json. Lossless rules are
validation/S032/stopped/learned.lem.gz. Original inputs/source/runtime/controls
are in validation/S032/start. Extract to the registered layout and verify hashes
before any reuse. No private CDCL state survives; do not promise seamless restart.

Owner wants useful progress information, not indefinite running on activity
alone. Read sessions/S032/PROGRESS_TOOLS.md. The native successor has30s/final
conflicts, decisions and propagations telemetry, alongside geometric counters;
scripts/build_s032_progress_native.py reproduces it separately. Rebuilt native
hash11f9edd801c33387a77dd71d539873985109d05d3e381dcdb49f3076a18c9740.
Small controls1024 exhaustive n5/fixed K33/positive24 pass;2s free K9 remained
UNKNOWN. No native full-K9 decision was achieved; do not conceal this limitation.

scripts/s032_coverage.py report is read-only with respect to search. The saved
ledger partitions8 free graph-presence variables into256 disjoint regions with
exact binomial weights after graph unit pins and m155/156. One cell128 has
standalone checked UNSAT both with and without campaign clauses: baseline
encoder/symmetry closure, not a new nonbiplanar-graph result or measured gain
from new rules. Weight0.9685672240percent of that encoded denominator; other
regions unresolved. A first15s augmented proof-check cap remains UNKNOWN,
the later60s solve/check succeeded. All attempts and proof bytes are archived.

A geometric clause forbids simultaneous edge presence in ONE layer. To count
graphs excluded solely by all clauses, graph edges must be counted once with
existential layer/auxiliary assignments: projected counting, not summing rule
counts. Do not advertise the raw1.33e110 labelled-edge-set count, internal
counters or region percentage as percent-to-solution or an ETA. High closed
weight can coexist with a very hard final region. State what is counted.

Before any resumed science, establish a NEW full271 CNF/proof smoke plus
retained/fresh K9 in the executing environment. A FAIL blocks science. Rebuild
and validate pins, region exports, telemetry, independent clause checks and
full-domain bijection. Run new small/backtracking/positive controls and preserve
failures. Do not rely on raw solver UNSAT or reuse old smoke as a fresh gate.

Agree a practical bounded CPU/wall/resource budget before a new long campaign;
D069's no-wall-limit permission ended at the owner's D070 stop. One heavy tree,
one CPU worker<=11GiB aggregate private memory,10GiB disk reserve, durable rules,
external supervision and an owner-stop path. No duplicate solver. Explain laptop
power/awake requirements and that checkpoints retain rules but not private CDCL
state. Configure a monitor only for a newly authorised run, quiet unless useful.

Prefer serial disjoint-region work if it yields meaningful certified closures.
`s032_coverage.py export --cell N` creates input but runs nothing; native region
work must be supervised. A stopped region's fresh geometric rules can be checked
and included by `check --cell N --extra-lemmas PATH --seconds SECONDS` for
standalone DRAT replay/check. Each phase is bounded and caps remain UNKNOWN.
Keep clause/mapping/source/proof provenance and do not count SAT relaxations
as planar graphs or closed regions. Native SAT triggers independent full
assignment, labelled disjoint layers, embeddings, alpha/proper-colouring and
counting checks before any chi>=10 claim. Native UNSAT requires checked proof
plus independent exact domain/encoding review before a whole-stratum result.

D044 Actions fallback remains available: ubuntu-24.04, SAME-JOB pinned setup
via scripts/cloud_setup.sh then full scripts/cloud_smoke.py before science;
record actual workflow/run/job/artifact/source/environment/proof hashes. Read
docs/CLOUD_ENVIRONMENT.md and validation/S011/SUMMARY.json for tested runs
38623187997/38623722547/38624616691 and preservation38625149681. Save permanent
evidence; an expiring ZIP or scaffold job is not a mathematical certificate.

Refresh prior art honestly if needed; S029 baseline stays frozen, source-stated
regular154/conditional-delta boundaries and parked T3/C5/old queues unchanged.
No novelty, formalisation, publication or external correspondence is authorised.

Close exactly S033 with truthful records, paired catalogues, all ledgers,
permanent evidence/hashes and byte-identical COMPLETE S034 future prompts.
One atomic authored commit from reconciled live entry main, ordinary PR,
non-force two-parent merge and actual head/main hosted-job verification. Output
verified commit/PR/merge links and the FULL future prompt. Disable its monitor
at closeout and stop; do not execute S034.
'''


def main():
    c=json.loads((AREA/'campaign/CONTROLLER.json').read_text())
    a=json.loads((AREA/'CAMPAIGN_AUDIT.json').read_text())
    cp=json.loads((AREA/'campaign/CHECKPOINT.json').read_text())
    controls=json.loads((AREA/'progress-controls-final/RESULT.json').read_text())
    assert c['worker_result']['stop_reason']=='OWNER_STOP' and not (AREA/'ACTIVE.lock').exists()
    assert a['status']=='PASS' and a['independently_checked_native_clauses']==2579937
    assert controls['status']=='PASS'
    rebuild=DEST/'rebuild';rebuild.mkdir(exist_ok=True)
    for name in ['RESULT.json']:
        shutil.copy2(AREA/'progress-controls-final'/name,rebuild/'CONTROLS.json')
    for directory in ['native-progress','progress-controls-final','coverage','coverage-base']:
        target=rebuild/(directory+'.tar.gz')
        with tarfile.open(target,'w:gz',compresslevel=6) as archive:
            for p in sorted((AREA/directory).rglob('*')):
                if p.is_file() and p.suffix not in ['.o','.rsp']:
                    archive.add(p,arcname=p.relative_to(ROOT).as_posix(),recursive=False)
        assert target.stat().st_size<95*1024**2,target
    for directory in ['coverage','coverage-base']:
        for name in ['coverage.json','REPORT.json']:
            shutil.copy2(AREA/directory/name,rebuild/(directory+'-'+name))
    summary=dict(session='S032',status='COMPLETED_OWNER_STOP_UNKNOWN',executor='Codex desktop local Windows',
        entry_main=ENTRY,started_utc=c['started_utc'],finished_utc=c['finished_utc'],
        wall_seconds=c['worker_result']['seconds'],sleep_gap_seconds=30853.814352035522,
        observed_native_cpu_seconds_before_stop=57120.4375,
        peak_private_kib=c['worker_result']['peak_aggregate_private_kib'],
        retained_geometric_rules=2579937,diagnostic_seed_rules=162536,campaign_new_rules=2417401,
        lemma_bytes=cp['complete_lemma_bytes'],lemma_sha256=cp['lemma_sha256'],
        partial_checks_last_observed=14653878,complete_model_checks_last_observed=0,
        native_cdcl_state_saved=False,independent_rule_and_renaming_audit='PASS',
        S11_m155_156='UNKNOWN',S11_m154_regular='SOURCE_STATED_NOT_PROGRAMME_DECIDED',
        S10='NOT_RUN',S9='NOT_RUN',S8_unconditional_fallback='NOT_RUN',
        witness=None,certified_strata=[],range={'lower':9,'upper':12},
        monitor_status='PAUSED',all_campaign_processes_stopped=True,no_automatic_resume=True,
        rebuilt_native_sha256=controls['native_sha256'],progress_controls='PASS',
        free_K9_native='UNKNOWN_AT_2S_IN_REBUILD; HISTORICAL60S/300S_UNKNOWN',
        exact_projected_excluded_graph_count='NOT_COMPUTED',
        coverage_demo='cell128 checked UNSAT both base-only and augmented; baseline encoder closure, not a new graph result',
        next_session='S033_FUTURE_UNEXECUTED')
    dump(DEST/'SUMMARY.json',summary)
    body='''# S032 closeout — safely stopped; rules preserved; progress tools rebuilt

Owner stopped the long campaign under D070 on2026-10-21. Registered STOP
produced OWNER_STOP, the native/controller exited, lock cleared and sleep
inhibition released. Monitor PAUSED. No long search has been restarted.

Retained2579937 complete geometric rules (162536 diagnostic seeds plus2417401
campaign additions),189309949 bytes, zero partial tail. Full independent
subdivision audit and exact336030-clause/17976-variable input renaming passed.
Uncompressed SHA2566e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177.
The190MB plain file and lossless archive are verified; compressed bytes, exact
source/runtime/input and controls are permanently archived. Private CDCL state
was lost at stop, as disclosed; semantic geometric knowledge is preserved.

Wall duration88133.828s includes8h34m battery sleep; about15.9 CPU hours were
observed before stop. Last native counters14653878 partial checks, zero complete
models. Peak aggregate private2774176KiB, below11GiB. S11 UNKNOWN; no witness,
stratum proof or lower-bound advance. Regular154 source-stated; S10/S9/S8
NOT_RUN and conditional-delta/parked/publication/formalisation gates unchanged.

Built a separate native successor with periodic/final conflicts, decisions and
propagations telemetry. Rebuilt1024 exhaustive n5/fixed K33/positive24 controls
passed.2s free K9 remained UNKNOWN; neither earlier60s/300s caps nor this stress
test certify K9. New disjoint-region accounting has exact combinatorial weights
and requires standalone checked DRAT to close a region. Tiny controls test SAT
remaining unresolved, damaged-proof rejection and exact weights. Exported real
cell128 payload byte-matches its independently refuted formula.

Real cell128 is checked UNSAT both WITHOUT and WITH retained campaign clauses.
It closes0.9685672240percent of the stated unit-pinned encoded denominator,
already implied by baseline encoder/symmetry constraints. This is NOT a new
nonbiplanar graph exclusion, a measured benefit from new rules, a witness, or
percent-to-solution. Its first augmented15s checker cap remains UNKNOWN;
later60s replay/check succeeded. All proof/cap bytes are archived. Other255
regions unresolved; no exact count of graphs excluded solely by learned layer
rules was computed. That would require projected counting over graph edges with
existential layer/auxiliary assignments, not addition of rule effects.

Read PROGRESS_TOOLS.md for CLI commands and limitations. `report` starts no
solver; `check` explicitly starts bounded standalone proof work only; `export`
writes future region input only. No successor search or S033 was executed.
Historical RUNNING/PLAN/launch snapshots retain original wording/provenance;
D070 supersedes D069 continuation. S033 future prompt requires fresh invocation
and a practical budget, fresh smoke and domain/resource/proof gates.

One atomic authored session commit from entrymain e3145c77a7350ebd2c8aa3197cf97bf5e626099f;
WIP backup history is never inherited. Ordinary PR/non-force two-parent merge
and actual head/main hosted jobs are verified after commit. Job identities are
reported live because a commit cannot pin its own final hash. Scaffold checks
test integrity/governance, not mathematical soundness or search exhaustion.
'''
    write(SESSION/'CLOSEOUT.md',body)
    append(SESSION/'RESEARCH.md',body)
    append(SESSION/'ADVERSARIAL.md','D070 closeout: all2579937 retained clauses independently checked. No full model/stratum proof. Geometric clauses are layer predicates, not direct graph exclusions. Cell128 baseline/augmented proofs concern an encoded symmetry region only. Exact projected count and ETA remain unknown. All original/native/full-K9 limitations preserved; no automatic restart.')
    append(SESSION/'PRIOR_ART.md','D070 stop/rebuild used pinned already-inspected implementation; no further landscape or novelty claim. SRC0055 attribution retained; S029 freeze and prior dated access grades unchanged.')
    write(SESSION/'S033_FUTURE_PROMPT.md',PROMPT)
    write(ROOT/'authoritative/NEXT_SESSION_PROMPT.md',PROMPT)
    state=json.loads((ROOT/'authoritative/STATE.json').read_text())
    state['last_completed_session']='S032';state['recommended_next_session']='S033'
    state['next_session_is_future_unexecuted']=True
    state['s032_completed_runtime']=state.pop('active_session')
    state['s032_completed_runtime']['status']='COMPLETED_OWNER_STOP_UNKNOWN'
    state['s032_completed_runtime']['finished_utc']=c['finished_utc']
    state['s032_science']=summary
    state['standing_continuation_authorization']['status']='ENDED_D070_OWNER_STOP_NO_AUTOMATIC_RESUME'
    state['headline_status']='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S032'
    state['latest_session_branch']='codex/S032-partial-planarity';state['latest_session_entry_main']=ENTRY
    state['latest_session_integration']={'status':'S032_IDENTITIES_TO_BE_VERIFIED_LIVE_AFTER_COMMIT','entry_main':ENTRY}
    state['open_obligations']=['S033 FUTURE/UNEXECUTED; no automatic S032 resume. Exact projected count/ETA not computed; use bounded proof-backed region accounting if owner invokes.',
        'S11 m155/156 UNKNOWN; regular154 SOURCE_STATED, finite RUP branches only.',
        'S10/S9 NOT_RUN; delta>=9 conditional on SRC0037; unconditional S8 NOT_RUN.',
        'All parked queues and publication/outreach/formalisation gates unchanged;9<=chi2<=12.']
    dump(ROOT/'authoritative/STATE.json',state)
    claim={'id':'CLM-0119','status':'COMPUTED_EXACT','sources':['SRC-0055'],
        'claim':'All2579937 persisted S032 geometric clauses independently satisfy the single-layer K5/K33-subdivision check; original336030 clauses/17976 variables retained by independently checked bijective renaming.',
        'notes':'Owner-stopped campaign UNKNOWN; no complete model, witness or whole-stratum proof. Lossless189309949-byte rule archive matches final SHA256. Rebuilt progress tools pass finite controls; encoded cell128 DRAT closure is baseline encoder/symmetry closure, not a new nonbiplanarity theorem or increment attributable to learned rules. Exact projected graph count and ETA not computed.'}
    claims=json.loads((ROOT/'catalogue/CLAIMS.json').read_text())
    assert not any(c['id']==claim['id'] for c in claims)
    claims.append(claim)
    for row in claims:
        if row['id']=='CLM-0118':row['notes']=row['notes'].replace('Unbounded-duration campaign is IN_PROGRESS under D069; this finite diagnostic claim does not report its eventual outcome.','The later campaign was owner-stopped under D070, UNKNOWN; see CLM0119 for the final finite audit.')
    dump(ROOT/'catalogue/CLAIMS.json',claims)
    md=ROOT/'catalogue/CLAIMS.md'
    write(md,md.read_text(encoding='utf-8').replace('Unbounded-duration campaign is IN_PROGRESS under D069; this finite diagnostic claim does not report its eventual outcome.','The later campaign was owner-stopped under D070, UNKNOWN; see CLM0119 for the final finite audit.'))
    append(md,'## CLM-0119 — COMPUTED_EXACT\n\n'+claim['claim']+'\n\n'+claim['notes']+' Source: SRC-0055 (method attribution); internal independent audit.')
    sources=json.loads((ROOT/'catalogue/SOURCES.json').read_text())
    for row in sources:
        if row['id']=='SRC-0055':row['note']+=' S032 D070: instrumented successor adds internal counters only; final2579937 layer-clause audit passes. No exact projected graph count or runtime prediction; scope remains implementation inspection, not a new mathematical source claim.'
    dump(ROOT/'catalogue/SOURCES.json',sources)
    append(ROOT/'catalogue/SOURCES.md','S032 D070 update to SRC-0055: instrumented successor adds CaDiCaL counters; final2579937 layer clauses independently audited. Existing access grade/attribution unchanged. No projected graph-count or runtime claim.')
    append(ROOT/'docs/DECISION_LOG.md','**D070 (owner,2026-10-21):** safely stop S032, retain rules and rebuild progress capability. Registered OWNER_STOP; all2579937 saved clauses independently checked and losslessly archived. Monitor PAUSED; no automatic restart. Separate native internal telemetry and proof-backed disjoint-region CLI built/tested. Exact projected count/ETA unknown. S032 closes UNKNOWN, S033 FUTURE/UNEXECUTED.')
    ledger=ROOT/'docs/SESSION_LEDGER.md'
    text=ledger.read_text(encoding='utf-8');text='\n'.join(line for line in text.splitlines() if not line.startswith('| S032 |'))+'\n'
    write(ledger,text)
    append(ledger,'| S032 | 2026-10-20/21 | D068 invocation, D069 no fixed wall, D070 owner stop/rebuild; local Codex, CAM0038 |2579937 geometric rules independently audited; no model/stratum/witness; S11 UNKNOWN; proof-backed region tooling and native telemetry rebuilt/tested;9<=chi2<=12 | Complete owner-stopped; S033 FUTURE, no automatic resume |')
    append(ROOT/'docs/PHASE_GATE_LEDGER.md','S032 (2026-10-21): owner-stopped UNKNOWN;2579937 independently checked layer rules. No witness, stratum or lower-bound advance. Region-accounting baseline closure is not a graph theorem; Phase1 gate NOT PASSED. All parked/publication/formalisation gates unchanged.')
    append(ROOT/'docs/FAILURE_LEDGER.md','| F086 (S032) | Partial-planarity learning will finish within practical laptop runtime | Owner stopped after88133.828s wall including8h34m battery sleep; about15.9 observed CPU hours, no complete model | Preserve2579937 rules; no ETA from counters; rebuild logical telemetry and proof-backed disjoint-region accounting; no automatic restart |\n\n| F087 (S032 progress demo) |15s suffices for augmented region DRAT checking | Solver UNSAT but checker capped; correctly UNKNOWN | Preserve failed attempt; later60s replay/check PASS; baseline-only proof closes same encoder region, so do not attribute this to new rules |')
    campaign=ROOT/'campaigns/CAM-0038.md'
    write(campaign,'# CAM-0038 — S032 OWNER_STOPPED_UNKNOWN (D070)\n\n'+body+'\n\nHistorical preregistration remains sessions/S032/PLAN.md; launch provenance in RUNNING.md.\n')
    append(ROOT/'campaigns/README.md','CAM-0038 S032: COMPLETED_OWNER_STOP_UNKNOWN;2579937 checked geometric clauses; rebuilt telemetry/region CLI; no automatic resume, S033 FUTURE.')
    for name in ['AGENTS.md','authoritative/START_HERE.md']:
        p=ROOT/name
        write(p,p.read_text(encoding='utf-8').replace('Rebuild/test and closeout only; no long search restart or S033 without fresh owner invocation.','S032 closeout complete; rebuilt progress tools tested. No long search restart or S033 without fresh owner invocation.'))
    files=[p for p in DEST.rglob('*') if p.is_file() and p.name!='PACKAGE.json']
    dump(DEST/'PACKAGE.json',{'files':{p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)}})
    manifest_files=[p for p in SESSION.rglob('*') if p.is_file() and p.name!='MANIFEST.json']
    manifest_files += [p for p in (ROOT/'scripts').glob('*s032*.py')]
    manifest_files += [ROOT/'tools/s032_subdivision.hpp',ROOT/'docs/D070_S032_OWNER_STOP_AND_PROGRESS_REBUILD.md']
    dump(SESSION/'MANIFEST.json',{'artifact_sha256':{p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(manifest_files)}})
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
