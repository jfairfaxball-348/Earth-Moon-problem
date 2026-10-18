"""Write final S026 governance from completed receipts; no science is run."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,s):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,d):write(p,json.dumps(d,indent=2)+chr(10))
def append(p,marker,s):
 old=(ROOT/p).read_text(encoding='utf-8')
 if marker not in old:write(p,old+chr(10)+s+chr(10))
def main():
 q=read('validation/S026/local/QUEUE.json');a=read('validation/S026/audit/AUDIT.json')
 assert q['status']=='QUEUE_FINISHED_NOT_A_SESSION_CLOSEOUT'
 assert a['status']=='FINISHED_WITH_EXPLICIT_PER_CASE_VERDICTS'
 assert a['old18_absence_audit_complete']
 jobs=[];new=[];unknown=[];positive=[]
 for item in q['jobs']:
  tag=item['tag'];d='validation/S026/local/C5-'+tag;r=read(d+'/SUMMARY.json')
  verdict=r['verdict'];cert=verdict=='NONBIPLANAR_CERTIFIED'
  jobs.append(dict(tag=tag,directory=d,verdict=verdict,certified=cert))
  (new if cert else positive if verdict=='BIPLANAR_CHECKED' else unknown).append(tag)
 jobs.append(dict(directory='validation/S026/source',certified=False,kind='HOSTED_SOURCE_COMPLETED_BEFORE_LOCAL_DIRECTION'))
 assert not positive,'Explicit positive sum17 requires amended classification and colouring audit before closeout'
 maps=[dict(candidate=x['candidate'],obstruction=x['tag'],vertex_map=x['vertex_map']) for x in a['containment'] if x['verdict']=='CONTAINS_EXPLICIT_CHECKED']
 assert len(maps)==4
 total=a['classification']['certified_sum17_classes'];pending=', '.join('C5['+','.join(t)+']' for t in unknown) or 'none'
 overview=f'S026: {len(new)} additional C5 negatives certified; {total}/26 sum17 classes certified, {len(unknown)} UNKNOWN. 2185 source models,2180 checked obstruction maps,one filter UNKNOWN,four admitted and all four NON-BIPLANAR by new certified C5 maps;72 independent old18 absence DRAT proofs. No chi>=10 biplanar witness;9<=chi2<=12.'
 save('validation/S026/SUMMARY.json',dict(session='S026',entry_main='96c9f3c9d482844a5c952d856132b99579b660bd',overview=overview,jobs=jobs,additional_C5_certified=new,C5_unknown=unknown,classification=a['classification'],candidate_transfers=maps,source_models=2185,old_filter_transfers=2180,filter_unknown=1,admitted=4,admitted_nonbiplanar=4,old18_absence_proofs=72,range=[9,12],novelty_claimed=False,formalisation_executed=False))
 claims=read('catalogue/CLAIMS.json')
 extra=[
 dict(id='CLM-0097',status='PROGRAMME_PROVED',sources=['SRC-0005','SRC-0014'],claim='Two-branch one-layer contraction lemma: disjoint connected R,S outside K7 Q, with representatives r,s, layer neighbours replacing every missing Q-representative edge, and rs present in G or an R-S edge in that layer, contradict biplanarity.',notes='Hand proof research/S026_TWO_BRANCH_LEMMA.md; independent clause checker s026_check_two_branch.py; actual-meaning positive controls; K9 thickness3 dependency. Necessary candidate filter only; no novelty claim.'),
 dict(id='CLM-0098',status='COMPUTED_EXACT',sources=['SRC-0005','SRC-0014','SRC-0017'],claim=f'S026 additionally certifies non-biplanarity of C5 weights {new}. Cumulative {total}/26 sum17 classes certified; remaining {unknown} UNKNOWN. All262 K9-free sum<=16 classes independently rechecked biplanar. The full iff remains pending unless all26 are certified.',notes='validation/S026/local per-graph clause justification, byte CNF regeneration and native checked DRAT. Three recovered S025 cut sets newly obtain complete proofs. Caps are UNKNOWN; original S025 claims retained historically.'),
 dict(id='CLM-0099',status='PROGRAMME_PROVED',sources=['SRC-0005'],claim='Direct quotient-assignment CNF with exactly-one bag rows, explicit bag-capacity clauses, nonedge incompatibility and within-true-twin ordering is SAT iff a fixed clique blow-up obstruction embeds as a non-induced subgraph of the target clique blow-up.',notes='research/S026_CONTAINMENT_ENCODING.md. Independent decoder checks explicit injective vertex maps on labelled graph edges. A negative needs checked native DRAT for the exact CNF; no encoder/cardinality-library dependence.'),
 dict(id='CLM-0100',status='COMPUTED_EXACT',sources=['SRC-0005','SRC-0037','SRC-0017'],claim='S026 restricted 28-vertex alpha<=3 source:2185 models,2180 independently checked old-C5 transfers,one capped filter UNKNOWN,four admitted graphs. Each admitted graph has alpha=3, noK9, and72 total native DRAT proofs show old18 absence. Each contains a newly certified obstruction, so all4 are NON-BIPLANAR. Five zero-model exact profile CNFs have native DRAT proofs.',notes='validation/S026/source and audit. Base orders9..14,30 fixed profiles,seed260018,capped model counts and SAT calls; not an exhaustive family theorem or headline advance. An explicit proper colouring would only be an upper bound; chi>=10 here follows from28/alpha3, while biplanarity fails.')]
 for e in extra:
  claims=[c for c in claims if c['id']!=e['id']];claims.append(e)
 save('catalogue/CLAIMS.json',claims)
 for e in extra:append('catalogue/CLAIMS.md','## '+e['id']+' ',f"## {e['id']} — {e['status']}\n\n{e['claim']}\n\n{e['notes']}")
 state=read('authoritative/STATE.json')
 state.update(as_of='2026-10-18',last_completed_session='S026',recommended_next_session='S027',headline_status='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S026',candidate_10_11_12=overview,source_status='S026_PRIMARY_SOURCE_REFRESH_ACCESS_GRADED_NO_NOVELTY_CLAIM',latest_session_branch='codex/S026-obstruction-aware',latest_session_entry_main='96c9f3c9d482844a5c952d856132b99579b660bd',next_session_is_future_unexecuted=True)
 state['s026_science']=read('validation/S026/SUMMARY.json')
 state['latest_session_integration']={'status':'S026_AUTHORED_AND_MERGE_IDENTITIES_TO_BE_VERIFIED_LIVE_AFTER_COMMIT','entry_main':state['latest_session_entry_main'],'receipt_scope':'The atomic commit cannot contain its own outgoing SHA. Verify ordinary PR, two-parent merge, equal tree and actual hosted governance jobs live; WIP branches are never merged.'}
 state['c5_blowup_classification'].update(sum17_certified_nonbiplanar=total,additional_S026_certified_tags=new,pending_sum17_tags=unknown,iff_theorem_status='COMPLETE' if total==26 else 'PENDING_REMAINING_SUM17_CLASSES')
 state['c5_blowup_classification']['sum17_certified_list'] += ['C5['+','.join(t)+']' for t in new if 'C5['+','.join(t)+']' not in state['c5_blowup_classification']['sum17_certified_list']]
 state['c5_blowup_classification']['claims'] += [c for c in ['CLM-0098'] if c not in state['c5_blowup_classification']['claims']]
 state['open_obligations']=[f'S027 FUTURE: avoid all{total} certified C5 obstructions during candidate generation; quantitative learned-obstruction source, independent containment checks, bounded checkpoint continuation for '+pending+'.','S026 source: all4 admitted candidates now non-biplanar;one separate filter timeout remains UNKNOWN. No exhaustive 28-vertex source theorem.','Local laptop execution preferred by owner; each invoked session must pass full271+K9 smoke,one heavy11GiB tree,explicit caps and durable checkpoints.']+state['open_obligations']
 state['mathematical_results']+= [e['id'] for e in extra if e['id'] not in state['mathematical_results']]
 state['session_gate']='S026 completed; S027 FUTURE/UNEXECUTED until new owner invocation under D047. D042 lower-only; no publication/formalisation.'
 # Retain history but clearly label stale queue policies as discharged.
 state['next_session_serial_219_policy']['status']='HISTORICAL_DISCHARGED_D058_ALL271_NONBIPLANAR'
 state['next_session_serial_219_policy']['remaining_original_unknown']=0
 save('authoritative/STATE.json',state)
 prompt=f"""# S027 — learned-obstruction candidate generation (FUTURE / UNEXECUTED)

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

