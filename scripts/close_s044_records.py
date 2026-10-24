"""Close the S044 audit and narrow live implications; no research/process action."""
import hashlib
import json
from pathlib import Path

from close_s037_records import read, write, dump, append

ROOT = Path(__file__).resolve().parents[1]


def main():
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] == 'S043' and state['recommended_next_session'] == 'S044'
    verify = read('validation/S044/VERIFICATION.json')
    assert verify['status'] == 'PASS' and verify['cpu_upper_accounted'] < 600
    rows = [
        ('S037', 'Sorted prefixes; selected planar pairs, flips and fixed templates',
         'EXACT_SCOPED_AND_CAPPED', '247 prefixes follow sorting; nine S11 cases UNKNOWN; fixed-template arms capped',
         'Best I4 91/125 at 156/155 edges; all 19 saved records <=9-colourable',
         60.1875, '44.625 discovery plus 15.5625 nonextension certificates; acceptance/replays separate',
         'Finite, plateau and conflict stops; no whole-stratum exclusion'),
        ('S038', 'Boundary-only disk supports 1..4 and joint 1+1/1+2/2+1/2+2 at two fixed embeddings',
         'EXACT_NEIGHBOURHOODS_HEURISTIC_ARMS', 'No strict improvement in the tested initial neighbourhoods; paths and other embeddings unexcluded',
         'Best I4 91/123; all 22 saved records <=9-colourable',
         101.09375, 'Experimental CPU only; controls, smoke and replays separate',
         'Registered plateaus; patches offered no best-score advantage'),
        ('S039', 'Degree 3..6 vertex-star relocation; protected Sulanke seeds at order 28',
         'EXACT_NEIGHBOURHOODS_HEURISTIC_ARMS', 'Selected 1811 neighbours exact; broader extensions unsearched',
         'Best I4 82/79; all saved pairs <=9-colourable; protected saved graphs exactly chi9',
         79.71875, 'Experimental CPU; saved classification 1 second separate',
         'Finite plateaus; proposed coordinated move for S040'),
        ('S040', 'One selected star per layer at the 82/79 states; matched arms',
         'EXACT_NEIGHBOURHOODS_PIVOT', '216582/119281 scored states, zero strict improvements; larger moves unexcluded',
         'No qualifying gain; all saved pairs <=9-colourable; K9/K10 repair barrier diagnosed',
         347.0625, '315.15625 experiment plus 31.90625 post-hoc; controls/replays separate',
         'D077 gate failed; star/patch/coordinated objective search parked'),
        ('S041', 'Comparative routes; complete order-13 alpha<=3 slice; three explicit apex leaf shapes',
         'EXACT_SCOPED_AUDIT', '3510 valid biplanar pairs, zero alpha<=3; three individual apex negatives; composition implication narrowed by S044',
         'No witness; order-13 minimum I4 767; no positive apex leaf',
         920.4457328033448, 'Reported probe CPU; mixed precise/rounded components',
         'Ranked R3 then R1; finite probes did not produce a live construction'),
        ('S042', '45 apex-leaf types, 15 resolved and 30 unresolved windows; partial Ore members included',
         'EXACT_FINITE_NEGATIVES_PIVOT', '97 individual graphs non-biplanar by checked DRAT; all-tested-leaf closure only, per S044 correction',
         'No live leaf and no witness; mixed-tree single-leaf implication unproved',
         2671.4050147533417, 'Includes estimated 900-second abandoned run; another failed start lacks separate CPU meter',
         'Registered gate failed; no exhaustive non-Ore generator'),
        ('S043', 'Order-3 layer-preserving 156-edge order-28 alpha<=3 slice',
         'UNKNOWN_PIVOT', 'Entire existence question UNKNOWN at 20000-cut cap; no DRAT exclusion',
         '10000 relaxation models; zero planar layers in them; one planar-layer control is not a pair',
         1026.703125, 'Driver CPU including encoding/controls; later portable replay separate',
         'Registered cut cap; no witness or <=40-I4 symmetric planar pair')]
    evidence = []
    for sid, domain, status, closure, gain, cpu, basis, stop in rows:
        evidence.append(dict(session=sid, domain=domain, status=status, exact_boundary=closure,
                             constructive_gain=gain, reported_cpu_seconds=cpu, cost_basis=basis, stop_reason=stop,
                             summary_path=f'validation/{sid}/SUMMARY.json'))
    frozen = [ROOT/f'sessions/S{n:03d}/{f}.md' for n in range(37,44) for f in ('CLOSEOUT','RESEARCH','ADVERSARIAL')]
    frozen += [ROOT/f'validation/S{n:03d}/MANIFEST.json' for n in range(37,44)]
    frozen += [ROOT/'validation/S043/RESULT.json', ROOT/'validation/S043/REGISTRATION.json']
    dump('validation/S044/EVIDENCE.json', dict(rows=evidence, reported_cpu_sum=sum(r['reported_cpu_seconds'] for r in evidence),
         cost_total_is_exact=False, sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen}))
    table = '# S044 evidence table — S037–S043\n\nHistorical reports, with fresh portable replay. No new research search. I4 means independent four-sets.\n\n'
    table += '| Session / tested domain | Exact closure and UNKNOWN boundary | Constructive gain | Reported CPU seconds / basis | Stop reason |\n|---|---|---|---|---|\n'
    for r in evidence:
        table += f"| {r['session']}: {r['domain']} | {r['exact_boundary']} | {r['constructive_gain']} | {r['reported_cpu_seconds']:.3f}; {r['cost_basis']} | {r['stop_reason']} |\n"
    table += '\nThe reported sum excludes separate acceptance/replays and some failures; it is not an exact campaign total or a matched efficiency comparison. The all-tested-leaf qualification supersedes the older arbitrary-one-leaf wording. See SCOPE_CORRECTION.md.\n'
    write('sessions/S044/EVIDENCE_TABLE.md', table)
    example = dict(initial_triangles=[[0,1,2],[3,4,5],[6,7,8]], joins=[dict(delete=[[0,1],[3,4]], identify=[0,3], add=[1,4]), dict(delete=[[0,2],[6,7]], identify=[0,6], add=[2,7])],
                   final_edges=[[0,5],[0,8],[1,2],[1,4],[2,7],[4,5],[7,8]], designated_leaf=[0,1,2], designated_edges_retained=[[1,2]],
                   scope='counterexample to retention of each designated leaf copy only; no global mixed-composite counterexample')
    dump('validation/S044/LEAF_SCOPE_CONTROL.json', example)
    claims = read('catalogue/CLAIMS.json')
    originals = [dict(c) for c in claims if c['id'] in ('CLM-0140','CLM-0141','CLM-0143')]
    replacements = {
        'CLM-0140': 'The three explicit S041 apex leaf graphs (K7-e) join C5, (K4-e) join Hajos(K6,K6), and (K3-e) join Hajos(K7,K7) are not biplanar. A graph containing any certified obstruction is excluded. Arbitrary iterated mixed compositions with only one tested leaf are not excluded by the recorded leaf-containment proof.',
        'CLM-0141': 'If K_a join H contains a surviving K_a join (L-e) with a certified non-biplanarity verdict, then K_a join H is non-biplanar. For iterated Step-One Hajos trees, testing every edge deletion for EVERY leaf is sufficient (CLM-0145); one tested leaf somewhere in an arbitrary mixed tree is not justified by the former proof.',
        'CLM-0143': 'All 97 S042 non-isomorphic apex leaf graphs from resolved types and PARTIAL 7-Ore/13 members are certified non-biplanar; 23514 choices reduce to these graphs. Their certificates are unchanged. Composition exclusions require a surviving obstruction or the all-tested-leaves hypothesis of CLM-0145; unresolved windows remain open.'}
    for c in claims:
        if c['id'] in replacements:
            c['claim'] = replacements[c['id']]
            c['notes'] += ' S044 scope correction: ancestors may delete further edges of an earlier leaf. The arbitrary-one-tested-leaf implication is not established by that proof. Original text retained in validation/S044/CORRECTIONS.json and frozen S041/S042 records.'
    new = dict(id='CLM-0145', status='PROGRAMME_PROVED', sources=['SRC-0002'],
               claim='For a Step-One Hajos tree of t>=2 leaf copies, some leaf loses at most one original edge, since at most 2t-2 original leaf edges are deleted. Thus if every K_a join (L-e) for EVERY leaf and edge is certified non-biplanar, K_a join H is non-biplanar. A specified leaf can lose more than one edge; one tested leaf in an arbitrary mixed tree is not covered by this proof.',
               notes='Written injectivity/provenance and deletion-count proof in sessions/S044/SCOPE_CORRECTION.md. Fixed three-triangle control checks the designated-copy issue only. No independent-set identification, general DHGO split, formalisation or global counterexample is claimed.')
    assert new['id'] not in {c['id'] for c in claims}
    dump('catalogue/CLAIMS.json', claims+[new])
    dump('validation/S044/CORRECTIONS.json', dict(original_claims=originals, replacements=replacements, new_claim=new['id'], finite_certificates_changed=False))
    append('catalogue/CLAIMS.md', '## S044 scope correction — CLM-0140, CLM-0141, CLM-0143\n\nHistorical sections above are superseded for the iterated-composition implication only.\n\n'+'\n\n'.join(k+': '+v for k,v in replacements.items())+'\n\nOriginal JSON entries: validation/S044/CORRECTIONS.json. All 97 individual certificates remain intact.')
    append('catalogue/CLAIMS.md', f"## {new['id']} — {new['status']}\n\n{new['claim']}\n\n{new['notes']}")
    sources = read('catalogue/SOURCES.json')
    for s in sources:
        if s['id'] in ('SRC-0002','SRC-0020','SRC-0065'):
            s['accessed'] = '2026-10-24'
            s['note'] += ' S044: limited primary refresh; scope and access described in sessions/S044/PRIOR_ART.md; no new unreviewed theorem imported.'
    new_sources = [dict(id='SRC-0066',title='Near-apex vertices and the integral gap of the Earth–Moon near-misses',authors='low_alpha_designer (rStation handle)',year=2026,publication_date='2026-10-15',url='https://rstation.ai/problems/earth_moon/papers/58',doi=None,access='ABSTRACT_INSPECTED',accessed='2026-10-24',note='v3 abstract inspected; reported near-apex experiments and certificates not replayed. Context only.'),
                   dict(id='SRC-0067',title='Two apices reduce chi=10 to doubly outerplanar chi=8',authors='selene_opus (rStation handle)',year=2026,publication_date='2026-10-08',url='https://rstation.ai/r/earth_moon/posts/77',doi=None,access='STATEMENT_INSPECTED',accessed='2026-10-24',note='Limited cone-chain discussion inspected; shared-apex and fresh-tight-source qualifications noted. Other results, code and review claims not adopted.')]
    assert not {s['id'] for s in sources} & {s['id'] for s in new_sources}
    dump('catalogue/SOURCES.json', sources+new_sources)
    append('catalogue/SOURCES.md', 'S044 primary refresh: SRC0002 Step-One/Step-Two definition re-inspected; SRC0020 abstract/metadata and SRC0065 current problem statement refreshed. SRC0051 direct refresh failed; F9 remains conjectural. No novelty claim. See sessions/S044/PRIOR_ART.md.')
    for s in new_sources:
        append('catalogue/SOURCES.md', f"## {s['id']} — {s['title']}\n\n{s['authors']}, {s['publication_date']}; {s['url']}; {s['access']}, accessed {s['accessed']}. {s['note']}")
    summary = dict(status='CLOSED_DECISION_AUDIT_RECOMMEND_PAUSE', recommendation='PAUSE', owner_decision='PENDING',
                   date='2026-10-24', entry_main='344014850e7909e661a1864f3726af664bcb2e71', new_search_experiments=0,
                   verification_job_cpu_seconds=verify['job_cpu_seconds'], verification_accounted_seconds=verify['cpu_upper_accounted'],
                   verification_cpu_cap=600, frozen_replays='PASS', fresh_smoke='PASS', fresh_97_proof_drat_replay=False,
                   scope_correction='ARBITRARY_ONE_TESTED_LEAF_IMPLICATION_UNPROVED; ALL_TESTED_LEAVES_SUFFICIENT',
                   witness=False, bounds=[9,12], S11='UNKNOWN', order3='UNKNOWN', S036_restarted=False,
                   computation='STOPPED', next_session='S045_FUTURE_UNEXECUTED')
    dump('validation/S044/SUMMARY.json', summary)
    state.update(last_completed_session='S044', recommended_next_session='S045', as_of='2026-10-24',
                 headline_status='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S044', source_status='S044_LIMITED_PRIMARY_REFRESH_NO_NOVELTY_CLAIM',
                 next_session_status='S045_QUEUED_FUTURE_UNEXECUTED', next_session_is_future_unexecuted=True,
                 current_computation='STOPPED', latest_session_branch='main', latest_session_entry_main=summary['entry_main'])
    state.pop('active_session', None)
    state['s044_queued']['status'] = 'EXECUTED_CLOSED_S044'
    state['s044_result'] = summary
    state['s045_queued'] = dict(status='FUTURE_UNEXECUTED',prompt='authoritative/NEXT_SESSION_PROMPT.md',archival_copy='sessions/S044/S045_FUTURE_PROMPT.md',objective='Owner decision and re-entry gate; preservation only unless a concrete direction is supplied; no experiment in S045',s036_restart_authorized=False)
    state['mathematical_results'].append(new['id'])
    state['latest_session_integration'] = dict(status='VERIFY_PUSHED_COMMIT_AND_HOSTED_JOB_AFTER_PUBLICATION',entry_main=summary['entry_main'],branch='main',force=False,authority='S044 existing-main prompt',verification='artifacts/tmp/S044/INTEGRATION.json and immutable hosted run in final report')
    state['open_obligations'][0] = 'S044 CLOSED: recommend PAUSE, owner decision PENDING. S045 decision/re-entry gate FUTURE/UNEXECUTED. S036 remains CLEAN_STOPPED.'
    state['open_obligations'][2] = 'All 97 individual S042 apex leaf graphs remain certified non-biplanar. Composition closure requires all leaves tested or an explicit surviving obstruction; arbitrary one-tested-leaf mixed-tree implication is unproved (S044 correction). Thirty non-Ore windows UNRESOLVED.'
    dump('authoritative/STATE.json', state)
    write('authoritative/NEXT_SESSION_PROMPT.md', (ROOT/'sessions/S044/S045_FUTURE_PROMPT.md').read_text(encoding='utf-8'))
    header = '# S044 CLOSED — decision audit recommends PAUSE (24 October 2026)\n\nOwner decision pending; no target change or new research run authorised.\nNo witness; 9<=chi_2<=12; order3 and nine S11 cases UNKNOWN. All 97\nindividual apex negatives stand; iterated composition needs all-tested-leaf\nor surviving-obstruction qualification (sessions/S044/SCOPE_CORRECTION.md).\nS036 stays stopped. S045 decision/re-entry gate FUTURE/UNEXECUTED. Existing\nmain, ordinary non-force commit/push, no branch/PR. Historical headers follow.\n\n'
    for p in ('AGENTS.md','authoritative/START_HERE.md'):
        write(p, header+(ROOT/p).read_text(encoding='utf-8'))
    report = 'S044 recommends PAUSE; owner decision pending. S037–S043 evidence audited; no new search, no witness, 9..12 unchanged. Hajós arbitrary-one-leaf implication narrowed; 97 individual negatives intact. S045 decision/re-entry gate FUTURE/UNEXECUTED.'
    for p,t in [('docs/SESSION_LEDGER.md','| S044 | 2026-10-24 | CAM0048 decision audit | '+report+' |'),('docs/DECISION_LOG.md',report),('docs/PHASE_GATE_LEDGER.md',report+' Phase1 remains OPEN; publication/Lean gates unchanged.'),('docs/FAILURE_LEDGER.md','S044 proof-scope finding: later Hajós joins can delete further edges of a designated earlier leaf. Frozen S041/S042 text preserved; live claims narrowed to surviving-obstruction/all-tested-leaf scope. This is a proof gap in the mixed-tree implication, not a counterexample to its conclusion.'),('campaigns/README.md','**CAM-0048 / '+report+'**')]:
        append(p,t)
    write('campaigns/CAM-0048.md','# CAM-0048 — S044 decision audit\n\n'+report+'\n\nVerification receipt: validation/S044/VERIFICATION.json. No scientific search. Recovery map and scope correction are in sessions/S044/.\n')
    print(report)


if __name__ == '__main__':
    main()
