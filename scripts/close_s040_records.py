"""Close only S040 with the D077 PIVOT decision and queue S041; no scientific or process action."""
from pathlib import Path
from close_s037_records import read, write, dump, append

ROOT = Path(__file__).resolve().parents[1]


def main():
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] == 'S039' and state['recommended_next_session'] == 'S040'
    experiment = read('validation/S040/EXPERIMENT.json')
    posthoc = read('validation/S040/POSTHOC_SWAPS.json')['cpu_seconds']+read('validation/S040/POSTHOC_REPAIR.json')['cpu_seconds']
    assert experiment['status'] == 'FINISHED' and not experiment['witness_stop']
    total = experiment['experimental_cpu_seconds']+posthoc
    assert total < 7200
    arms = {r['name']: r['best_violations'] for r in read('validation/S040/arms/SUMMARY.json')}
    gate_b1 = all(arms[f'{d}-{s}-coord'] <= t for d, t in ((156, 41), (155, 39)) for s in (4000, 4001))
    gate_c = all(arms[f'protected-{s}-coord'] <= 39 for s in (4010, 4011))
    checks = read('validation/S040/PAIR_CHECKS.json')
    assert not gate_b1 and not gate_c and not checks['witness_found']
    summary = dict(status='CLOSED_D077_PIVOT_NO_SOLID_PROGRESS', date='2026-10-24',
                   entry_main='af53af4a85ad6207b22cd9f2220c52b7a2738036', d077_decision='PIVOT',
                   gate=dict(A_witness=False, B1_halving_all_coord_arms=False, C_protected_source=False,
                             thresholds={'156': 41, '155': 39, 'protected': 39}, registration='validation/S040/REGISTRATION.json'),
                   experimental_cpu_seconds=experiment['experimental_cpu_seconds'], posthoc_cpu_seconds=posthoc,
                   total_counted_cpu_seconds=total, compute_cap_cpu_seconds=7200,
                   exact_coordinated_neighborhoods={'156': dict(start=82, scored_states=216582, strict_improvements=0,
                                                                minima=dict(single=82, type0=89, type1=90, type2=96)),
                                                    '155': dict(start=79, scored_states=119281, strict_improvements=0,
                                                                minima=dict(single=80, type0=83, type1=88, type2=79))},
                   arm_bests=arms, tau_exact={'156': 5, '155': 7}, tau_k9_safe_exact={'156': 17, '155': 11},
                   occupancy_blocked_useful_pairs={'156': 2, '155': 5}, alpha3_repairs_contain_K10=True,
                   checked_saved_records=checks['records'], replayed_transitions=482,
                   all_saved_pairs_have_checked_at_most_9_coloring=True, witness=False,
                   heuristic_verdict='UNKNOWN', whole_stratum_certified=False, S11='UNKNOWN', bounds=[9, 12],
                   S036_restarted=False, all_experimental_processes_finished=True,
                   parked='star/patch/coordinated four-set hill-climbing', next_session='S041_FUTURE_UNEXECUTED')
    dump('validation/S040/SUMMARY.json', summary)
    state.update(as_of='2026-10-24', last_completed_session='S040', recommended_next_session='S041',
                 headline_status='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S040',
                 source_status='S029_LANDSCAPE_FROZEN_PLUS_DATED_REFRESH_S040_NO_NOVELTY_CLAIM',
                 current_computation='STOPPED', next_session_status='S041_QUEUED_FUTURE_UNEXECUTED',
                 next_session_is_future_unexecuted=True, latest_session_branch='main',
                 latest_session_entry_main=summary['entry_main'])
    state.pop('active_session', None)
    state['s040_queued'].update(status='EXECUTED_CLOSED_S040_PIVOT')
    state['s040_result'] = summary
    state['s041_queued'] = dict(status='FUTURE_UNEXECUTED', installed_date='2026-10-24',
                               prompt='authoritative/NEXT_SESSION_PROMPT.md', archival_copy='sessions/S040/S041_FUTURE_PROMPT.md',
                               objective='D077 PIVOT: comparative audit of at least two genuinely different chi>=10 construction routes (symmetry-first, graph-first exact split, non-alpha compositions); S042 prompt with its own progress gate',
                               parked='star/patch/coordinated four-set hill-climbing', s036_restart_authorized=False)
    state['latest_session_integration'] = dict(status='VERIFY_PUSHED_COMMIT_AND_HOSTED_JOB_AFTER_PUBLICATION',
                                              entry_main=summary['entry_main'], branch='main', force=False,
                                              authority='S040 existing-main prompt (D077 revision)',
                                              verification='artifacts/tmp/S040/INTEGRATION.json and immutable run linked in final report')
    state['open_obligations'] = [
        'S040 CLOSED with D077 decision PIVOT. All experiments finished; S036 CLEAN_STOPPED. S041 comparative route audit FUTURE/UNEXECUTED, no automatic successor.',
        'Exact coordinated one-star-per-layer neighborhoods at82/79: 216582/119281 scored states, no strict improvement; matched arms no improvement; protected193->192. Star/patch/coordinated four-set hill-climbing PARKED.',
        'Diagnostics: tau5/7 exact, occupancy not binding; post-hoc hub pairs complete K9/K10, tau_safe17/11 exact; label-fixed alpha3 repairs contain K10. Diagnostic learning only.',
        'All saved S040 pairs <=9-colourable; no chi10 witness. Closed through17 Sulanke-core ranges unchanged.',
        'All247 historical S11 prefix closures follow sorting alone. Nine sorted prefixes UNKNOWN; S11 m155/156 UNKNOWN; regular154 SOURCE_STATED; S10/S9/S8 NOT_RUN;9<=chi2<=12; parked/Lean/publication gates unchanged.']
    new_claims = [
        dict(id='CLM-0133', status='PROGRAMME_PROVED', sources=['SRC-0060'],
             claim='For single-layer components a (layer0) and b (layer1) that each keep their own layer a simple sphere map, the final layers are edge-disjoint iff C_a<=R_b, C_b<=R_a and A_a,A_b are disjoint, where C=A meets the other layer. Type1 pairs (one C empty) are two-step sequential S039 paths; type2 pairs (both nonempty) are not two-step compositions of their components.',
             notes='Set identity L0\'&L1\'=(C_b-R_a)|(C_a-R_b)|(A_a&A_b); proof in sessions/S040/RESEARCH.md. Controlled on full cartesian products (14.6M pairs) and by per-move replay. SRC0060 is related simultaneous-flip context only, not the proof.'),
        dict(id='CLM-0134', status='COMPUTED_EXACT', sources=[],
             claim='At the S039 bests (82 independent four-sets at156 edges, 79 at155), the registered degree3..6 one-star-per-layer coordinated neighborhoods, including S039-legal singles, have216582/119281 exactly scored states and no strict improvement; minima single/type0/type1/type2 are82/89/90/96 and80/83/88/79.',
             notes='Independent chord-subset regeneration over the full cartesian product with delta scoring and with OR masks reproduces both canonical table hashes. Fixed embeddings and the registered family only; coordinated flips/patches, multi-star moves and other embeddings unsearched.'),
        dict(id='CLM-0135', status='COMPUTED_EXACT', sources=[],
             claim='S040 matched arms (12 unprotected, 4 protected; caps150 CPU s, plateau30) end at their starts82/79 except protected coord seed4010 (193->192). The registered D077 criteria (A) witness, (B) halving to <=41/<=39 in all four coord arms, (C) protected <=39 all fail: decision PIVOT. All24 saved records have checked <=9-colourings.',
             notes='482 transitions, sphere rotations, all20475 four-sets and colourings independently replayed; protected bests keep the Sulanke core (exact chi9). Two seeds and early plateaus give no statistical or global statement. Heuristic verdict UNKNOWN.'),
        dict(id='CLM-0136', status='COMPUTED_EXACT', sources=['SRC-0014'],
             claim='At the S040 inputs the independent-four-set hitting number is exactly5 (156) and7 (155); every four-set has a pair addable by an S039-legal single move, and only2/5 useful pairs need relaxed pairs. Post-hoc, the minimum hitting sets complete K10 from omega8 unions, the K9-safe hitting number is exactly17/11, and that safe set still forms K9/K10; label-fixed alpha<=3 repairs within edit distance10/13 contain K10.',
             notes='Packings and hitting sets checked in code; K9 non-biplanarity inherited (CLM0022/SRC0014). Label-fixed statements only, not about relabelled or arbitrary graphs. Post-hoc items registered in PLAN_ADDENDUM.md after the gate; explanatory learning, no construction or biplanarity claim.')]
    claims = read('catalogue/CLAIMS.json')
    assert not {c['id'] for c in claims} & {c['id'] for c in new_claims}
    sources = read('catalogue/SOURCES.json')
    new_sources = [
        dict(id='SRC-0062', title='earth_moon_small_order: computer-assisted proof of nine-colorability for biplanar graphs on at most 18 vertices',
             authors='EpsilonPhoenix (GitHub handle)', year=2026, publication_date='2026-09-19',
             url='https://github.com/EpsilonPhoenix/earth_moon_small_order', doi=None, access='STATEMENT_INSPECTED', accessed='2026-10-24',
             note='README statements only: claims order<=18 biplanar graphs are9-colourable; Lean part is partial with unproved reduction/finite-case hypotheses. Unreviewed; not replayed. Closed-range context for S041.'),
        dict(id='SRC-0063', title='earth-moon-alpha2: small-order results on the independence-number-2 route',
             authors='ivanspog (GitHub handle)', year=2026, publication_date='2026-10-03',
             url='https://github.com/ivanspog/earth-moon-alpha2', doi='10.5281/zenodo.22242268', access='STATEMENT_INSPECTED', accessed='2026-10-24',
             note='README statements only (pushed2026-10-03; Zenodo DOI as stated there, not resolved): alpha<=2 reductions, odd-cycle inflation cases and non-biplanarity claims of mixed certificate status. Not replayed; alpha<=2 is covered at theorem level by SRC-0037. Context for S041.')]
    assert not {s['id'] for s in sources} & {s['id'] for s in new_sources}
    dump('catalogue/SOURCES.json', sources+new_sources)
    for s in new_sources:
        append('catalogue/SOURCES.md', f"## {s['id']} — {s['access']}\n\n{s['authors']}, *{s['title']}*, {s['publication_date']}, {s['url']} (accessed24 October2026).\n\n{s['note']}")
    append('catalogue/SOURCES.md', 'S040 refresh24Oct2026: no reported chi>=10 biplanar graph found; SRC0004/0035/0037 grades unchanged; rStation post list not rendered, newer posts not re-read. See sessions/S040/PRIOR_ART.md.')
    dump('catalogue/CLAIMS.json', claims+new_claims)
    for c in new_claims:
        state['mathematical_results'].append(c['id'])
        append('catalogue/CLAIMS.md', f"## {c['id']} — {c['status']}\n\n{c['claim']}\n\n{c['notes']}")
    dump('authoritative/STATE.json', state)
    write('authoritative/NEXT_SESSION_PROMPT.md', (ROOT/'sessions/S040/S041_FUTURE_PROMPT.md').read_text(encoding='utf-8'))
    header = ('# S040 CLOSED — D077 decision PIVOT (24 October 2026)\n\n'
              'Coordinated two-layer stars gave no strict improvement at82/79 (exact\n'
              'neighborhoods, matched arms); the registered progress gate failed. Star/\n'
              'patch/coordinated four-set hill-climbing is PARKED. Diagnostic: residual\n'
              'four-sets sit on K9/K10-completing pairs. No witness;9<=chi_2<=12. S036\n'
              'stays stopped. S041 comparative route audit is FUTURE/UNEXECUTED; read\n'
              'authoritative/NEXT_SESSION_PROMPT.md. Existing main, ordinary non-force\n'
              'commit/push, no branch/PR. Historical headers follow.\n\n')
    for path in ('AGENTS.md', 'authoritative/START_HERE.md'):
        write(path, header+(ROOT/path).read_text(encoding='utf-8'))
    write('campaigns/CAM-0044.md', (
        '# CAM-0044 — S040 coordinated two-layer stars, CLOSED PIVOT\n\n'
        'Owner invocation `run s04p` (S040),24 October2026. Existing main, no branch/PR.\n'
        'Fresh full271+K9 smoke and frozen S037/S038/S039 replays PASS before science.\n'
        'Registration sessions/S040/PLAN.md with the D077 gate, hashed before results.\n\n'
        'Exact one-star-per-layer coordinated neighborhoods at82/79: 216582/119281\n'
        'scored states, no strict improvement. Twelve matched unprotected arms and four\n'
        'protected arms: no improvement except protected193->192. Gate (A)/(B)/(C)\n'
        'fail: PIVOT. tau5/7 exact; occupancy not binding; post-hoc hub pairs complete\n'
        'K9/K10, tau_safe17/11 exact. All24 saved records <=9-colourable; no witness.\n\n'
        'Experimental CPU315.15625 s plus post-hoc31.90625 s; controls/replay separate.\n'
        'One process, finished. S041 comparative route audit FUTURE/UNEXECUTED.\n'))
    entries = [
        ('docs/SESSION_LEDGER.md', '| S040 |2026-10-24| CAM0044 coordinated two-layer stars, D077 gate |335863 exactly scored coordinated states, no strict improvement; 16 arms, 482 replays; tau5/7, K9 barrier; all saved <=9-colourable; no witness| CLOSED PIVOT; S041 FUTURE/UNEXECUTED |'),
        ('docs/PHASE_GATE_LEDGER.md', 'S040 CLOSED PIVOT: CLM0133 compatibility lemma; CLM0134 exact coordinated neighborhoods; CLM0135 arms and failed D077 gate; CLM0136 tau/K9-barrier diagnostics. Phase1 NOT PASSED;9..12 unchanged. S041 FUTURE/UNEXECUTED; publication/Lean gates unchanged.'),
        ('docs/DECISION_LOG.md', 'S040 owner invocation24Oct2026 (`run s04p`) executes the D077-revised prompt. Registered gate failed: no strict improvement in exact coordinated neighborhoods or matched arms. D077 decision PIVOT: park star/patch/coordinated four-set hill-climbing; queue S041 comparative audit of at least two genuinely different routes. S041 not executed.'),
        ('docs/FAILURE_LEDGER.md', 'S040: coordinated one-star-per-layer moves found no strict improvement at82/79; all matched arms plateaued at their starts (protected193->192). Occupancy relaxation targeted a non-binding obstacle; residual four-sets sit on K9/K10-completing pairs. First pair validation passed an unsupported CaDiCaL flag (-t), six attempts UNKNOWN, rerun with subprocess timeout before records were kept. Fixed-embedding family results only, not global exclusions.'),
        ('campaigns/README.md', '**CAM-0044 / S040 CLOSED PIVOT:** exact coordinated two-layer star neighborhoods (335863 scored states) and16 matched arms give no strict improvement at82/79; D077 gate failed. tau5/7, hub pairs complete K9/K10 (tau_safe17/11). All24 saved records <=9-colourable.9..12 unchanged; S041 comparative route audit FUTURE/UNEXECUTED.')]
    for p, t in entries:
        append(p, t)
    print('S040 closeout installed with D077 PIVOT; S041 NOT EXECUTED')


if __name__ == '__main__':
    main()