The owner's submission of this prompt, its link, or 'run next session' invokes exactly S027 under D047. No second confirmation. Stop before S028. D042 remains lower-only: one finite simple biplanar graph with chi>=10, explicit disjoint labelled layers, independent planarity checks and checked non9 proof or elementary counting certificate. No universal upper-bound work, Lean, registration, publication or correspondence.

Read live remote main SHA/tree, PR parents, actual checks/jobs, open PRs/branches/rulesets before writes. Read AGENTS, STATE, START_HERE, SESSION_PROTOCOL, CERTIFICATE_POLICY, S026 CLOSEOUT/RESEARCH/ADVERSARIAL/PRIOR_ART/MANIFEST, research/S026_TWO_BRANCH_LEMMA.md, research/S026_CONTAINMENT_ENCODING.md, campaigns CAM0030/31 and validation/S026/SUMMARY.json. Preserve the original271 NON-BIPLANAR decisions; D051/D054 priority is discharged.

Frozen S026 facts: {overview} Newly certified tags: {', '.join(new)}. Remaining C5 sum17 targets: {pending}. Do not claim the full C5 iff while any remain UNKNOWN. External Patil primary sources already state balanced C5 non-biplanarity; novelty is unclaimed and external archives were not replayed.

Main arm: genuinely improve the candidate source. The old source rejected2180/2185 models after generation, and all4 admitted cases were later closed by new obstructions. Preregister a revised weighted source with all certified C5 filters integrated through sound learned projection clauses. For each found obstruction embedding, identify the required base-edge support at that fixed weight profile; its conjunction forces the same explicit subgraph map. Block that conjunction, rather than only the current whole model. Prove the learned clause, independently check the map/support and use positive controls before science. Never learn from UNKNOWN or bare UNSAT. Preserve chi>=10 by an explicit weighted-independence certificate or checked native no9 proof; retain K9/Euler filters. Use30 fixed profiles at most100 candidate models each, seed270018, soft180s/profile and hard7200s whole source; at most6 distinct admitted graphs, each two60s annealing attempts and600s exact search. Register any changed ranges before activation. Caps do not prove exhaustion. Do not rerun the four closed S026 candidates.

