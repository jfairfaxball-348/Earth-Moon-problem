"""Package the completed S031 cap and truthful handoff; no search or Git writes."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'artifacts/tmp/S031'
DEST=ROOT/'validation/S031'
SESSION=ROOT/'sessions/S031'
ENTRY='dd802686215781cbc35aa86ea14c54369aaec7e5'


def write(p,text):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8',newline='\n')


def dump(p,data):write(p,json.dumps(data,indent=2)+'\n')


def append(p,text):write(p,p.read_text(encoding='utf-8').rstrip()+'\n\n'+text.strip()+'\n')


def hashes(paths):
    return {p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,
             'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)}


PROMPT='''# S032 — OP1(b): strengthen persistent S11 search (FUTURE / UNEXECUTED)

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

This is a handoff only. D066 ended authorization after S031; do not execute
S032 until the owner supplies this prompt, its link, or a fresh next-session
invocation (D047). That act invokes exactly S032; stop before S033. Preserve
D042 lower-only scope, the order-28 OP1(b) target, all parked queues and the
separate publication, outreach, registration and formalisation gates.

Target: an explicit simple biplanar graph on 28 vertices with alpha<=3, hence
chi>=10, or an independently checked exclusion of a complete stated stratum.
S031's persistent run capped after28692s,46 relaxation models,1809 checked cuts
(1114 inherited,695 new),205206574 conflicts and2073 budget slices. Both layers
of every saved model are nonplanar. S11 delta11/m155..156 remains UNKNOWN;
S10/S9/S8 NOT_RUN. Regular154 remains SOURCE_STATED: only three finite RUP
branches were replayed, not hand coverage. Delta>=9 depends on SRC-0037;
the unconditional delta>=8 boundary leaves S8 explicit. No chi>=10 witness;
classical9<=chi2<=12. These sampled models do not measure exhaustive coverage.

Independently reconcile live remote main SHA/tree/parents, actual PR/head/main
jobs, open PRs and competing branches. Read AGENTS, STATE, START_HERE, protocol,
D066, all S031 records, MANIFEST/START_MANIFEST, validation/S031/SUMMARY.json,
SEARCH_REPLAY.json and PACKAGE.json. Historical RUNNING.md and start/controller
snapshots are provenance, not current authority. S031's worker has stopped;
verify actual PIDs before any launch. Never duplicate an active heavy worker.
WIP snapshots are never merged or inherited into the session commit.

Record executor. Use the hooked cloud setup or owner-authorized local pinned
toolchain. Before science run a NEW full scripts/cloud_smoke.py: all271 archived
CNF/proof checks plus retained/fresh K9. A failure blocks science. One heavy
process tree<=11GiB aggregate private memory, external Windows wall/memory
supervision,10GiB disk reserve. Windows CaDiCaL has no usable -t switch.
Declare wall ceiling, workers/CPU/RAM, overnight suitability, laptop power and
awake requirements, checkpoints and wakeups before any long campaign. Prefer
one substantive multi-hour campaign with durable checks after hours. Do not
reuse S031's disabled monitor without configuring a newly authorized monitor.

Reproduction: with pinned python-sat1.9.dev15/networkx3.5 run
`.venv/Scripts/python.exe scripts/replay_s031_search.py validation/S031/search`
(Linux: .venv/bin/python). This checks all46 full assignments against their
chronological formula, all1809 cut semantics, variable maps and regenerated
336030-clause17976-variable final formula. Decompress archived JSON/CNF files
into a NEW session scratch directory; never edit S031 evidence. Revalidate
the semantic checkpoint. Private CDCL state is gone after the cap; a new
process restores only semantic cuts. Fresh solver/positive controls remain
required, including independent RUP checks and the24-vertex alpha3 split.
An actual17-vertex alpha2 control was not retrieved; J1 has alpha3.

Do not simply repeat an unchanged eight-hour cap. Diagnose the205M-conflict
bottleneck and preregister a materially stronger sound method: for example
incremental partial-assignment planarity propagation or a reviewed persistent
native external propagator, with proof-producing final-formula replay. Inspect
and attribute SRC-0055 bipsat2 before reuse; its twinning assumptions must not
restrict the full labelled domain. A different encoding or decomposition needs
a coverage proof, controls and independent semantic checks. Preserve CLM-0115
root/star/type relabelling, exact alpha-four-set, degree/edge/layer constraints,
and sound K9/triangle-free104/certified-library cuts. No sampled-model blockers,
unproved automorphism assumptions or family-only substitutes for the stratum.

Continue S11 first. Only a complete independently checked S11 decision permits
S10 then S9; keep unconditional S8 and regular154 dependencies explicit. Every
cut must be semantically checked and linked to exact variables/source inputs.
On incremental UNSAT save the full formula and obtain/check native DRAT with
pinned checker under separately declared serial caps. Bare UNSAT, interrupted
proofs and timeouts remain UNKNOWN. Any planar survivor stops all search for
independent labelled layers/embedding, alpha, proper colouring and chi>=10
counting validation.28/3 counting applies only after biplanarity is checked.

Refresh paper59, posts146/152/155 and arXiv2609.28102 against S031 dated receipts.
The S031 closeout article bodies were unchanged, paper59 v3/arXiv v1. Source
claims only prioritize until re-proved/replayed; no novelty guarantee or forum
contact. S029 frozen baseline stays intact. T3 orders21..27 and the old S029
obstruction/C5 queues remain PARKED.

D044 alternate runner: preregister a new never-merged WIP Actions job on
ubuntu-24.04; SAME-JOB `bash scripts/cloud_setup.sh`, full smoke, registered
science, upload/download exact sources/environment/proof artifacts. Tested
historical workflow/run/artifact details: docs/CLOUD_ENVIRONMENT.md and
validation/S011/SUMMARY.json (runs38623187997/38623722547/38624616691,
preservation38625149681). Expiring ZIPs cannot be sole permanent evidence.
Hosted Research scaffold checks validate governance, not mathematical claims.

Close exactly S032 with complete records, paired sources/claims and all
session/phase/decision/failure/campaign ledgers, permanent evidence/hashes,
truthful STATE and byte-identical COMPLETE S033 future prompts in authoritative/
NEXT_SESSION_PROMPT.md and sessions/S032/S033_FUTURE_PROMPT.md. One atomic
authored session commit from live entry main, ordinary PR, non-force two-parent
merge and independently verified main/tree/parents and actual hosted jobs.
Final report includes verified commit/PR/merge links, all stratum verdicts and
the FULL S033 prompt. Disable S032 monitoring at closeout; do not execute S033.
'''


def main():
    controller=json.loads((RUN/'CONTROLLER.json').read_text())
    result=json.loads((RUN/'search/RESULT.json').read_text())
    replay=json.loads((RUN/'SEARCH_REPLAY.json').read_text())
    assert controller['status']=='SEARCH_FINISHED_UNKNOWN_REVIEW_REQUIRED'
    assert controller['worker_process']['completed_process'] and controller['worker_process']['returncode']==0
    assert controller['sleep_inhibition_released'] and result['status']=='WALL_CAPPED'
    assert replay['status']=='PASS' and replay['models_checked']==46 and replay['cuts_checked']==1809
    for name,h in controller['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    # Preserve exact final bytes; large text objects are deterministic gzip.
    search=DEST/'search';search.mkdir(exist_ok=True)
    for p in (RUN/'search').iterdir():
        if p.is_dir():
            assert p.name=='models'
            shutil.copytree(p,search/p.name,dirs_exist_ok=True)
        elif p.stat().st_size>50000:
            (search/(p.name+'.gz')).write_bytes(gzip.compress(p.read_bytes(),mtime=0))
        else:shutil.copy2(p,search/p.name)
    for name in ['CONTROLLER.json','SEARCH_REPLAY.json']:
        shutil.copy2(RUN/name,DEST/name)
    for name in ['LONG_JOURNAL.jsonl','worker.log','controller.stdout.log','controller.stderr.log']:
        (DEST/(name+'.gz')).write_bytes(gzip.compress((RUN/name).read_bytes(),mtime=0))
    prior=DEST/'prior-art-closeout';prior.mkdir(exist_ok=True)
    for name in ['FETCH_RECEIPTS.json','ARTICLE_COMPARISON.json']:
        shutil.copy2(RUN/'prior-art-closeout'/name,prior/name)
    fetched=json.loads((prior/'FETCH_RECEIPTS.json').read_text())
    for row in fetched:
        row['access_grade']='ABSTRACT_INSPECTED' if 'arxiv.org' in row['url'] else ('METADATA_ONLY' if '/api/' in row['url'] else 'STATEMENT_INSPECTED')
    dump(prior/'FETCH_RECEIPTS.json',fetched)
    summary={'session':'S031','executor':'Codex desktop local Windows',
        'started_utc':result['started_utc'],'finished_utc':controller['finished_utc'],
        'status':'COMPLETED_WALL_CAPPED','search_seconds':result['seconds'],
        'external_worker_seconds':controller['worker_process']['seconds'],
        'startup_diagnostic_seconds':82.14,'sat_models':46,'seed_cuts':1114,'new_cuts':695,
        'cuts':1809,'conflicts':result['stats']['conflicts'],'budget_slices':2073,
        'peak_aggregate_private_kib':controller['worker_process']['peak_tree_rss_kib'],
        'memory_cap_kib':11534336,'sleep_inhibition_released':True,
        'S11_m155_156':'UNKNOWN','S11_m154_regular':'SOURCE_STATED_NOT_PROGRAMME_DECIDED',
        'S10':'NOT_RUN','S9':'NOT_RUN','S8_unconditional_fallback':'NOT_RUN',
        'witness':None,'certified_strata':[],'independent_replay':'PASS',
        'smoke':'PASS_FULL_271_PLUS_RETAINED_AND_FRESH_K9',
        'range':{'lower':9,'upper':12},'next_session':'S032_FUTURE_UNEXECUTED',
        'successive_sessions_authorized':False,'monitor':'DISABLE_AFTER_INTEGRATION_D066'}
    dump(DEST/'SUMMARY.json',summary)
    write(SESSION/'S032_FUTURE_PROMPT.md',PROMPT)
    write(ROOT/'authoritative/NEXT_SESSION_PROMPT.md',PROMPT)
    headline='46 relaxation models independently audited;28692s persistent search;1809 checked cuts (1114 inherited,695 new); S11 m155/156 UNKNOWN; S10/S9/S8 NOT_RUN; no certified stratum or chi>=10 witness;9<=chi2<=12.'
    closeout=f'''# S031 closeout — persistent eight-hour S11 campaign

{headline}

One unchanged live cadical300 instance ran from2026-10-19T18:44:38Z to
2026-10-20T02:42:50Z. External supervised duration28694.14s; exit0;
2073 budget slices,205206574 conflicts,515307191 decisions. Peak aggregate
private commit1284484KiB, below11GiB; disk remained above10GiB reserve.
Controller and worker exited and the temporary sleep inhibition was released.
The82.14s startup diagnostic is separately preserved; no model was found
there, and only semantic cuts, not its private CDCL state, were resumed.

Independent scripts/replay_s031_search.py validates all46 complete assignments
against their chronological formula, alpha-four-sets, degree/edge/layer counts,
root/star/type conditions, and every one of1809 cuts. Both layers of each saved
model have independently checked subdivisions to K5/K3,3. The final formula
regenerates exactly:17976 variables,336030 clauses. Cut totals1629 K9 and180
Kuratowski. All695 new cuts have model provenance. No sampled-model blockers.
No UNSAT occurred, so native DRAT replay was not triggered. No full graph
biplanarity verdict follows merely from a rejected saved layer assignment.

Fresh full271+K9 smoke and2916 persistent small-assignment/incremental controls
passed at entry;44 S030 models and all seed cuts were rechecked. Paper59 finite
RUP branches passed both checkers; hand coverage remains unproved here. The
actual17-vertex alpha2 calibration was not retrieved; positive24 alpha3 was
checked. No source-stated theorem or regular154 decision is promoted.

Two dated primary-source refreshes found unchanged paper59/post146/152/155
article text; closeout2026-10-20T02:47Z still reports paper59 v3 and arXiv v1.
S029 landscape stays frozen. CLM-0117 records only the exact finite replay.
Phase1 gate remains unpassed; all parked and publication/outreach/Lean gates
are unchanged. Persistent learning did not finish S11 within the cap; S032
should diagnose and strengthen the method before another unchanged long cap.

Permanent reproducible evidence: validation/S031 (launch snapshots, native/
extension/source hashes, final full formula/cuts/checkpoint/assignments and
supervisor journal). PACKAGE/MANIFEST hash the archived bytes. Compression is
lossless. Semantic cuts can resume; private learned clauses cannot be restored.

D066 authorizes ONLY S031. The full paired S032 prompt is FUTURE/UNEXECUTED.
No successor ran. Disable the heartbeat after integration and stop. One atomic
authored commit on codex/S031-persistent-op1b, sole parent {ENTRY}; WIP history
is not inherited. PR/merge/head/main job identities are verified live after
commit, because self-identities cannot be pinned within their own commit.
The final report supplies verified links and the entire future prompt.
'''
    write(SESSION/'CLOSEOUT.md',closeout)
    append(SESSION/'RESEARCH.md','## Completed campaign and independent audit\n\n'+headline+'\n\nSee CLOSEOUT.md and validation/S031/SEARCH_REPLAY.json for exact chronological model/cut/formula replay. No whole-stratum proof. Native final-formula replay was not triggered because the incremental solver never returned UNSAT.')
    append(SESSION/'ADVERSARIAL.md','## Final audit\n\nAll46 saved assignments and1809 cut semantics PASS, including two nonplanar layer subdivisions per model. The cap is UNKNOWN; it establishes neither absence of a graph nor a complete stratum. No private learned state survives process exit. D066 supersedes the historical D065 successor wording above: S032 remains FUTURE/UNEXECUTED and monitoring ends after integration.')
    append(SESSION/'INPUT.md','## Outcome\n\nThe registered worker finished at its wall ceiling; this session is now completed with UNKNOWN S11. CLOSEOUT and final evidence supersede the launch-only IN_PROGRESS descriptions above. D066 forbids successor execution.')
    old=(SESSION/'RUNNING.md').read_text(encoding='utf-8')
    write(SESSION/'RUNNING.md','# HISTORICAL RUNNING HANDOFF — S031 worker has finished\n\nFinal capped result and independent audit are in CLOSEOUT.md and validation/S031.\nDo not execute the historical resume command without a fresh authorized session.\nThe original running handoff follows as provenance.\n\n'+old)
    append(SESSION/'PRIOR_ART.md','## Closeout refresh — 2026-10-20T02:47 UTC\n\nAll six URLs returned HTTP200. Paper59 API still v3; all four rStation article bodies text-identical to entry (and hence inspected S030 text). ArXiv submission history still v1,2026-09-23. Exact response hashes and article-text comparisons are archived under validation/S031/prior-art-closeout. Access grades reflect article statements/abstract/metadata only; no additional full proof inspection or novelty claim. Existing source boundaries unchanged.')
    write(ROOT/'campaigns/CAM-0037.md','# CAM-0037 — S031 persistent S11 campaign (COMPLETED, UNKNOWN)\n\n'+headline+'\n\nPreregistration sessions/S031/PLAN.md; executed sources/native hashes and full fresh gate in validation/S031/start. One persistent cadical300 instance;28692s,2073 slices,205206574 conflicts; peak1284484KiB aggregate private. All46 models/1809 cuts independently audited. Both layers of every model nonplanar; no UNSAT or witness. Permanent semantic checkpoint, formula and full assignments archived. Native private learned state is not saved. D066 ends execution after S031; S032 requires fresh invocation.\n')
    p=ROOT/'campaigns/README.md';t=p.read_text(encoding='utf-8');t=t.replace('**CAM-0037 (S031, IN_PROGRESS)** persistent S11 long run; fresh full gate and\n  controls passed,8h cap/11GiB tree, two-hour scheduled checks. No new verdict.','**CAM-0037 (S031, COMPLETED UNKNOWN)** persistent28692s S11 run;46 models/1809 cuts independently audited; no certified stratum or witness. S032 FUTURE only (D066).');write(p,t)
    p=ROOT/'docs/SESSION_LEDGER.md';t=p.read_text(encoding='utf-8');t=t.replace('| S031 | 2026-10-19 | D065 standing authorization; CAM0037 persistent S11 worker; full smoke and controls PASS | IN_PROGRESS_LONG_RUN,8h ceiling,11GiB,2h scheduled checks; no certified stratum or witness | RUNNING; last completed remains S030 |',f'| S031 | 2026-10-19/20 | D065 launch, D066 S031 ONLY; local Codex; CAM0037 persistent worker | {headline} | Complete capped; S032 FUTURE/UNEXECUTED; stop |');write(p,t)
    append(ROOT/'docs/DECISION_LOG.md','**D067 (S031 closeout,2026-10-20):** '+headline+' D066 remains binding: disable monitor after integration and stop. Future S032 should first diagnose/strengthen the persistent method; no successor execution or scope change authorized.')
    append(ROOT/'docs/FAILURE_LEDGER.md','| F084 (S031) | Persistent incremental CDCL will finish S11 within eight hours |28692s,205206574 conflicts,46 relaxation models,695 added sound cuts; full stratum still UNKNOWN | Diagnose search/propagation bottleneck and validate a materially stronger method before repeating an unchanged cap; preserve semantic cuts and explicit loss of private CDCL state |\n\n| F085 (S031 startup) |2000-conflict/20000-decision slices suit long-run checkpointing |914 re-entries in82.14s, no model; diagnostic stopped gracefully | Preserved exact receipts/source; current campaign used100000/1000000 on one live instance, then completed its registered cap |')
    append(ROOT/'docs/PHASE_GATE_LEDGER.md','S031 (2026-10-20): '+headline+' Phase1 lower-bound gate NOT PASSED; no novelty/Lean/registration/publication/outreach advancement. D066 stops after S031.')
    banner='# D067 S031 completed (2026-10-20; eight-hour persistent S11 cap)\n\n'+headline+' Full fresh271+K9 smoke/controls PASS. D066 S031-only scope is discharged by closeout; S032 FUTURE/UNEXECUTED requires fresh invocation. Parked queues and all scientific/publication gates unchanged.\n\n'
    for name in ['AGENTS.md','authoritative/START_HERE.md','docs/SESSION_PROTOCOL.md']:
        p=ROOT/name;write(p,banner+p.read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'catalogue/SOURCES.json').read_text(encoding='utf-8'))
    for row in sources:
        if row['id'] in ['SRC-0037','SRC-0045','SRC-0048','SRC-0049','SRC-0050']:
            row['accessed']='2026-10-20'
            row['note']+=' S031 entry/closeout refresh: article text unchanged; paper59 v3/arXiv v1. See validation/S031/prior-art-closeout; no proof-status promotion.'
    dump(ROOT/'catalogue/SOURCES.json',sources)
    append(ROOT/'catalogue/SOURCES.md','S031 dated refresh (entry2026-10-19, closeout2026-10-20): SRC-0037/0045/0048/0049/0050 unchanged at article-text/abstract level; paper59 v3 and arXiv v1. Exact receipts/comparison: validation/S031/prior-art-closeout. Access grades and source-stated boundaries unchanged; no new external source or novelty claim.')
    claims=json.loads((ROOT/'catalogue/CLAIMS.json').read_text(encoding='utf-8'))
    claim={'id':'CLM-0117','status':'COMPUTED_EXACT','sources':[],
        'claim':'S031 finite replay checks46 saved S11 relaxation assignments chronologically,1809 sound semantic cuts and the exact regenerated17976-variable336030-clause final formula; both layers of each saved model have checked nonplanar subdivisions.',
        'notes':'validation/S031/SEARCH_REPLAY.json; scripts/replay_s031_search.py. This is a finite audit only:28692s WALL_CAPPED, S11 UNKNOWN, no certified stratum or biplanar witness.1629 K9/180 Kuratowski cuts total,1114 seeds/695 new. No complete graph biplanarity exclusion inferred from one rejected split.'}
    claims.append(claim);dump(ROOT/'catalogue/CLAIMS.json',claims)
    append(ROOT/'catalogue/CLAIMS.md','## CLM-0117 — COMPUTED_EXACT\n\n'+claim['claim']+'\n\n'+claim['notes']+' Sources: internal saved assignments and independently checked cut certificates; no external theorem promoted.')
    state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
    assert state['last_completed_session']=='S030'
    state['last_completed_session']='S031';state['recommended_next_session']='S032'
    state['as_of']='2026-10-20';state['next_session_is_future_unexecuted']=True
    state['headline_status']='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S031'
    state['source_status']='S029_FROZEN_PLUS_S031_DATED_REFRESH_NO_NOVELTY_CLAIM'
    state['latest_session_branch']='codex/S031-persistent-op1b';state['latest_session_entry_main']=ENTRY
    state['latest_session_integration']={'status':'S031_IDENTITIES_TO_BE_VERIFIED_LIVE_AFTER_COMMIT','entry_main':ENTRY}
    state['session_gate']='S031 completed capped UNKNOWN; D066 stop after closeout. S032 FUTURE/UNEXECUTED requires fresh owner invocation under D047.'
    state['next_session_priority']='S032 FUTURE: diagnose/strengthen persistent S11 method, revalidate saved semantic cuts; no unchanged automatic eight-hour rerun.'
    state['historical_open_obligations_before_S031']=state['open_obligations']
    state['open_obligations']=['S032 FUTURE/UNEXECUTED: stronger certified S11 method; S031 whole stratum UNKNOWN.']+state['open_obligations'][1:]
    state['s031_science']=summary
    state['s031_completed_runtime']=state.pop('active_session')
    state['s031_completed_runtime']['status']='COMPLETED_WALL_CAPPED_UNKNOWN'
    state['s031_completed_runtime']['finished_utc']=controller['finished_utc']
    state['standing_continuation_authorization']['status']='S031_EXECUTION_FINISHED_NO_SUCCESSOR_AUTHORIZATION'
    state['s030_integration_verified']={'pr':39,'authored_commit':'45bc0437d99deb6580c78e057c483694eeeae1e7',
        'merge_commit':ENTRY,'parents':['1e1fdc1985f125b5092fe1e2252a2767d8d8bc7a','45bc0437d99deb6580c78e057c483694eeeae1e7'],
        'tree':'9a97e5d1c06d6f50b1903b13bad1aa9c77757950','main_governance_run':39303612275,'job':118234888136}
    dump(ROOT/'authoritative/STATE.json',state)
    package={'scope':'S031 exact archived evidence; capped UNKNOWN, not a stratum proof',
             'files':hashes(p for p in DEST.rglob('*') if p.is_file() and p.name!='PACKAGE.json')}
    dump(DEST/'PACKAGE.json',package)
    manifest={'scope':'S031 completed capped session; no witness or whole-stratum result','entry_main':ENTRY,
              'artifact_sha256':hashes(p for p in SESSION.rglob('*') if p.is_file() and p.name!='MANIFEST.json')}
    dump(SESSION/'MANIFEST.json',manifest)
    print(headline)


if __name__=='__main__':main()
