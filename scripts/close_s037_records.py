"""Install S037 closeout authority; never launches computation or alters S036."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def write(p, text):
    (ROOT/p).write_text(text, encoding='utf-8', newline='\n')


def dump(p, data):
    write(p, json.dumps(data, indent=2)+'\n')


def append(p, text):
    old = (ROOT/p).read_text(encoding='utf-8')
    assert text.strip() not in old, 'closeout already installed: '+p
    write(p, old.rstrip()+'\n\n'+text.strip()+'\n')


def main():
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] == 'S036' and state['recommended_next_session'] == 'S037'
    summary = dict(status='CLOSED_BOUNDED_DISCOVERY_NO_WITNESS', date='2026-10-24',
                   entry_main='8e67c193bd09278872fba69a0106a92ce824a85f',
                   symmetry_theorem='ALL_247_CLOSED_PREFIXES_FOLLOW_FROM_SORTING_ALONE',
                   nine_unknown=[0, 1, 3, 7, 15, 31, 63, 127, 255],
                   best_violations={'155': 125, '156': 91}, checked_layer_records=19,
                   all_saved_pairs_have_checked_at_most_9_coloring=True,
                   experimental_cpu_seconds=44.625, nonextension_certificate_cpu_seconds=15.5625,
                   total_discovery_and_certificate_cpu_seconds=60.1875,
                   compute_cap_cpu_seconds=7200, single_flip_neighbors=43,
                   single_flip_minimum_neighbor_violations=93,
                   fixed_split_nonextension_examples=2, subdivision_certificates=446,
                   hitting_family_size=4821, hitting_relaxations='77_AND_78_EXPLICIT_NONPLANAR',
                   whole_stratum_certified=False, witness=False, bounds=[9, 12],
                   S036_restarted=False, fresh_historical_DRAT_replay=False,
                   next_session='S038_FUTURE_UNEXECUTED', all_experimental_processes_finished=True)
    dump('validation/S037/SUMMARY.json', summary)
    state.update(as_of='2026-10-24', last_completed_session='S037', recommended_next_session='S038',
                 headline_status='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S037',
                 next_session_status='S038_QUEUED_FUTURE_UNEXECUTED',
                 next_session_is_future_unexecuted=True, current_computation='STOPPED',
                 latest_session_branch='main', latest_session_entry_main=summary['entry_main'])
    state.pop('active_session', None)
    state['s037_queued']['status'] = 'EXECUTED_CLOSED_S037'
    state['s037_queued']['prompt'] = 'sessions/S036/S037_FUTURE_PROMPT.md'
    state['s037_result'] = summary
    state['s038_queued'] = dict(status='FUTURE_UNEXECUTED', installed_date='2026-10-24',
                               prompt='authoritative/NEXT_SESSION_PROMPT.md',
                               archival_copy='sessions/S037/S038_FUTURE_PROMPT.md',
                               objective='Nonextension-aware bounded planar face-patch repair',
                               s036_restart_authorized=False)
    state['latest_session_integration'] = dict(status='VERIFY_PUSHED_COMMIT_AND_HOSTED_JOB_AFTER_PUBLICATION',
                                              entry_main=summary['entry_main'], branch='main',
                                              authority='S037 explicit existing-main override', force=False,
                                              verification='artifacts/tmp/S037/INTEGRATION.json (local post-push receipt), plus immutable GitHub run linked in final report')
    state['open_obligations'] = [
        'S037 CLOSED bounded discovery. S036 remains CLEAN_STOPPED; no campaign process active. S038 is FUTURE/UNEXECUTED.',
        'S037 independently proves ALL 247 historical encoded closures follow from sorting alone. Nine sorted prefixes 0,1,3,7,15,31,63,127,255 remain UNKNOWN; 96.5% is not substantive closure progress.',
        'Best planar pairs: 91/125 independent four-sets at 156/155 edges; all saved pairs have checked <=9-colourings. No chi>=10 witness.',
        'S11 m155/156 UNKNOWN; regular154 SOURCE_STATED; S10/S9/S8 NOT_RUN. 9<=chi2<=12; parked/publication/Lean gates unchanged.',
        'S036 geometric archives preserved unchanged, private CDCL lost by design; historical closeout receipts retained.']
    for cid in ('CLM-0123', 'CLM-0124', 'CLM-0125'):
        assert cid not in state['mathematical_results']
        state['mathematical_results'].append(cid)
    dump('authoritative/STATE.json', state)
    prompt = (ROOT/'sessions/S037/S038_FUTURE_PROMPT.md').read_text(encoding='utf-8')
    write('authoritative/NEXT_SESSION_PROMPT.md', prompt)
    header = ('# S037 CLOSED — bounded structural reset (24 October 2026)\n\n'
              'All 247 historical closed prefixes follow from sorting alone; the nine\n'
              'sorted S11 prefixes remain UNKNOWN. Best checked planar pairs have 91/125\n'
              'independent four-sets at 156/155 edges and explicit <=9-colourings. No new\n'
              'witness; 9<=chi_2<=12. S036 remains stopped. S038 face-patch repair is\n'
              'FUTURE/UNEXECUTED; read authoritative/NEXT_SESSION_PROMPT.md. Existing\n'
              'main, ordinary non-force commit/push; no branch/PR. Historical headers follow.\n\n')
    for path in ('AGENTS.md', 'authoritative/START_HERE.md'):
        write(path, header+(ROOT/path).read_text(encoding='utf-8'))

    sources = read('catalogue/SOURCES.json')
    for source in sources:
        if source['id'] == 'SRC-0054':
            source['accessed'] = '2026-10-24'
            source['note'] += ' S037: primary post re-inspected; existing flip/tabu/relabel methodology acknowledged, numerical results not replayed. Strictly disjoint dense experiments are not directly comparable.'
    new_sources = [
        dict(id='SRC-0058', title='plantri and fullgen official page; Fast generation of planar graphs expanded paper',
             authors='Gunnar Brinkmann, Heidi Van den Camp and Brendan McKay (program page); Brinkmann and McKay (2007 paper)',
             year=2026, publication_date='2026-03-04 (plantri 5.8)', url='https://users.cecs.anu.edu.au/~bdm/plantri/',
             alternate_url='https://users.cecs.anu.edu.au/~bdm/papers/plantri-full.pdf', doi=None,
             access='STATEMENT_INSPECTED', accessed='2026-10-24',
             note='Official classes/version and paper abstract/sections 1.1-1.2 inspected. Program not built/run; no exhaustive generation or global connectivity claim used.'),
        dict(id='SRC-0059', title='Tight separators and common triangulation completions in biplanar graphs',
             authors='lunar_structure (rStation handle)', year=2026, publication_date='2026-10-06 (v2)',
             url='https://rstation.ai/problems/earth_moon/papers/11', doi=None,
             access='STATEMENT_INSPECTED', accessed='2026-10-24',
             note='Article text, deficit-one density/face argument and completion discussion inspected. Supplement not replayed; full paper claims and line-graph applications not adopted. S037 independently derives elementary near-triangulation fact.')]
    assert not set(s['id'] for s in sources) & set(s['id'] for s in new_sources)
    sources += new_sources
    dump('catalogue/SOURCES.json', sources)
    for s in new_sources:
        append('catalogue/SOURCES.md', f"## {s['id']} — {s['access']}\n\n{s['title']}. {s['authors']}. {s['publication_date']}. {s['url']}\n\n{s['note']}")
    append('catalogue/SOURCES.md', 'S037 refresh SRC-0054: primary post re-inspected 24 October 2026; flip/tabu/relabel prior art acknowledged, numerical reports not replayed. See sessions/S037/PRIOR_ART.md.')
    new_claims = [
        dict(id='CLM-0123', status='PROGRAMME_PROVED', sources=[],
             claim='For the actual sorted S11 encoding and registered eight-bit partition, exactly the nine prefixes 0,1,3,7,15,31,63,127,255 satisfy sorting alone; all 247 historical certified closed prefixes violate sorting.',
             notes='Tiny monotone-type proof plus independent exhaustive 65536 local assignments, full-eleven-position DP, all 16 type truth-table rows, frozen formula/mapping hash and exact historical certificate-ID comparison. tools/s037_symmetry.py; validation/S037/SYMMETRY.json. No fresh historical DRAT replay, graph exclusion or surviving S11 satisfiability decision.'),
        dict(id='CLM-0124', status='COMPUTED_EXACT', sources=['SRC-0054', 'SRC-0058'],
             claim='S037 preserved 19 independently checked saved planar-layer records (including duplicates), best 91/125 independent four-sets at 156/155 edges. Every saved pair has a checked proper colouring with at most nine colours.',
             notes='Explicit layers, sphere rotation certificates, direct 20475-four-set enumeration and colourings: validation/S037/PAIR_CHECKS.json. Discovery heuristics and capped permutation solves remain UNKNOWN. Nonplanar hitting relaxations are not witnesses. Source IDs attribute methods, not these computations; 9<=chi2<=12.'),
        dict(id='CLM-0125', status='COMPUTED_EXACT', sources=['SRC-0059'],
             claim='The explicit S037 91-violation pair has 43 admissible disjoint single flips, all with at least 93 violations. Two explicit 155-edge fixed layer splits admit no disjoint one-edge completion of their second layer, across all embeddings.',
             notes='Direct finite neighbor enumeration plus 446 explicit independently checked K5/K33 subdivisions covering all 223 absent pairs in each fixed split. validation/S037/STRUCTURE.json and NONEXTENSION.json. Elementary deficit-one/degree lemmas in RESEARCH.md; no novelty claimed. Does not exclude alternative repartitioning, larger patch moves, other graphs or a global witness.')]
    claims = read('catalogue/CLAIMS.json')
    assert not set(c['id'] for c in claims) & set(c['id'] for c in new_claims)
    dump('catalogue/CLAIMS.json', claims+new_claims)
    for c in new_claims:
        append('catalogue/CLAIMS.md', f"## {c['id']} — {c['status']}\n\n{c['claim']}\n\n{c['notes']}")
    for p, text in [
        ('docs/SESSION_LEDGER.md', '| S037 |2026-10-24| CAM0041 structural reset | sorting explains all247 historical closures; checked planar pairs best91/125 independent four-sets; strict local trap and446 nonextension subdivisions; no witness | CLOSED; S038 patch repair FUTURE/UNEXECUTED |'),
        ('docs/PHASE_GATE_LEDGER.md', 'S037 CLOSED: CLM-0123 sorted-prefix theorem, CLM-0124 checked planar records, CLM-0125 finite local/nonextension certificates. Phase1 NOT PASSED; 9..12 unchanged. S038 FUTURE/UNEXECUTED; all publication/Lean gates unchanged.'),
        ('docs/DECISION_LOG.md', 'S037 owner invocation 24Oct2026 adopts installed structural-reset prompt on existing main. Confirmed all247 closed prefixes are sorting bookkeeping. Next direction: bounded planar multi-edge patch repair, including nonextendible 77-edge layers. S036 stays stopped; S038 queued only.'),
        ('docs/FAILURE_LEDGER.md', 'S037: random kick arm3704 never packed (six overlaps); swap-only stagnation can freeze useful flips. Guided descent reaches strict single-flip traps. Fixed-template SAT adds4.85M clauses without improvement and caps UNKNOWN. Hitting SAT models fail planarity; preserve explicit subdivisions. A capped78 hitting solve is UNKNOWN although separate direct edge addition establishes relaxed78 feasibility. No witness or global negative conclusion.'),
        ('campaigns/README.md', '**CAM-0041 / S037 CLOSED bounded discovery:** all247 historical closures follow from sorting alone; best91/125 independent four-sets at156/155 edges; all saved pairs <=9-colourable; local trap/nonextension certificates. S038 patch repair FUTURE/UNEXECUTED; no S036 restart.')]:
        append(p, text)
    print('S037 closeout records installed; no successor executed')


if __name__ == '__main__':
    main()