Use the independent quotient-assignment containment CNF to audit admitted candidates against every certified C5 obstruction. Accept negatives only with native DRAT; positive maps must be checked on independently rebuilt labelled edges. If the revised source still has zero admissible graphs after its cap, explain quantitatively why and propose a different chromatic source for S028; do not fill time with repeated old profiles.

Secondary bounded arm: continue saved C5 theory-cut checkpoints on the remaining targets above, serially. First independently audit checkpoint input/eager metadata and saved cuts. S026's two-branch pilot used600s, reached UNKNOWN where listed, and saved Kuratowski cuts without internal learned state. Preregister one changed strength strategy (e.g. larger branch sets with the same proved lemma) or justified resumed search; at most3600s search per unresolved graph and1800s each native solve/check,4h absolute graph cap. Stop unchanged cap repetition. Every accepted negative requires independent clause justification, byte-for-byte CNF regeneration and checked native DRAT. Every positive needs explicit split/planarity checks; a sum17 positive would refute the proposed threshold and must be reported honestly. Only if all26 are certified negative may positivity-preserving deletion to sum17 plus the262 checked positives close the full C5 iff.

Execute locally on the owner's laptop through Codex when S027 is invoked. Full scripts/cloud_smoke.py with absolute pinned native paths must pass271 originals plus retained/fresh K9 before science. One heavy process tree,11GiB private-memory cap, external wall supervision; no GPU benefit assumed. Reuse scripts/run_s026_local.py and audit patterns after adapting IDs/caps, and preserve exact raw source/input/native hashes. Use quiet watchdog waits, atomic queue/checkpoint JSON, flushed start/heartbeat/end records and hash-validated completed-unit reuse. Do not infer mid-solver resumption from progress counts. GitHub Actions is an alternate only if local execution is unavailable: D044 ubuntu-24.04 never-merged WIP workflow with SAME-JOB setup and full smoke; .github/workflows/s026-research.yml and validation/S026/HOSTED_39142133864.json retain actual runner/artifact evidence. Hosted green jobs are not mathematical proofs.

