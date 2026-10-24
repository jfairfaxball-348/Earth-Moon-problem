"""Close only S042 (apex-leaf census, PIVOT) and queue S043; no scientific or process action."""
from pathlib import Path
from close_s037_records import read, write, dump, append

ROOT = Path(__file__).resolve().parents[1]


def main():
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] == 'S041' and state['recommended_next_session'] == 'S042'
    dec = read('validation/S042/DECISIONS.json')
    leaves = read('validation/S042/LEAF_GRAPHS.json')
    types = read('validation/S042/CENSUS_TYPES.json')
    assert all(d['verdict'] == 'NONBIPLANAR_DRAT_VERIFIED' for d in dec['decisions']) and dec['cpu_seconds_total'] < 3600
    replays = [read(f'validation/S042/{f}') for f in ('LEAF_REPLAY.json', 'LEAF_REPLAY_STRONG.json') if (ROOT/'validation/S042'/f).exists()]
    assert replays and all(r['status'] == 'PASS' for r in replays) and read('validation/S042/LOCAL_VERIFY.json')['status'] == 'PASS'
    summary = dict(status='CLOSED_APEX_LEAF_CENSUS_PIVOT', date='2026-10-24',
                   entry_main='ef06ec59a6f545e146b00f18101c3da03da545c5', gate_decision='PIVOT',
                   gate=dict(A_witness=False, B_live_leaf=False),
                   census_types=len(types), resolved_types=sum(r['resolved'] for r in types),
                   unresolved_types=sum(not r['resolved'] for r in types),
                   considered_leaf_choices=leaves['considered_leaf_pairs'], leaf_graphs=len(leaves['leaf_graphs']),
                   nonbiplanar_drat_verified=len(dec['decisions']), ore_counts=leaves['ore_counts'],
                   experimental_cpu_seconds=dec['cpu_seconds_total'], compute_cap_cpu_seconds=3600,
                   archive_policy='edges and DRAT committed; CNF/lemmas local, deterministic, SHA-256 pinned',
                   witness=False, S11='UNKNOWN', bounds=[9, 12], S036_restarted=False,
                   all_processes_finished=True, next_session='S043_FUTURE_UNEXECUTED')
    dump('validation/S042/SUMMARY.json', summary)
    state.update(as_of='2026-10-24', last_completed_session='S042', recommended_next_session='S043',
                 headline_status='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S042',
                 source_status='S029_LANDSCAPE_FROZEN_PLUS_DATED_REFRESH_S042_NO_NOVELTY_CLAIM',
                 current_computation='STOPPED', next_session_status='S043_QUEUED_FUTURE_UNEXECUTED',
                 next_session_is_future_unexecuted=True, latest_session_branch='main',
                 latest_session_entry_main=summary['entry_main'])
    state.pop('active_session', None)
    state['s042_queued'].update(status='EXECUTED_CLOSED_S042_PIVOT')
    state['s042_result'] = summary
    state['s043_queued'] = dict(status='FUTURE_UNEXECUTED', installed_date='2026-10-24',
                               prompt='authoritative/NEXT_SESSION_PROMPT.md', archival_copy='sessions/S042/S043_FUTURE_PROMPT.md',
                               objective='R1: exact decision of 156-edge order28 biplanar pairs with a layer-preserving order-3 automorphism, D077-style gate; PIVOT leads to an owner-decision audit',
                               s036_restart_authorized=False)
    state['latest_session_integration'] = dict(status='VERIFY_PUSHED_COMMIT_AND_HOSTED_JOB_AFTER_PUBLICATION',
                                              entry_main=summary['entry_main'], branch='main', force=False,
                                              authority='S042 existing-main prompt',
                                              verification='artifacts/tmp/S042/INTEGRATION.json and immutable run linked in final report')
    state['open_obligations'] = [
        'S042 CLOSED apex-leaf census, decision PIVOT. S043 order-3 symmetric class FUTURE/UNEXECUTED, no automatic successor. S036 CLEAN_STOPPED.',
        'All 97 resolved-domain apex leaf graphs (C5, 6-Ore/11, 7-Ore/19; PARTIAL 7-Ore/13) certified non-biplanar by K9-minor CEGAR with DRAT; apex-over-Hajos from these leaves closed. Thirty non-Ore windows UNRESOLVED.',
        'Order-13 layer-symmetric class empty (S041). Star/patch/coordinated four-set hill-climbing parked (S040). Counting routes carry the F9 risk.',
        'All247 historical S11 prefix closures follow sorting alone. Nine sorted prefixes UNKNOWN; S11 m155/156 UNKNOWN; regular154 SOURCE_STATED; S10/S9/S8 NOT_RUN;9<=chi2<=12; parked/Lean/publication gates unchanged.']
    new_claims = [
        dict(id='CLM-0141', status='PROGRAMME_PROVED', sources=['SRC-0002'],
             claim='If H is a Hajos composite of (10-a)-critical graphs (a=1,2,3) and some composition leaf L has every census leaf graph K_av(L-e) non-biplanar, then K_avH is not biplanar: each e gives a K9, an Euler-infeasible K_av(L-e), or a census leaf graph contained in K_avH.',
             notes='Proof in sessions/S042/RESEARCH.md. Covers Hajos composites and edge-deleted DHGO operands only; vertex-split operands are not covered.'),
        dict(id='CLM-0142', status='PROGRAMME_PROVED', sources=['SRC-0011', 'SRC-0020', 'SRC-0027'],
             claim='For apex leaves on at most 21 vertices exactly 45 (a,c,factor) types meet the leaf budget: 15 resolved (odd cycle C5, 6-Ore on 11, 7-Ore on 19, empty 7-critical orders 17-18) and 30 unresolved non-Ore windows (9-critical 17-21, 8-critical 15-21, 7-critical 13-16 vertices).',
             notes='Gallai join decomposition, Kostochka-Yancey bound with equality iff k-Ore and the non-Ore bound of SRC-0020 Theorem 6 (statement-level). Table independently re-derived by separately written stdlib code.'),
        dict(id='CLM-0143', status='COMPUTED_EXACT', sources=['SRC-0014'],
             claim='All 97 non-isomorphic apex leaf graphs from the resolved types (plus PARTIAL 7-Ore/13 members) are not biplanar; 23514 (a,L,e) choices reduce to them. Hence no apex-over-Hajos composite with a leaf of these types is biplanar.',
             notes='Lemma-B/C CEGAR (CLM0090/0091; K9 premise CLM0022), pinned DRAT verified by pinned drat-trim, every clause re-justified; independent VF2 replay; CNFs regenerate byte-identically and the committed DRAT re-verifies. Unresolved windows not excluded.')]
    claims = read('catalogue/CLAIMS.json')
    assert not {c['id'] for c in claims} & {c['id'] for c in new_claims}
    dump('catalogue/CLAIMS.json', claims+new_claims)
    for c in new_claims:
        state['mathematical_results'].append(c['id'])
        append('catalogue/CLAIMS.md', f"## {c['id']} — {c['status']}\n\n{c['claim']}\n\n{c['notes']}")
    sources = read('catalogue/SOURCES.json')
    for s in sources:
        if s['id'] == 'SRC-0020':
            s['access'] = 'STATEMENT_INSPECTED'
            s['note'] = (s.get('note') or '')+' S042: ar5iv full text read at statement level: Theorem 6 (k-critical meets KY bound iff k-Ore; non-Ore bound with y_k=max{2k-6,k^2-5k+2}); DHGO definition of k-Ore. Proofs not read.'
    dump('catalogue/SOURCES.json', sources)
    append('catalogue/SOURCES.md', 'S042 refresh24Oct2026: SRC-0020 upgraded to STATEMENT_INSPECTED (Theorem 6 via ar5iv). BGS part one preprint text re-read: 40 9-critical thickness-two graphs on 12-16 vertices (joins by Gallai). Part two graphs not obtained. See sessions/S042/PRIOR_ART.md.')
    dump('authoritative/STATE.json', state)
    write('authoritative/NEXT_SESSION_PROMPT.md', (ROOT/'sessions/S042/S043_FUTURE_PROMPT.md').read_text(encoding='utf-8'))
    header = ('# S042 CLOSED — apex-leaf census, decision PIVOT (24 October 2026)\n\n'
              'All 97 resolved-domain apex leaf graphs are certified non-biplanar by\n'
              'K9-minor lemmas (DRAT); apex-over-Hajos from odd-cycle/6-Ore/7-Ore leaves is\n'
              'closed; thirty non-Ore windows UNRESOLVED. No witness;9<=chi_2<=12. S036\n'
              'stays stopped. S043 order-3 symmetric class is FUTURE/UNEXECUTED; read\n'
              'authoritative/NEXT_SESSION_PROMPT.md. Existing main, ordinary non-force\n'
              'commit/push, no branch/PR. Historical headers follow.\n\n')
    for path in ('AGENTS.md', 'authoritative/START_HERE.md'):
        write(path, header+(ROOT/path).read_text(encoding='utf-8'))
    write('campaigns/CAM-0046.md', (
        '# CAM-0046 — S042 apex-leaf census, CLOSED PIVOT\n\n'
        'Owner invocation (`Yes`, `Run s042`),24 October2026. Existing main, no branch/PR.\n'
        'Fresh full271+K9 smoke and frozen replays PASS. Registration sessions/S042/PLAN.md\n'
        'plus hashed addendum before leaf output.\n\n'
        '45 leaf types (15 resolved, 30 unresolved non-Ore windows); 23514 choices give 97\n'
        'leaf graphs; all certified non-biplanar by K9-minor CEGAR with DRAT. Gate: PIVOT.\n'
        'Experimental CPU2671.4 s of3600. S043 order-3 symmetric class FUTURE/UNEXECUTED.\n'))
    entries = [
        ('docs/SESSION_LEDGER.md', '| S042 |2026-10-24| CAM0046 certified apex-leaf census | 97 leaf graphs all non-biplanar (K9-minor CEGAR, DRAT); 30 non-Ore windows unresolved; no witness| CLOSED PIVOT; S043 FUTURE/UNEXECUTED |'),
        ('docs/PHASE_GATE_LEDGER.md', 'S042 CLOSED PIVOT: CLM0141 leaf lemma; CLM0142 census type reduction; CLM0143 97 leaf graphs non-biplanar. Phase1 NOT PASSED;9..12 unchanged. S043 FUTURE/UNEXECUTED; publication/Lean gates unchanged.'),
        ('docs/DECISION_LOG.md', 'S042 owner invocation24Oct2026. Registered gate failed (no live apex leaf). Decision PIVOT: park R3 apex-over-Hajos search; queue S043 as the exact order-3 layer-symmetric class (R1), whose own PIVOT leads to an owner-decision audit rather than further slices. S043 not executed.'),
        ('docs/FAILURE_LEDGER.md', 'S042: every resolved apex leaf graph dies by cross-layer K9-minor lemmas. First census run stopped for redundant generation (about900 CPU s counted); two restarts failed immediately (escaping, node labels). Certificate archive exceeded repository scale; CNF/lemma files moved local and hash-pinned after byte-identical regeneration was confirmed.'),
        ('campaigns/README.md', '**CAM-0046 / S042 CLOSED PIVOT:** certified apex-leaf census. 45 types, 97 leaf graphs, all non-biplanar by K9-minor CEGAR with DRAT; 30 non-Ore windows unresolved.9..12 unchanged; S043 order-3 symmetric class FUTURE/UNEXECUTED.')]
    for p, t in entries:
        append(p, t)
    print('S042 closeout installed with PIVOT; S043 NOT EXECUTED')


if __name__ == '__main__':
    main()
