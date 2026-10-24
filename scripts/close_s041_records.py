"""Close only S041 (comparative route audit) and queue S042; no scientific or process action."""
from pathlib import Path
from close_s037_records import read, write, dump, append

ROOT = Path(__file__).resolve().parents[1]


def main():
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] == 'S040' and state['recommended_next_session'] == 'S041'
    probes = read('validation/S041/PROBES.json')
    p3 = sum(r['seconds'] for r in read('validation/S041/P3_BIPLANARITY.json')['rows'])
    anneal = 6*45.02
    cegar = 0.6
    total = probes['total_cpu_seconds']+p3+anneal+cegar
    assert total < 1800 and not probes['witness_stop']
    leaves = read('validation/S041/P3B_LEAVES.json')+read('validation/S041/P4_LEAVES.json')
    assert all(r['verdict'] == 'NONBIPLANAR_DRAT_VERIFIED' for r in leaves)
    summary = dict(status='CLOSED_COMPARATIVE_ROUTE_AUDIT', date='2026-10-24',
                   entry_main='77a9f5e61732cc805160a489b213ca10b0686c38',
                   ranking=['R3 non-alpha joins/apex', 'R1 symmetry-first', 'R2 graph-first exact split', 'R4 S11 cells (parked)'],
                   probe_cpu_seconds=dict(p1_p2=probes['total_cpu_seconds'], p3=p3, p3b_p4_anneal=anneal, p3b_p4_cegar=cegar, total=total),
                   compute_cap_cpu_seconds=1800,
                   order13_class=dict(candidate_layers=50600, planar_layers=156, valid_pairs=3510, alpha3_pairs=0, min_independent_four_sets=767),
                   layer_preserving_odd_prime_orders_at_28=[3, 13],
                   counting_surviving_chi10_joins=['K1vH9 omega<=7', 'K2vH8 omega<=6', 'K3vH7 omega<=5 h<=16'],
                   mycielski_biplanar=False,
                   nonbiplanar_apex_leaf_graphs=[r['name'] for r in leaves],
                   witness=False, S11='UNKNOWN', bounds=[9, 12], S036_restarted=False,
                   all_processes_finished=True, next_session='S042_FUTURE_UNEXECUTED')
    dump('validation/S041/SUMMARY.json', summary)
    state.update(as_of='2026-10-24', last_completed_session='S041', recommended_next_session='S042',
                 headline_status='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S041',
                 source_status='S029_LANDSCAPE_FROZEN_PLUS_DATED_REFRESH_S041_NO_NOVELTY_CLAIM',
                 current_computation='STOPPED', next_session_status='S042_QUEUED_FUTURE_UNEXECUTED',
                 next_session_is_future_unexecuted=True, latest_session_branch='main',
                 latest_session_entry_main=summary['entry_main'])
    state.pop('active_session', None)
    state['s041_queued'].update(status='EXECUTED_CLOSED_S041')
    state['s041_result'] = summary
    state['s042_queued'] = dict(status='FUTURE_UNEXECUTED', installed_date='2026-10-24',
                               prompt='authoritative/NEXT_SESSION_PROMPT.md', archival_copy='sessions/S041/S042_FUTURE_PROMPT.md',
                               objective='R3: exact certified apex-leaf census for K1vH9, K2vH8, K3vH7 joins with a D077-style progress gate',
                               fallback_on_pivot='R1 exact layer-preserving Z3 class at order28 or a fresh audit',
                               s036_restart_authorized=False)
    state['latest_session_integration'] = dict(status='VERIFY_PUSHED_COMMIT_AND_HOSTED_JOB_AFTER_PUBLICATION',
                                              entry_main=summary['entry_main'], branch='main', force=False,
                                              authority='S041 existing-main prompt',
                                              verification='artifacts/tmp/S041/INTEGRATION.json and immutable run linked in final report')
    state['open_obligations'] = [
        'S041 CLOSED comparative route audit; ranking R3 > R1 > R2 > R4 (parked). S042 apex-leaf census FUTURE/UNEXECUTED, no automatic successor. S036 CLEAN_STOPPED.',
        'Order-13 layer-symmetric 156-edge order28 pairs completely classified: 3510 pairs, none alpha<=3 (best 767). Layer-preserving odd prime orders at order28 are only 3 and 13.',
        'Counting: Mycielski-type constructions never biplanar; only K1vH9, K2vH8, K3vH7 joins survive with omega(H)<=8-a. Apex leaf graphs of Sulanke, K3vHajos(K6,K6), K2vHajos(K7,K7) certified non-biplanar (K9-minor lemmas, DRAT).',
        'Star/patch/coordinated four-set hill-climbing remains PARKED (S040 D077 PIVOT). Counting routes carry the rStation F9 risk (chi_f<=9 conjecture, out of scope to prove).',
        'All247 historical S11 prefix closures follow sorting alone. Nine sorted prefixes UNKNOWN; S11 m155/156 UNKNOWN; regular154 SOURCE_STATED; S10/S9/S8 NOT_RUN;9<=chi2<=12; parked/Lean/publication gates unchanged.']
    new_claims = [
        dict(id='CLM-0137', status='PROGRAMME_PROVED', sources=['SRC-0048'],
             claim='If sigma != id of odd prime order p preserves a simple sphere triangulation, it fixes no edge, fixes a face only if p=3, and #fixed vertices + #invariant faces = 2. Hence a layer-preserving automorphism of odd prime order of a 156-edge 28-vertex biplanar pair has order 13 (exactly two fixed vertices) or 3 (exactly one fixed vertex).',
             notes='Proof in sessions/S041/RESEARCH.md from classical inputs (3-connectivity of triangulations, Whitney uniqueness, Lefschetz on S^2). Explains why fixed-point-free Z7 cannot preserve layers (cf. SRC-0048). Layer-swapping symmetries, involutions and 155-edge pairs not covered.'),
        dict(id='CLM-0138', status='COMPUTED_EXACT', sources=[],
             claim='Every 156-edge 28-vertex biplanar pair with a layer-preserving automorphism of order13 is among 3510 explicitly enumerated pairs of 156 certified planar invariant layers (from 50600 certified candidates); none has alpha<=3, and the minimum number of independent four-sets is767.',
             notes='Nonplanarity certified by failed necessary triangulation tests or stdlib-checked Kuratowski subdivisions, planarity by checked rotations; portable stdlib replay in CI. Uses CLM-0137 and a pair lemma. Not a statement about order3, involutions or non-symmetric graphs.'),
        dict(id='CLM-0139', status='PROGRAMME_PROVED', sources=['SRC-0011', 'SRC-0027'],
             claim='Conditional on the Kostochka-Yancey bound: no (generalized) Mycielskian of a 9-chromatic graph is biplanar, and a biplanar 10-chromatic join must be K1vH9, K2vH8 or K3vH7 (h<=16) with omega(H)<=8-a and apex budgets e(H)<=5h-6, 4h-1, 3h+3; for a Hajos-join H the apex case needs e(H)<=5h-7.',
             notes='Exact integer tables in validation/S041/P2_COUNTING.json; K4vH6/K5vH5 cases removed with Gallai join theorem (SRC-0027) and the classical 11-vertex triangle-free 4-chromatic minimum. Necessary conditions only, no construction.'),
        dict(id='CLM-0140', status='COMPUTED_EXACT', sources=['SRC-0002', 'SRC-0014'],
             claim='The graphs K5 v pentagonal bipyramid = (K7-e)vC5 (12 vertices, 60 edges), (K4-e)vHajos(K6,K6) (15, 78) and (K3-e)vHajos(K7,K7) (16, 82) are not biplanar. Hence no K1vH with H containing Sulanke K6vC5 minus at most one edge, and no apex-over-Hajos composite using leaves Sulanke, K3vHajos(K6,K6) or K2vHajos(K7,K7), is biplanar.',
             notes='S025 Lemma-B/C K9-minor CEGAR (CLM0090/0091; K9 premise CLM0022), pinned CaDiCaL DRAT verified by pinned drat-trim, every clause justified; zero Kuratowski lemmas needed. Plain Kuratowski CEGAR was UNKNOWN after 600 s. Hajos biplanarity is BGS prior art (SRC-0002).')]
    claims = read('catalogue/CLAIMS.json')
    assert not {c['id'] for c in claims} & {c['id'] for c in new_claims}
    dump('catalogue/CLAIMS.json', claims+new_claims)
    for c in new_claims:
        state['mathematical_results'].append(c['id'])
        append('catalogue/CLAIMS.md', f"## {c['id']} — {c['status']}\n\n{c['claim']}\n\n{c['notes']}")
    append('catalogue/SOURCES.md', 'S041 refresh24Oct2026: BGS part one excerpts confirm Hajos plus permuted layers give infinite 9-critical thickness-two families (SRC0002 grade unchanged); part two 17/25/33-vertex graphs not obtained (SRC0003 unchanged); Kostochka-Yancey statements re-seen (SRC0011/0020 unchanged). No reported chi>=10 biplanar graph. See sessions/S041/PRIOR_ART.md.')
    dump('authoritative/STATE.json', state)
    write('authoritative/NEXT_SESSION_PROMPT.md', (ROOT/'sessions/S041/S042_FUTURE_PROMPT.md').read_text(encoding='utf-8'))
    header = ('# S041 CLOSED — comparative route audit (24 October 2026)\n\n'
              'Ranking R3 non-alpha joins/apex > R1 symmetry > R2 graph-first > R4 (parked).\n'
              'Order-13 symmetric order28 pairs: none alpha<=3. Only K1vH9/K2vH8/K3vH7\n'
              'joins survive counting; three apex leaf graphs certified non-biplanar by\n'
              'K9-minor lemmas. No witness;9<=chi_2<=12. S036 stays stopped. S042 apex-\n'
              'leaf census is FUTURE/UNEXECUTED; read authoritative/NEXT_SESSION_PROMPT.md.\n'
              'Existing main, ordinary non-force commit/push, no branch/PR. Historical\n'
              'headers follow.\n\n')
    for path in ('AGENTS.md', 'authoritative/START_HERE.md'):
        write(path, header+(ROOT/path).read_text(encoding='utf-8'))
    write('campaigns/CAM-0045.md', (
        '# CAM-0045 — S041 comparative route audit, CLOSED\n\n'
        'Owner invocation `Run next session` (S041),24 October2026. Existing main, no branch/PR.\n'
        'Fresh full271+K9 smoke and frozen S037/S038/S040 replays PASS. Registration\n'
        'sessions/S041/PLAN.md plus hashed addenda P3, P3b, P4 before each probe.\n\n'
        'P1: order-13 layer-symmetric order28 class completely classified (3510 pairs,\n'
        'none alpha<=3, best767). P2: counting leaves only K1/K2/K3 apex joins.\n'
        'P3/P3b/P4: three apex leaf graphs certified non-biplanar by K9-minor CEGAR\n'
        'with DRAT. Ranking R3 > R1 > R2 > R4. Probe CPU about921 s of1800 s.\n'
        'S042 certified apex-leaf census FUTURE/UNEXECUTED.\n'))
    entries = [
        ('docs/SESSION_LEDGER.md', '| S041 |2026-10-24| CAM0045 comparative route audit | order-13 class empty (3510 pairs, best767); joins reduced to K1/K2/K3 apex; three apex leaves certified non-biplanar; ranking R3>R1>R2>R4; no witness| CLOSED; S042 FUTURE/UNEXECUTED |'),
        ('docs/PHASE_GATE_LEDGER.md', 'S041 CLOSED: CLM0137 symmetry orders lemma; CLM0138 order-13 classification; CLM0139 counting for joins/Mycielski; CLM0140 apex-leaf non-biplanarity. Phase1 NOT PASSED;9..12 unchanged. S042 FUTURE/UNEXECUTED; publication/Lean gates unchanged.'),
        ('docs/DECISION_LOG.md', 'S041 owner invocation24Oct2026 executes the D077 PIVOT audit. Decision: rank R3 non-alpha joins/apex first because its chi>=10 is certified by construction and avoids the chi_f>9 counting premise (F9 risk); queue S042 as an exact apex-leaf census with a D077-style gate; R1 order-3 symmetry is the fallback. Star/patch search and S11 cells stay parked. S042 not executed.'),
        ('docs/FAILURE_LEDGER.md', 'S041: order-13 symmetric pairs are far from alpha<=3 (best767). Plain Kuratowski CEGAR left K5 v bipyramid UNKNOWN at600 s; Lemma-B/C CEGAR decided it and two further leaf graphs non-biplanar in under a second each. The registered P1 certification scheme was revised before any probe ran (cost), with both hashes kept. Cover annealing plateaus are heuristic only.'),
        ('campaigns/README.md', '**CAM-0045 / S041 CLOSED:** comparative route audit. Order-13 symmetric order28 class empty (3510 pairs, best767); counting leaves K1/K2/K3 apex joins; Sulanke, K3vHajos(K6,K6), K2vHajos(K7,K7) apex leaves certified non-biplanar. Ranking R3>R1>R2>R4.9..12 unchanged; S042 apex-leaf census FUTURE/UNEXECUTED.')]
    for p, t in entries:
        append(p, t)
    print('S041 closeout installed; S042 NOT EXECUTED')


if __name__ == '__main__':
    main()