Refresh primary prior art twice with honest grades. Record exact counts, timings, memory, seeds, caps, errors and UNKNOWNs. Maintain paired sources/claims, campaigns, decisions/failures/session/phase ledgers and truthful STATE. Commit full S027 INPUT/PLAN/RESEARCH/ADVERSARIAL/PRIOR_ART/CLOSEOUT/MANIFEST/OWNER_INVOCATION/EXECUTED_PROMPT. Write identical COMPLETE S028 FUTURE prompts at authoritative/NEXT_SESSION_PROMPT.md and sessions/S027/S028_FUTURE_PROMPT.md. One atomic authored session commit, ordinary PR, non-force two-parent merge; independently verify main, parents, equal tree and actual hosted governance jobs. Final report must include verified commit/PR/merge links and the FULL S028 prompt verbatim. Do not execute S028.
"""
 write('authoritative/NEXT_SESSION_PROMPT.md',prompt);write('sessions/S026/S027_FUTURE_PROMPT.md',prompt)
 p=ROOT/'README.md';text=p.read_text(encoding='utf-8');text=text.replace('CURRENT NEXT SESSION: S026','CURRENT NEXT SESSION: S027').replace('Status after S025 (2026-10-16; integration reconciled2026-10-18)','Status after S026 (2026-10-18)');write('README.md',text)
 report=f"""# S026 closeout — completed, no headline advance

{overview}

Additional certified C5 tags: {', '.join(new)}. Remaining: {pending}. Original271 stays271 NON-BIPLANAR,0 UNKNOWN. No full C5 iff is promoted while pending cases remain.

Local queue completed with per-case verdicts in validation/S026/local/QUEUE.json. Full271+retained/fresh K9 smoke PASS. One11GiB externally supervised process tree, checkpoints and start/heartbeat/end journal. Five first-pass jobs were blocked before search by a control-reader Path conversion, fixed and repeated without rerunning three completed proofs. Raw CRLF and LF source variants are separately hash archived; base Git commits are not represented as clean-worktree fingerprints.

The main source was completed on hosted run39142133864 before the local instruction; remaining hosted C5 work was cancelled. Owner explicitly requested local execution through Codex. Hosted initial/revised provenance and artifact digests are permanently retained. The local controller makes no model calls and quiet waits need no frequent agent inspection. Davenport S110 operational lessons are in docs/S026_LONG_RUN_LESSONS.md.

All2180 source transfers and all4 alpha3/K9-free certificates are independently checked.72 native DRAT certificates validate absence of old18 obstructions. New explicit maps close all4 admitted graphs. Five source-profile domain negatives are finite-formula results only; one source-filter cap remains UNKNOWN and profiles are not universally exhausted.

No novelty guarantee; primary-source refresh and external proof limitations in PRIOR_ART. D042 lower-only; Lean, registration, publication and outreach unexecuted. S027 is queued FUTURE/UNEXECUTED, byte-identical in authoritative/ and this session.

