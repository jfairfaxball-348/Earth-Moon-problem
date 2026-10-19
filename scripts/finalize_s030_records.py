"""Write S030 closeout and next-session handoff from checked bounded evidence."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def write(path,text):
    (ROOT/path).write_text(text,encoding='utf-8',newline='\n')


def add(path,text):
    p=ROOT/path;p.write_text(p.read_text(encoding='utf-8')+'\n'+text+'\n',encoding='utf-8',newline='\n')


def main():
    s=json.loads((ROOT/'validation/S030/SUMMARY.json').read_text())
    assert s['S11_m155_156']=='UNKNOWN'
    source={'id':'SRC-0057','title':'Paper59 v3 CC0 regular566 literal RUP supplement',
      'authors':'earth_moon_codex_two (rStation handle)','year':2026,'publication_date':'2026-10-15',
      'url':'https://rstation.ai/api/v1/papers/earth_moon_59/versions/3/supplement',
      'access':'PROOF_INSPECTED','accessed':'2026-10-19',
      'note':'S030 inspected encoder/checker and replayed the three finite RUP branches with supplied and independent naive checkers. Packet27864 bytes, b35f139e59467f20b771f090188fa5536d8342dcbc4446cf7945a74fb2fa64b3. Full graph reduction/hand coverage not independently proved. CC0 supplement retained under validation/S030/prior_art/paper59; full regular exclusion not promoted.'}
    sources=json.loads((ROOT/'catalogue/SOURCES.json').read_text())
    assert not any(r['id']==source['id'] for r in sources)
    refresh={
      'SRC-0037':'S030 refreshed primary abstract/HTML: v1 only; n<=18 and universal-vertex18 scopes distinguished; computational/Lean archive not replayed.',
      'SRC-0045':'S030 fetched v3 and inspected the CC0 branch encoder/checker; both supplied and independent RUP replays passed. Full hand coverage remains unverified; see separate SRC-0057 for finite proof scope.',
      'SRC-0048':'S030 direct primary fetch includes the fixed-point-free graph-invariance correction; no automorphism/symmetry exclusion imported.',
      'SRC-0049':'S030 primary refresh:421 propagator decisions await DRAT replay; enumerated objects are paired-twin doublings, not an independently established census of all graphs with closed twins.',
      'SRC-0050':'S030 primary refresh: local normal-form/profile arguments remain source-stated, not a whole155-edge exclusion or discard filter.'}
    for r in sources:
        if r['id'] in refresh:
            r['note']+=' '+refresh[r['id']];r['accessed']='2026-10-19'
    sources.append(source)
    write('catalogue/SOURCES.json',json.dumps(sources,indent=2)+'\n')
    add('catalogue/SOURCES.md','## SRC-0057 — PROOF_INSPECTED (finite RUP branches only)\n\n'+source['authors']+', '+source['title']+', 2026-10-15; accessed2026-10-19. '+source['url']+' . '+source['note']+'\n\nS030 refresh of SRC-0037/0045/0048/0049/0050: see sessions/S030/PRIOR_ART.md and fetch receipts. Whole manuscripts remain STATEMENT_INSPECTED; source claims are not automatic filters.')
    claims=[
      {'id':'CLM-0114','status':'PROGRAMME_PROVED','sources':['SRC-0014','SRC-0012','SRC-0037'],
       'claim':'Necessary order28 alpha<=3 biplanar filters: K9-free,117<=m<=156,delta<=11, every triangle-free subgraph has<=104 edges. Unconditionally delta>=8; conditionally on SRC-0037 Theorem1 delta>=9.',
       'notes':'Full attributed proofs sessions/S030/RESEARCH.md; the conditional delta9 statement does not discharge S8 without its source premise. No novelty or colouring theorem.'},
      {'id':'CLM-0115','status':'PROGRAMME_PROVED','sources':['SRC-0014','SRC-0045'],
       'claim':'Every K9-free order28 graph of minimum degree11 can be relabelled with independent roots0,1,2, neighbors of0 exactly3..13, and nondecreasing adjacency-to-(1,2) types in blocks3..13 and14..27. A biplanar split can put edge03 in layer1.',
       'notes':'Antineighborhood of a degree11 vertex has16 vertices and is not a clique; pick a nonadjacent pair, fix the root star, sort within blocks, exchange layers. Full proof sessions/S030/RESEARCH.md. No automorphism assumption and no novelty.'},
      {'id':'CLM-0116','status':'COMPUTED_EXACT','sources':['SRC-0057'],
       'claim':'Paper59 v3 finite branches q=2,3,4 regenerate71834-variable173170-clause formulas and have independently checked49,188,193 RUP additions ending in empty clauses.',
       'notes':'Supplied stdlib checker plus independent naive unit propagation; all15 supplied file hashes match API manifest. This is only the propositional part: full11-regular graph exclusion remains SOURCE_STATED; hand coverage and reductions are separate premises.'}
    ]
    old=json.loads((ROOT/'catalogue/CLAIMS.json').read_text())
    assert not ({r['id'] for r in old}&{r['id'] for r in claims})
    write('catalogue/CLAIMS.json',json.dumps(old+claims,indent=2)+'\n')
    for r in claims:add('catalogue/CLAIMS.md',f"## {r['id']} — {r['status']}\n\n{r['claim']}\n\n{r['notes']} Sources: {', '.join(r['sources'])}.")
    next_prompt='''# S031 — OP1(b): persistent certified S11 continuation (FUTURE / UNEXECUTED)

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

The owner's submission of this prompt, its link, or "run next session" invokes exactly S031 under D047. Stop before S032. D042 lower-only scope and D062/D063 order28 pivot remain binding. No universal upper-bound work, T3 below28, outreach, formalisation, registration or publication.

Target: a simple biplanar graph on28 vertices with alpha<=3, hence chi>=10, or a checked exclusion of a complete explicitly stated stratum. S030 did not decide any stratum. S11 (delta11,m155/156) is UNKNOWN; S10/S9 are NOT_RUN. The m154 regular case remains SOURCE_STATED: S030 replayed only paper59's three finite RUP branches, not the hand coverage. Delta>=9 imports SRC-0037; an unconditional delta>=8 proof leaves S8 as an explicit fallback obligation. Classical9<=chi2<=12; no chi10 witness.

Entry: independently reconcile live remote main SHA/tree/parents, PR/check jobs/open branches; read AGENTS, STATE, START_HERE, protocol, S030 INPUT/PLAN/RESEARCH/ADVERSARIAL/PRIOR_ART/CLOSEOUT/MANIFEST, validation/S030/SUMMARY.json and SEARCH_REPLAY.json. S029 landscape remains frozen. Keep old queues parked. Record executor. Use hooked cloud setup or the S030-authorised local pinned toolchain; run full scripts/cloud_smoke.py with271 proofs plus retained/fresh K9 before science. One heavy process tree<=11GiB, external wall/private-memory supervision on Windows; no CaDiCaL -t there. A smoke FAIL blocks science. D044 fallback is a preregistered never-merged WIP Actions branch, ubuntu24.04, SAME-JOB scripts/cloud_setup.sh then full smoke, science and durable artifact download; tested historical runner details are in docs/CLOUD_ENVIRONMENT.md and validation/S011/SUMMARY.json. Hosted scaffold CI is governance only.

First independently replay S030 archived models, cuts and finite RUP packet; inspect exact source snapshots and hashes. Obtain an actual17-vertex alpha2 positive control if accessible; J1 is alpha3. The24-vertex alpha3 split is an additional positive control. Do not turn missing calibration into a negative theorem.

Prioritise a materially changed persistent incremental CEGAR solver retaining learned state between valid cuts, with native final-formula DRAT replay if UNSAT, rather than unchanged native restart caps. Preregister finite ranges, symmetry and proof, encoding, memory, wall caps and stop rules before execution. Reuse the globally valid S030 cuts after independent validation. Decode archived final.cnf.gz/CUTS/VARIABLES; do not claim native CDCL state was retained. Root/star/type sorting is justified by CLM-0115; no twin or graph-automorphism restriction. Keep exact alpha-four-set, edge/degree/layer cardinalities, K9, triangle-free104 and certified-library filters; every cut needs an independent semantic checker. Measure bottlenecks without predicting exhaustion from sample throughput.

Continue S11 first. Only a full-stratum checked proof can exclude it; bank each completed stratum separately. S10 then S9 follow only after an actual S11 decision. Caps stay UNKNOWN and retain S11 for the handoff. Any planar SAT survivor stops all search for independent layer/embedding, alpha, proper colouring and chi>=10 counting validation.

Refresh paper59, posts146/152/155 and arXiv since S030 receipts; source-stated results only prioritise until independently re-proved/replayed. The post155 propagator decisions await DRAT, and its enumerated family is the paired-twin doubling slice. Attribute overlap; no novelty claim and no forum contact.

Close exactly S031 with complete records, paired sources/claims and ledgers, permanent certificates/hashes, truthful STATE, byte-identical COMPLETE S032 future prompts in authoritative/NEXT_SESSION_PROMPT.md and sessions/S031/S032_FUTURE_PROMPT.md. One atomic authored commit, ordinary PR, non-force two-parent merge, independently verified main/tree/parents and actual hosted jobs. Final report must include verified links, all stratum verdicts and the FULL S032 prompt. Do not execute S032.
'''
    for a,b in [('on28','on 28'),('order28','order 28'),('delta11','delta 11'),
                ('delta9','delta 9'),('m155/156','m = 155/156'),('m154','m = 154'),
                ('paper59','paper 59'),('Paper59','Paper 59'),('Classical9','Classical 9'),
                ('with271','with 271'),('<=11GiB','<=11 GiB'),('ubuntu24.04','ubuntu-24.04'),
                ('alpha2','alpha 2'),('alpha3','alpha 3'),('The24','The 24'),
                ('actual17','actual 17'),('vertex18','vertex 18'),('theorem1','theorem 1'),
                ('posts146/152/155','posts 146/152/155'),('post155','post 155')]:
        next_prompt=next_prompt.replace(a,b)
    write('authoritative/NEXT_SESSION_PROMPT.md',next_prompt)
    write('sessions/S030/S031_FUTURE_PROMPT.md',next_prompt)
    outcome=f"{s['sat_models']} SAT relaxation models independently audited; {s['seconds']}s registered serial search; S11 m155/156 UNKNOWN; S10/S9 NOT_RUN; no certified stratum or chi>=10 witness;9<=chi2<=12."
    close='''# S030 closeout — bounded OP1(b) work, no stratum decision

'''+outcome+'''

Full local271+K9 smoke PASS. Three search segments: general labelled pilot,
independent-triple anchor, then sorted root types with retained valid cuts.
All saved models and every cut independently audited; Kuratowski subdivisions
checked by suppression to K5/K3,3. No sampled-model blocking or blow-up restriction.
The final segment stopped at its registered800s cap. Interrupted earlier
segments are preserved with native exit4294967295, not reinterpreted as UNSAT.

Written necessary filters and sound relabelling proof: CLM-0114/0115.
External CC0 regular566 packet: all three branches replayed twice (CLM-0116),
including an independently implemented unit-propagation checker. This does
not independently establish the paper's hand reduction/coverage, so the whole
regular154 exclusion is not promoted. Delta9 remains conditional; S8 is the
unsearched unconditional fallback. No requested alpha2 calibration was invented.

Sources/claims and frozen baseline boundaries are documented in PRIOR_ART.
Permanent compact evidence is validation/S030. Native partial DRAT traces
are incomplete search output, not certificates; their final hashes/lengths
are recorded, with final CNFs, semantic cuts and logs preserved. Semantic
cuts are resumable; the solver's internal learned state is not retained.

Validation: all10 existing unit tests passed, as did the archived S026/S027/
S028/D062/S029 record validators. The S030 math controls checked2916 complete
small partition assignments and both RUP implementations. SEARCH_REPLAY.json
records independent model, literal-formula and cut checks. The additional
S030 metadata validator and hosted governance jobs are checked at integration.

No further finite profile closure or headline advance. Parked queues unchanged.
S031 persistent S11 continuation is FUTURE/UNEXECUTED; paired full prompts
are byte-identical. One authored commit on codex/S030-op1b from entry main
1e1fdc1985f125b5092fe1e2252a2767d8d8bc7a. PR/merge identities and hosted jobs
must be verified live after commit (self-identities cannot be hash-pinned in
their own commit). The final user report supplies the verified links.
'''
    write('sessions/S030/CLOSEOUT.md',close)
    st=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
    st.update(as_of='2026-10-19',last_completed_session='S030',recommended_next_session='S031',
              headline_status='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S030',
              next_session_is_future_unexecuted=True,latest_session_branch='codex/S030-op1b',
              latest_session_entry_main='1e1fdc1985f125b5092fe1e2252a2767d8d8bc7a',
              latest_session_integration={'status':'S030_IDENTITIES_TO_BE_VERIFIED_LIVE_AFTER_COMMIT',
                 'entry_main':'1e1fdc1985f125b5092fe1e2252a2767d8d8bc7a'},s030_science=s)
    st['s029_integration_verified']={'pr':38,'authored_commit':'7c60fa8b0d4201204cf059d6c34ac9fc90334be9',
       'merge_commit':'1e1fdc1985f125b5092fe1e2252a2767d8d8bc7a','parents':['742c1a19bac8cd7caf4c734d73fc76262c8ced29','7c60fa8b0d4201204cf059d6c34ac9fc90334be9'],
       'tree':'0d61e17ef478036e8680b68bdfe2b3f92a8232a7','main_governance_run':39239671991,'job':118017161029}
    st['s030_executor']='Codex desktop local Windows; S030 Entry explicitly permits local pinned toolchain'
    st['source_status']='S029_FROZEN_PLUS_S030_DATED_REFRESH_NO_NOVELTY_CLAIM'
    st['open_obligations']=[
       'S031 FUTURE/UNEXECUTED: persistent certified S11 continuation; S030 whole stratum UNKNOWN.',
       'S11 regular154 SOURCE_STATED; only three finite RUP branches replayed, hand coverage not independently re-proved.',
       'S10/S9 NOT_RUN; delta>=9 conditional on SRC-0037, unconditional fallback S8 NOT_RUN.',
       'PARKED: T3 orders21..27, old S029 queue and pending C5 classes, unchanged.',
       'No certified chi>=10 witness;9<=chi2<=12; novelty/Lean/registration/publication/outreach gated.']
    st['mathematical_results']+=['CLM-0114','CLM-0115','CLM-0116']
    write('authoritative/STATE.json',json.dumps(st,indent=2)+'\n')
    header='# D064 S030 completed (2026-10-19; bounded OP1(b), no stratum decision)\n\n'+outcome+' Full local271+K9 smoke PASS; executor Codex desktop. Paper59 finite RUP branches replayed, hand coverage not independently re-proved. S031 FUTURE/UNEXECUTED: persistent certified S11 continuation. Older queues remain PARKED.\n\n'
    for name in ('AGENTS.md','authoritative/START_HERE.md','docs/SESSION_PROTOCOL.md'):
        p=ROOT/name;write(name,header+p.read_text(encoding='utf-8'))
    add('docs/SESSION_LEDGER.md',f'| S030 | 2026-10-19 | Owner `run next session`, Codex desktop local; CAM0036 unrestricted labelled OP1(b) CEGAR | {outcome} Paper59 finite branches replayed twice; hand coverage source-stated | Complete bounded session; S031 FUTURE |')
    add('docs/DECISION_LOG.md','**D064 (S030,2026-10-19):** '+outcome+' Persist valid cuts and whole-formula provenance; next S031 should retain learned state in incremental CEGAR before repeating caps. No upper-bound scope change. Delta9/regular154 dependency boundaries explicit; S8 fallback not discharged.')
    add('docs/FAILURE_LEDGER.md','| F082 (S030) | General labelled K9/Kuratowski CEGAR closes S11 in one bounded session | '+outcome+' Native restart learning is lost between cuts | Persist incremental learning and validated semantic cuts; do not equate model throughput with exhaustive coverage |\n\n| F083 (S030) | Prospective control J1 is alpha2; gate wrapper schema matches | J1 has alpha3; initial wrapper read nonexistent chromatic field after successful smoke | Preserve initial failures, verify fresh original PASS receipt, use actual row counters; no theorem promoted on missing17v alpha2 calibration |')
    add('docs/PHASE_GATE_LEDGER.md','S030 (2026-10-19): '+outcome+' Phase1 lower-bound gate NOT PASSED; novelty/Lean/publication gates unchanged.')
    add('campaigns/README.md','- **CAM-0036 (S030)** unrestricted labelled order28 S11 CEGAR; '+outcome)
    add('campaigns/CAM-0036.md','Final bounded outcome: '+outcome+' Details and independent replay: validation/S030/SUMMARY.json and SEARCH_REPLAY.json.')
    paths=[p for p in (ROOT/'sessions/S030').glob('*') if p.is_file() and p.name!='MANIFEST.json']
    paths += [ROOT/'validation/S030/PACKAGE.json']
    paths += [ROOT/'tools/s030_op1b.py']+list((ROOT/'scripts').glob('*s030*.py'))
    manifest={'scope':'S030 bounded session; no whole-stratum proof or witness',
       'entry_main':'1e1fdc1985f125b5092fe1e2252a2767d8d8bc7a','artifact_sha256':{}}
    for p in paths:
        b=p.read_bytes();manifest['artifact_sha256'][p.relative_to(ROOT).as_posix()]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    write('sessions/S030/MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    print(outcome)


if __name__=='__main__':main()
