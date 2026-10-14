"""Finalise S008 records after actual worker/audit completion, no next-session execution."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path('validation/S008')
ENTRY='23d36d93ebb225668180c8499eb6793775d4fa1d'
TREE='7556cac9eee8a6e26af5460b7d16d8479e5f1e29'
BRANCH='codex/S008-kuratowski-support'


def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d):Path(p).write_text(json.dumps(d,indent=1,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def write(p,s):Path(p).write_text(s,encoding='utf-8',newline='\n')


def records():
    original=load(ROOT/'SUMMARY.json');tree=load(ROOT/'tree/SUMMARY.json')
    seqrows=load(ROOT/'search_results.json');treerows=load(ROOT/'tree/search_results.json')
    assert len(seqrows)==len(treerows)==4
    assert not any(r['verdict']=='BIPLANAR_CHECKED_CHI10' for r in seqrows+treerows), 'Positive requires full result audit before closeout'
    transfer=load(ROOT/'transfers.json')
    transferred={r['index'] for r in transfer if r['verdict']=='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED'}
    last_transfers=load(ROOT/'last_transfers.json')
    transferred|={r['target'] for r in last_transfers if r['verdict']=='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED'}
    new=sorted(set(original['S008_new_exclusions'])|set(tree['S008_new_exclusions'])|transferred)
    prior=load('validation/S007/SUMMARY.json');s=dict(prior)
    s.pop('S007_new_exclusions');s['S008_new_exclusions']=new
    s['excluded_indices']=sorted(set(prior['excluded_indices'])|set(new))
    s['remaining_unknown_indices']=sorted(set(range(271))-set(s['excluded_indices']))
    s['remaining_unknown']=len(s['remaining_unknown_indices'])
    s['D2_remaining_unknown']=sorted(set(prior['D2_remaining_unknown'])-set(new))
    from blowup_graph import blowup
    import collections
    corpus=load('validation/S003/survivors_alpha_ge3.json')
    counts=collections.Counter(6*sum(corpus[i][1])-12-len(blowup(*corpus[i][:2])[0]) for i in s['remaining_unknown_indices'])
    s['stratum_remaining_counts']={str(k):v for k,v in sorted(counts.items())}
    s['transfer_new_exclusions']=sorted(transferred)
    s['transfer_mapped_indices']=load(ROOT/'transfer_search.json')['mapped']
    s['last_transfer_verdicts']=[{k:r[k] for k in ('source','target','verdict','permutations')} for r in last_transfers]
    s['transfer_stop']=load(ROOT/'transfer_stop.json')
    heavy=load(ROOT/'heavy_tree/result.json');s['heavy_K7I5_tree_verdict']=heavy['verdict']
    assert load(ROOT/'supervised_upper_command.json')['returncode']==0
    lanes={}
    for name,rows in [('sequential',seqrows),('tree',treerows)]:
        lanes[name]=dict(targets=[r['target']['index'] for r in rows],
            unknown=[r['target']['index'] for r in rows if r['verdict']=='UNKNOWN'],
            not_run=[r['target']['index'] for r in rows if 'NOT_RUN' in r.get('reason','')],
            capped=[r['target']['index'] for r in rows if r.get('run',{}).get('reason')=='external wall cap'],
            native_export_capped=[r['target']['index'] for r in rows if r.get('certificate',{}).get('solve',{}).get('reason')=='external wall cap'],
            stopped_after_checked_transfer=[155] if name=='tree' and s['transfer_stop'].get('returncode')==0 else [])
    attempted={r['target']['index'] for r in seqrows+treerows if 'run' in r}
    s['registered_unknown']=sorted(set((162,155,157,159))-set(new))
    s['registered_not_run']=sorted(set((162,155,157,159))-attempted)
    s['wall_capped']=sorted(set(lanes['sequential']['capped'])|set(lanes['tree']['capped']))
    s['lanes']=lanes;s['prior_S007_registered_not_run']=prior['registered_not_run']
    for key in ('global_relaxation_verdicts','heavy_cover_verdicts','heavy_K7I5_cegar_verdict'):
        s['prior_'+key]=s.pop(key)
    s['headline_advance']=False;s['headline_bounds']=[9,12];save(ROOT/'SUMMARY.json',s)
    outcome=f"S008 adds{len(new)} checked finite exclusions; total{len(s['excluded_indices'])}/271, {s['remaining_unknown']} biplanarity UNKNOWN."
    scope=f"Sequential lane UNKNOWN{lanes['sequential']['unknown']}, NOT_RUN{lanes['sequential']['not_run']}, search caps{lanes['sequential']['capped']}, native export caps{lanes['sequential']['native_export_capped']}. Tree lane UNKNOWN{lanes['tree']['unknown']}, NOT_RUN{lanes['tree']['not_run']}, search caps{lanes['tree']['capped']}, native export caps{lanes['tree']['native_export_capped']}, stopped after checked transfer{lanes['tree']['stopped_after_checked_transfer']}. Overall registered NOT_RUN{s['registered_not_run']} and UNKNOWN{s['registered_unknown']}."
    sources=load('catalogue/SOURCES.json')
    updates={
        'SRC-0009':'S008 current abstract/v1 HTML X1-X3/local completion reductions re-inspected; alpha<=2 restriction retained, external Lean/LRAT not executed.',
        'SRC-0012':'S008 primary v1 description/metadata refreshed; PDF/package not executed.',
        'SRC-0017':'S008 live main/tree/date API matches corrected2026 pin; external SMS proofs not replayed.',
        'SRC-0021':'S008 live repository API still404; contents UNKNOWN.',
        'SRC-0027':'S008 primary Theorem1.3 and Lemma3 local induction re-inspected; methods attributed, full Gallai/density proof not reconstructed.',
        'SRC-0029':'S008 current abstract/v2 main statement parameter restrictions retained; main proof/package not audited.'}
    for x in sources:
        if x['id'] in updates:
            if updates[x['id']] not in x['note']:x['note']+=' '+updates[x['id']]
            x['accessed']='2026-10-14'
    if not any(x['id']=='SRC-0030' for x in sources):sources.append(dict(id='SRC-0030',
        title='On Graphs with Chromatic Number and Maximum Degree Both Equal to Nine',authors='Rachel Galindo and Jessica McDonald',
        year=2026,publication_date='2026-10 (day unspecified by primary page)',
        url='https://digitalcommons.georgiasouthern.edu/tag/vol13/iss2/1/',access='ABSTRACT_INSPECTED',accessed='2026-10-14',
        note='Primary journal abstract inspected. Theory & Applications of Graphs13(2),Article1. Maximum-degree-nine setting; no transfer to degree11/unbounded high vertices and no proof inspection.'))
    save('catalogue/SOURCES.json',sources)
    smd='# Sources register after S008\n\nExact access grades and local inspection limits retained.\n\n'
    for x in sources:
        smd+=f"## {x['id']} — {x['access']}\n\n{x['title']} ({x.get('year')}). {x['authors']}.\n\n{x.get('url') or 'No primary URL inspected.'}\n\n{x['note']}\n\nPublication date: {x.get('publication_date','not independently verified')}; accessed: {x.get('accessed','not newly refreshed')}.\n\n"
    write('catalogue/SOURCES.md',smd)
    claims=load('catalogue/CLAIMS.json')
    additions=[dict(id='CLM-0050',claim='Completion K5/input K3,3 clauses and the S008 totalizer representation are necessary in the registered full-layer CNFs.',status='PROGRAMME_PROVED',sources=['SRC-0009'],note='Euler/bipartite Euler and orbit-minimum proof in research/S008_ENCODING; library counter trust,27 direct controls/23 independent enumeration/2304 truth tests/23 tree pins. No SAT converse.'),
        dict(id='CLM-0051',claim='For every nonempty family of t heavy K8 noncut cores in a12-critical biplanar graph, its common exterior boundaries have union size at least ceil((7t+12)/6), hence admit distinct high-neighbour representatives.',status='PROGRAMME_PROVED',sources=['SRC-0027','SRC-0014'],note='All-order49t-edge Euler subgraph proof and classical Hall induction in research/S008_SHARED_SUPPORT. Overlap-weighted excess only; not distinct high-excess representatives, recolouring or universal upper improvement.'),
        dict(id='CLM-0052',claim='An11-colouring of G minus a family of heavy K8 noncut cores extends simultaneously through them iff every five-vertex exterior boundary uses at most four colours.',status='PROGRAMME_PROVED',sources=[],note='Exact clique/list argument in research/S008_NO_SPARE. No existence theorem for a suitable exterior colouring; actual criticality forces at least one bad block in every such colouring, possibly different blocks.')]
    if new:
        additions.append(dict(id='CLM-0053',claim=f'S008 adds{len(new)} checked non-biplanarity exclusions among the fixed271 exactchi10 candidates, rows{new}; {s["remaining_unknown"]} remain UNKNOWN.',
            status='COMPUTED_EXACT',sources=['SRC-0009','SRC-0024','SRC-0025'],
            note='New full-layer negatives use their own cold CNF/counter representation and original/compact/cold retained DRAT checks; any transfer uses independently checked labelled injection from a checked obstruction. Fresh lower chromatic proofs/proper10-colourings separate. Finite inputs only, no thickness-minimality/novelty/headline advance. Exact per-lane/transfer artifacts in validation/S008.'))
    if heavy['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
        additions.append(dict(id='CLM-0054',claim='The labelled K7 joined to independent5 is non-biplanar; hence no actual12-critical biplanar graph has a heavy K8 endblock with a cut vertex.',
            status='COMPUTED_EXACT',sources=['SRC-0009','SRC-0024','SRC-0025'],
            note='Cold tree FullCover CNF and original/compact/retained DRAT checked in validation/S008/heavy_tree. General injective transfer: noncut core7 plus its cut and four common high neighbours contains this graph after deleting outside edges. Not all K8 blocks; no universal11-colouring theorem/headline advance.'))
    elif heavy['verdict']=='BIPLANAR_CHECKED_CHI8':
        additions.append(dict(id='CLM-0054',claim='The labelled12v/56e K7 joined to independent5 is biplanar and exactly8-chromatic.',status='COMPUTED_EXACT',sources=[],
            note='Exact disjoint layers, fresh LR/sphere rotations and proper8-colouring; exhibited K8 clique. Not12-critical or a lower-bound lift. See validation/S008/heavy_tree.'))
    additions.append(dict(id='CLM-0055',claim='A heavy odd-cycle endblock in an actual12-critical biplanar graph has length r<=11; a whole heavy odd-cycle low component has r<=9. Independent exterior Z obeys excess>=(r-2)|Z|-11 for an endblock and(r-1)|Z|-11 for a whole component.',
        status='PROGRAMME_PROVED',sources=['SRC-0027','SRC-0014'],
        note='Euler subgraph and published-method blocking count with explicit path/cycle extension in research/S008_NO_SPARE. Actual common9-neighbour sets; overlaps cannot be summed freely. Necessary all-order constraints, no universal upper bound or novelty.'))
    claims=[x for x in claims if x['id'] not in {a['id'] for a in additions}]+additions
    save('catalogue/CLAIMS.json',claims)
    cmd='# Claims register after S008\n\n'
    for x in claims:
        cmd+=f"## {x['id']} — {x['status']}\n\n{x['claim']}\n\nSources: {', '.join(x['sources']) or 'None; programme proof/computation.'}.\n\n{x.get('note','')}\n\n"
    write('catalogue/CLAIMS.md',cmd)
    state=load('authoritative/STATE.json')
    state.update(as_of='2026-10-14',last_completed_session='S008',recommended_next_session='S009',
        headline_status='OPEN_9_TO_12_S008_FULL_COUNTER_CHALLENGES_SHARED_SUPPORT',candidate_10_11_12=outcome+' '+scope,
        latest_session_branch=BRANCH,latest_session_entry_main=ENTRY,latest_session_integration='VERIFY_LIVE_PR_MAIN_AFTER_SINGLE_ATOMIC_COMMIT',
        next_session_is_future_unexecuted=True,source_status='2026_PRIMARY_REFRESH_INCLUDING_OCTOBER_ABSTRACT_LOCAL_DEPENDENCIES_ONLY')
    state['phases'][1]['status']='ACTIVE_FULL_LAYER_AND_SHARED_SUPPORT_NO_HEADLINE_ADVANCE'
    state['s007_integration_verified']=dict(authored_commit='2751cfc659462b888d5579c98358e85d3f909d03',sole_parent='36f12095ca9a09cdabd74550e8bcedee6498f5a6',pr=7,merge_commit=ENTRY,
        merge_parents=['36f12095ca9a09cdabd74550e8bcedee6498f5a6','2751cfc659462b888d5579c98358e85d3f909d03'],tree=TREE,
        head_CI_run=38455256198,main_CI_run=38455487692,head_validate_job=115496220621,main_validate_job=115496995386,combined_status='PENDING_ZERO_CONTEXTS_NOT_CI_PASS')
    state['mathematical_results']=list(dict.fromkeys(state['mathematical_results']+[a['id'] for a in additions]))
    state['open_obligations']=[
        f"Decide remaining{s['remaining_unknown']} fixedchi10 rows; exact indices in S008/SUMMARY.",scope,
        'D2 all42 source rows must be accounted individually; stronger/tree models and caps do not close a stratum.',
        'All four prior globalD2 models SAT_RELAXATION; K7-I5 Cover/Kuratowski UNKNOWN, K6-I6 exactchi7/biplanar.',
        'Row165 no-lex and row158 smaller deletion UNKNOWN; no new minimality/containment theorem.',
        'C5 maximal13/children and independent wholek8/k9 census open; only two fixedk8 samples;159 corpus apices excluded, apex(C5K3)chi9/biplanarity UNKNOWN.',
        'Universal upper: support expansion supplies representatives, not colours; need simultaneous heavy/light exterior flexibility and all-order large-deficit control.',
        'Verify S008 actual authored commit/ordinary PR/two-parent merge/main checks live after frozen commit.',
        'Novelty/external universal review/Lean/formalisation/publication/outreach gates unpassed.']
    save('authoritative/STATE.json',state)
    write('sessions/S008/RESEARCH.md','# S008 research outcome\n\n'+outcome+' '+scope+'\n\nRead the three S008 dossiers. Complete new full-layer cuts and a second totalizer representation were tested with actual completions; the registered searches and all caps are finite outcomes. Shared-support expansion/overlap accounting and exact simultaneous core extension are necessary constraints only. No universal bound, construction lift, external review, novelty, Lean or publication.\n')
    write('sessions/S008/CLOSEOUT.md',f'''# S008 closeout — 2026-10-14

Exactly S008 authorised and executed. Headline OPEN9<=chi_2<=12 unchanged. {outcome} {scope}

Cold K9/row165/bag and all40 retained full refutations freshly regenerated/native checked;271 chromatic archive/CNF/colour audits and four fresh lower proofs passed.23 inherited+23 StrongCover splits,27 direct clause/rotation controls with supervised repeat,23 independent cut-family comparisons,2304 totalizer truth checks and23 tree completion pins passed.5 support-overlap counts and512 availability triples corroborate finite obligations only. No cap/partial CNF/relaxed SAT was used as an exclusion or witness.

Necessary all-order shared-support expansion, overlap-aware excess and exact simultaneous core extension criterion do not prove an11-colouring theorem or bound counterexample order/deficit. Current2026 sources including a primary October abstract inspected with explicit access limits; no novelty guarantee or external certificate/Lean replay. See ADVERSARIAL for provenance repairs and remaining assumptions. Local final checks/manifest recorded separately; hosted checks are observed after commit.

S007 PR#7/single authored commit/two-parent merge/matching tree/actual successful head and main jobs independently reconciled. S008 branch{BRANCH} begins at{ENTRY}, tree{TREE}. Own authored/PR/merge identities follow this file freeze and cannot be anticipated. Actual exit evidence is captured in ignored artifacts/tmp/S008/LIVE_EXIT_EVIDENCE.json and final response. Zero status contexts is not CI PASS.

Containment search mapped{load(ROOT/'transfer_search.json')['mapped']} within the registered distinct-bag family; new accepted transfers{sorted(transferred)}. Misses are not exclusions. Heavy K7-I5 new tree outcome:{heavy['verdict']}; other historical encodings remain their own UNKNOWN observations.

Source159→target155 is an independently checked24-vertex/130-edge isomorphism. The target exclusion comes from that source's completed native/cold proof, not a target-native proof or interruption. Its fresh non9 proof/proper10-colouring were separately checked. The redundant target tree solve was stopped after this proof transfer, retains UNKNOWN with actual return code/elapsed time and explicit stop metadata. No stop promotes negative evidence. Row162 and other direct negatives have their own checked full CNFs; no smaller/minimality or general noncontainment theorem is claimed.

S009 is FUTURE/UNEXECUTED only. No Lean, Palomar, registration, manuscript/publication, arXiv/journal, announcements or external correspondence executed.
''')
    for p,addition in [
        ('authoritative/START_HERE.md','\nS008 explicitly invoked and mathematically closed. '+outcome+' '+scope+' Shared-support/exact extension and full-layer counter challenges are necessary/finite only;9..12 unchanged. Read all S008 records/dossiers/CAM0009/SUMMARY/manifest. S007 integration independently verified in STATE; S008 outgoing integration live after freeze. S009 FUTURE/UNEXECUTED only.\n'),
        ('docs/PHASE_GATE_LEDGER.md','\nS008: '+outcome+' '+scope+' Headline gate1 NOT PASSED;9..12 unchanged. Gates2–7 unchanged; no universal/external review/Lean/publication.\n'),
        ('docs/DECISION_LOG.md','\n- D032(S008): Cold native replay before acceptance; new completionK5/inputK33 and tree-counter lanes registered separately, preserving each UNKNOWN/NOT_RUN/cap.\n- D033(S008): Shared support has Euler expansion/Hall representatives, with overlap-weighted excess; simultaneous extension needs colours, not only representatives. No universal/large-deficit advance.\n- D034(S008): Preserve actual launch versions and supervisory deviations; no fabricated hashes or negative inference. S009 future only.\n'),
        ('docs/FAILURE_LEDGER.md','\n| F036 | Euler expansion supplies simultaneous available colours | Distinct arbitrary support representatives do not control lists/boundary repetition | Universal no-spare route open |\n| F037 | Shared boundaries permit summing13t unweighted excess | Correct sum is weighted by support multiplicity; abstract sunflower passes expansion | Need actual maximum multiplicity/control |\n| F038 | Pairwise list feasibility implies global distinct assignment | Three{0,1} lists,512 registered controls | Hall/list/colour obligations separate |\n| F039 | Full-layer K5/K33/tree counter changes settle D2 | '+scope+' | No cap exclusions or full-stratum claim |\n'),
        ('campaigns/README.md','\n| [CAM-0009](CAM-0009.md) | S008 two fixed full-layer lanes, cold proofs, shared-support/palette controls | '+outcome+'9..12 unchanged |\n\nS008 manifest/SUMMARY retain distinct lane scopes; S009 FUTURE/UNEXECUTED.\n'),
        ('campaigns/CAM-0009.md','\n## Observed closeout\n\n'+outcome+' '+scope+' All registered baseline/controls checked; necessary support/extension results only,9..12 unchanged. No future-session execution or owner-gated downstream activity.\n'),
        ('README.md','\n## S008 results\n\n- [Full-layer encoding](research/S008_ENCODING.md): necessary completionK5/inputK33 and tree-counter challenges; '+outcome+'\n- [Shared supports](research/S008_SHARED_SUPPORT.md): all-order Euler expansion/Hall representatives and overlap-weighted excess.\n- [No-spare extension](research/S008_NO_SPARE.md): exact simultaneous core extension criterion; no universal upper improvement.\n\nOnly through S008 executed; S009 FUTURE/UNEXECUTED. Headline9..12 and all downstream gates unchanged. Historical future labels superseded only through S008.\n')]:
        with open(p,'a',encoding='utf-8',newline='\n') as f:f.write(addition)
    ledger=Path('docs/SESSION_LEDGER.md').read_text(encoding='utf-8')
    ledger=ledger.replace('| S008 | Future | D2 and no-spare critical exterior flexibility | None yet | FUTURE UNEXECUTED |',
        '| S008 | 2026-10-14 | Full-layer Kuratowski/tree encodings and shared critical support | '+outcome+'9..12 unchanged | MATHEMATICS COMPLETE; outgoing integration verify live |\n| S009 | Future | Full-layer decisions and simultaneous exterior colours | None yet | FUTURE UNEXECUTED |')
    write('docs/SESSION_LEDGER.md',ledger)
    phase=Path('docs/PHASE_GATE_LEDGER.md').read_text(encoding='utf-8').replace('Status after S007','Status after S008')
    lines=phase.splitlines()
    for i,line in enumerate(lines):
        if line.startswith('| 1 Headline mathematics |'):
            lines[i]='| 1 Headline mathematics | Actual rigorous improvement or complete solution, source and proof audit | ACTIVE; '+outcome+' No bound advance; headline gate NOT PASSED |'
    write('docs/PHASE_GATE_LEDGER.md','\n'.join(lines)+'\n')
    write('authoritative/NEXT_SESSION_PROMPT.md',f'''# S009 — full-layer decisions and simultaneous exterior colours (FUTURE, UNEXECUTED)

STOP. S008 invocation authorises no S009. A fresh explicit owner invocation permits exactly S009, not S010. Exact finite simple thickness-two Earth–Moon chi_2 remains9..12. Partial bound advances are not full resolution. No separately gated Lean/formalisation, registration, publication or outreach authority.

## Entry before writes

Pin LIVE remote main SHA/tree/status. Reconcile S008 ONE authored commit on {BRANCH}, sole parent{ENTRY}, ordinary non-draft PR, two-parent non-force merge and matching trees. Obtain outgoing identities live; do not anticipate from frozen files. Audit all open/recent/competing PRs/branches/records/workflows/runs/jobs/check-runs/status contexts/protection/rulesets. Zero contexts is not CI PASS; unavailable endpoints UNKNOWN.

Read AGENTS/STATE/START_HERE/protocol, COMPLETE S008 records including owner invocation/EXECUTED_PROMPT, three S008 dossiers, CAM0009 and amendments, SUMMARY/manifest/README/paired catalogues/programme ledgers. Archive fresh invocation/full prompt. Preregister ranges/completeness/symmetry/environment/commands/observed launch hashes/checkers/certificates/stops BEFORE computation. Proactively refresh recent primary work including2026; honest access grades.

## Construction

All271 originalalpha>=3 rows exactchi10. {outcome} {scope} Exact indices and per-lane metadata in S008/SUMMARY. Prior S007 NOT_RUN[157,159] is historical; the S008 tree lane attempts them. D0/D1 fixed-list strata already excluded; D2 still requires accounting all42 source rows (currently{len(s['D2_remaining_unknown'])} UNKNOWN). Prior four globalD2 models SAT_RELAXATION only; no biplanarity converse. Necessary completionK5/inputK33 cuts and totalizer representation do not justify caps. Shared/noninput completions remain permitted. Distinct global faces only proved atD<=2, disabled atD>=3. Restricted row157 distinct-bag maps:{load(ROOT/'transfer_search.json')['mapped']}; no missed-map exclusion or general containment completeness. Later source159→target155 is an exact24v/130e isomorphism from a checked native/cold negative;155 excluded by transfer, not by its interrupted tree solve or capped sequential export. Source162→155 restricted map miss is not noncontainment.

Cold regenerate/replay retained proofs before new acceptance; inspect necessity/actual lex, not inherited VERIFIED text. Prioritise genuinely stronger full encoding/cuts, structural compression or justified longer registered searches/minimal certified obstruction with general injective transfer. Compare actual counter sizes: totalizer does not automatically mean fewer clauses. Do not repeat short UNKNOWNs as exclusions. Partial initial/last-cut CNFs are NOT refutations. Row165 no-lex remainsUNKNOWN, S00523v row158 deletionUNKNOWN; no minimality/containment theorem. C5 maximal13/children and independent wholek8/k9 census remain open, only two fixedk8 samples. All159 corpus apices excluded; apex(C5[K3]) exactchi9/biplanarityUNKNOWN, no lift. K7-I5 Cover/KuratowskiUNKNOWN; K6-I6 exactchi7/biplanar checked.

Positive requires labelledV/E1/E2 exact disjoint input union, EACH independent planarity/sphere rotation, proper k-colouring and fresh checked non(k-1) proof. Negative requires sound necessary CNF/cuts/symmetry, exact cold LF byte regeneration and checked DRAT/LRAT. Original/compact raw/gzip hashes distinct; SAT relaxation/unverified UNSAT/caps/NOT_RUN/failed transfer stayUNKNOWN.

## Upper routes

Keep S005/S006 density inequalities with their distinct component corrections. S007 proves chi(G-C)=11 for EACH low component of actual12-critical biplanar G; chi(H)=11 follows only when L is nonempty connected. Published SRC0027 extension/light-pair/spare-colour/counting methods attributed. No simultaneous deletion conclusion for disconnected L. S008 heavy K7-I5 tree outcome:{heavy['verdict']}; interpret only its checked certificate/split. Historical Cover/Kuratowski caps remain UNKNOWN, not evidence against a new checked verdict.

HeavyK8 noncut cores T_i have7 low vertices and4 independent common high neighbours A_i. For every nonempty subfamily of t cores, |union A_i|>=ceil((7t+12)/6); identical boundaries cannot occur twice, and Hall supplies distinct arbitrary high-neighbour representatives. This does NOT select distinct degree>=16 vertices or available colours. Correct excess sum is sum_v r_v(deg(v)-12)>=13t, not unweighted13t without multiplicity bound; degree(v)>=7r_v. Average overlap control does not bound maximum overlap. Abstract sunflower is an inequality countermodel, not an actual biplanar12-critical witness.

An11-colouring of G-(union T_i) extends iff EACH A_i union{{z_i}} uses at most4 colours. Actual criticality forces at least one bad boundary in every such colouring, possibly changing with the colouring. Need all-order simultaneous no-spare flexibility beyond SRC0027's e_H+c<=65 budget, light/heavy overlap control and separate large-deficit argument. Palette equality is not actual-neighbour equality. Hall distinct-colour/list assignment is not arbitrary proper list colouring or boundary repetition. Pairwise feasibility fails globally; independent vertices may repeat colours. No copied planar contraction/separation: paths switch layers. Universal theorem requires all finite simple biplanar graphs/full proof/boundaries/induction/discharging and independent adversarial review; finite tests never suffice.

S008 heavy odd-cycle analysis: common9-neighbour endblocks have odd length r<=11; whole heavy odd-cycle components r<=9. For independent Z in the boundary, endblock excess>=(r-2)|Z|-11, whole-component excess>=(r-1)|Z|-11. Greedy path extension uses endpoint lists>=2/internal>=3 after boundary repetition, not a clique assumption. These necessary constraints do not eliminate remaining lengths or control repeated supports/all-order deficit.

SRC0028 k controls maximum degree k-1, not clique size. SRC0029 mad11+1/28 is not supplied by mad<12; k>=47/352 cannot specialise. SRC0030 is an October2026 maximum-degree-nine ABSTRACT only, no degree11 transfer. No external primary archives/main proofs fully replayed, novelty unassured.

## Tools and exit

Pinned .venv/native source/binary hashes in S008 environment/manifest; S004 build instructions. WindowsCaDiCaL has no-t; descendant-tree wall/private-memory supervision12GiB, max concurrency2; freshK9 verification if a new flush adapter is used. Two consecutive FINAL UNKNOWNs stop EACH lane, including exit0/check failures; later rowsNOT_RUN. Preserve actual partial metadata, initial/last-cut CNFs, observed launch versions and honest reconstruction grades. S008 initial control supervision deviation was repaired by registered supervised repeat; inherited adapter overwrites outer replay hash filename, so don't fabricate a lost observed outer hash. Adapter/baseline hashes observed before launch and snapshots retained.

Sync sources/claims MD+JSON/state/phase/session/decision/failure/campaign ledgers and allS009 INPUT/PLAN/RESEARCH/ADVERSARIAL/PRIOR_ART/CLOSEOUT. One atomic authored commit/ordinary PR/non-force two-parent merge and independent live verification. Prepare S010 FUTURE/UNEXECUTED only. No novelty guarantee, fake citations/hashes/proofs/CI/embeddings, EMP-resolution claim, Lean, registration, publication, announcements, arXiv/journal or external correspondence.
''')
    write(ROOT/'README.md','''# S008 reproduction and trust

CAM0009 and prospective amendmentA are the registration. From repo root with pinned .venv/native S004 tools:

    .venv/Scripts/python.exe tools/s008_entry.py
    .venv/Scripts/python.exe tools/s008_run.py replay
    .venv/Scripts/python.exe tools/s008_run.py controls
    .venv/Scripts/python.exe tools/s008_controls_audit.py
    .venv/Scripts/python.exe tools/s008_upper.py
    .venv/Scripts/python.exe tools/s008_run.py search
    .venv/Scripts/python.exe tools/s008_tree_run.py
    .venv/Scripts/python.exe tools/check_s008_archives.py --verify-only
    .venv/Scripts/python.exe tools/check_s008_archives.py --tree
    .venv/Scripts/python.exe scripts/check_scaffold.py
    .venv/Scripts/python.exe -m unittest discover -s tests -v

Entry capture is read-only remote evidence written locally; on a later main its results will differ from the frozen S008 entry. Do not rewrite previous evidence. At most two computing workers; caps and per-lane finalUNKNOWN stop rules are distinct. Baseline40 full proofs and four target lower proofs are fresh native checks;271 archive/CNF/colour checks are not fresh replay of all271 lower proofs. Initial direct27 controls lacked external supervision; registered repeat passed. Tree2304 finite truth checks and23 pinned completions are not a universal proof by testing.

Initial/partial CNF archives have no complete refutation. Cold-regenerate last cuts with original or tree generator as indicated, compare raw/gzip hashes, and never promote a partial CNF or cap. Any full negative requires separate original/compact/native cold checks. New clause necessity and overlap/support/extension proofs are in the three dossiers. Actual support-pair Euler exclusions concern their explicit local subgraphs, not new chi10 frontier exclusions. Passing Euler cases UNKNOWN.

Direct new negatives are157,159,162. Target155 transfers through the explicit24v/130e isomorphism from159 in last_transfers.json; its own capped export/interrupted solve are UNKNOWN. Independently reconstruct all labelled edges/map and compare source native/cold archive checks, plus target fresh chromatic proof. The registered source162→155 bag-map miss and source157-all271 search are restricted misses, never general noncontainment. Native source proof hashes are not represented as target-native proof hashes. Transfer stop metadata is separate.

Snapshots/observed launch hashes preserve adapter identity; overwritten outer replay filename is documented. Native logs preserve actual bytes; manifest hashes staged Git blobs, excludes itself. Source pins/library/checker/classical completion dependencies remain, no Lean/external universal review/novelty/publication. Own outgoing PR/merge evidence is observed after freeze. Only S008 executed, S009 FUTURE/UNEXECUTED.
''')
    print(outcome,scope)


def manifest():
    files=subprocess.check_output(['git','diff','--cached','--name-only','-z'],text=True).split('\0')
    table={}
    for p in files:
        if not p or p=='validation/S008_MANIFEST.json':continue
        raw=subprocess.check_output(['git','show',':'+p])
        table[p]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
    save('validation/S008_MANIFEST.json',dict(session='S008',date='2026-10-14',entry_main=ENTRY,entry_tree=TREE,branch=BRANCH,
        owner_invocation='sessions/S008/OWNER_INVOCATION.md',executed_prompt='sessions/S008/EXECUTED_PROMPT.md',preregistration='campaigns/CAM-0009.md and prospective amendments',
        environment=load(ROOT/'environment.json'),summary=load(ROOT/'SUMMARY.json'),checks=load(ROOT/'checks.json'),
        artifact_hash_policy='Staged Git blob bytes; native logs -text; manifest excludes itself',artifact_sha256=table,
        outgoing_integration='Observe one authored commit/ordinary PR/non-force two-parent merge/tree/main checks after freeze; ignored artifacts/tmp/S008/LIVE_EXIT_EVIDENCE.json and final response. Zero status contexts not CI PASS.',
        limitations='No bound advance/universal theorem/whole-stratum census/novelty/external review/Lean/publication. Per-lane caps and partial CNFs not exclusions.'))
    print('S008 manifest',len(table),'staged Git blobs')


if __name__=='__main__':{'records':records,'manifest':manifest}[sys.argv[1]]()