Integration contract: WIP branches retain exact science pins and are never merged. Collapse session work to one authored commit on live main; ordinary PR and non-force two-parent merge. The outgoing authored/merge SHA cannot be embedded in its own atomic commit. Independently obtain actual head/main governance jobs and verify parent/tree identities after integration; report those live links to the owner. Governance success is not scientific proof replay.
"""
 write('sessions/S026/CLOSEOUT.md',report)
 for file in ['AGENTS.md','authoritative/START_HERE.md']:
  old=(ROOT/file).read_text(encoding='utf-8');heading='# S026 completed authority update D059 (2026-10-18)'
  if not old.startswith(heading):write(file,heading+'\n\n'+overview+' S027 is FUTURE/UNEXECUTED. Owner explicitly authorised local laptop execution through Codex for S026; each future invoked session must establish its own full smoke. Historical instructions below retain their original scopes.\n\n'+old)
 append('docs/SESSION_LEDGER.md','| S026 |',f'| S026 | 2026-10-18 | CAM0030 serial C5 certificates/checkpoints and CAM0031 obstruction-aware source | {overview} | Complete; S027 FUTURE |')
 append('docs/PHASE_GATE_LEDGER.md','S026 (2026-10-18)',f'S026 (2026-10-18): {overview} Phase1 lower-bound gate NOT PASSED; novelty/Lean/publication gates unchanged.')
 append('docs/DECISION_LOG.md','**D059',f'**D059 (S026,2026-10-18):** Owner directly invoked S026 and then expressly requested local laptop execution through Codex. Cancel remaining hosted queue, preserve completed source/artifacts, full fresh local smoke before continuation. One11GiB heavy tree, quiet durable watchdog/checkpoints, retain finished proofs. Add sound two-branch contraction and independent exact quotient-containment audit. {overview} S027 requires a new invocation.')
 append('docs/FAILURE_LEDGER.md','F073 (S026)', '| F073 (S026) | Dense source would admit candidates after post-hoc Euler filtering | Initial4000 models all fail Euler | Move exact Euler bound into registered source CNF; retain initial receipts, no negative family theorem |')
 append('docs/FAILURE_LEDGER.md','F074 (S026)', '| F074 (S026) | New-method local controls execute | Path object passed to string-only J1 reader;five jobs BLOCKED_BEFORE_SEARCH | Convert path, retain failed receipts, fresh smoke and same-five retry; completed3 skipped |')
 append('docs/FAILURE_LEDGER.md','F075 (S026)',f'| F075 (S026) | Old18 obstruction avoidance yields a viable new source | All4 admitted contain a newly certified C5;{len(unknown)} new-method C5 pilots remain UNKNOWN | Integrate every certified obstruction into generation; preserve cap checkpoints; no iff or headline promotion |')
 append('docs/RESEARCH_ROADMAP.md','S026 frontier',f'S026 frontier: {overview} S027 should learn sound embedding-support clauses during generation and use exact independent containment checks. Remaining C5 cases: {pending}.')
 for num,title in [(30,'Serial C5 completion and two-branch contraction'),(31,'Weighted obstruction-aware source and independent containment audit')]:
  write(f'campaigns/CAM-00{num}.md',f'# CAM-00{num} — S026 {title}\n\nRegistration: sessions/S026/PLAN.md and immutable WIP source pins. {overview}\n\nPer-case evidence: validation/S026/SUMMARY.json, local/,source/,audit/. Mathematical scope and failure boundaries: sessions/S026/RESEARCH.md and ADVERSARIAL.md. One local11GiB heavy tree,full smoke,external caps; native certificates require clause checks and byte regeneration. No universal source completeness or novelty.\n')
 append('campaigns/README.md','CAM-0030','- **CAM-0030 (S026)** serial recovered/new-method C5 queue, local pinned full smoke, checked DRAT and resumable theory-cut checkpoints. '+overview)
 append('campaigns/README.md','CAM-0031','- **CAM-0031 (S026)** 30-profile alpha3 source plus independent SAT containment audit; all4 admitted non-biplanar. See validation/S026.')
 # Correct chronology without erasing original observed provenance fields.
 p=ROOT/'validation/S026/local/NEWLINE_PROVENANCE.json';nl=read(str(p.relative_to(ROOT)))
 for r in nl:r['chronology_correction']='Normalization occurred while the first recovered proof was active, AFTER its SOURCE manifest. Both raw variants archived; no semantic change. Original change string was inaccurate.'
 save(str(p.relative_to(ROOT)),nl)
 artifacts={}
 for folder in ['validation/S026','sessions/S026','research']:
  for p in (ROOT/folder).rglob('*'):
   if not p.is_file() or p.name=='MANIFEST.json' and p.parent==ROOT/'sessions/S026':continue
   if folder=='research' and not p.name.startswith('S026_'):continue
   b=p.read_bytes();artifacts[str(p.relative_to(ROOT)).replace('\\','/')]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 save('sessions/S026/MANIFEST.json',dict(session='S026',entry_main='96c9f3c9d482844a5c952d856132b99579b660bd',artifact_sha256=artifacts,scope='Packaging integrity; mathematical acceptance uses archived independent checker and native proof receipts. Outgoing integration identities verified live after atomic commit.'))
 print(overview)
if __name__=='__main__':main()
