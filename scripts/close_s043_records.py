"""Install S043 records after bounded search/replay; performs no process action."""
import gzip
import hashlib
import json
from pathlib import Path

from close_s037_records import read, write, dump, append

ROOT = Path(__file__).resolve().parents[1]


def main():
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] == 'S042' and state['recommended_next_session'] == 'S043'
    result = read('validation/S043/RESULT.json')
    replay = read('validation/S043/REPLAY.json')
    assert replay['status'] == 'PASS' and replay['all_clauses_rejustified']
    assert result['verdict'] == 'UNKNOWN' or result['verdict'].startswith('UNSAT_DRAT_VERIFIED')
    assert result['gate_decision'] == 'PIVOT'
    summary = dict(status='CLOSED_Z3_BOUNDED_UNKNOWN_PIVOT' if result['verdict'] == 'UNKNOWN' else 'CLOSED_Z3_CERTIFIED_EXCLUSION_PIVOT',
                   date='2026-10-24', entry_main='7f01c8b57177af18b73d7e455469f04104ceb060',
                   gate_decision='PIVOT', gate=dict(A_witness=False, B_pair_at_most_40=False),
                   verdict=result['verdict'], reason=result['reason'],
                   models=result['models'], checked_subdivision_cuts=result['cuts'],
                   planar_layers_seen=result['planar_layers'],
                   experimental_cpu_seconds=result['cpu_seconds'], experimental_wall_seconds=result['wall_seconds'],
                   compute_cap_cpu_seconds=2400, owner_ceiling_cpu_seconds=7200,
                   whole_slice_certified=result['whole_slice_certified'],
                   clauses_independently_rejustified=True, replay_cpu_seconds=replay['cpu_seconds'],
                   witness=False, S11='UNKNOWN', bounds=[9, 12], S036_restarted=False,
                   all_processes_finished=True, next_session='S044_FUTURE_UNEXECUTED')
    dump('validation/S043/SUMMARY.json', summary)
    stop_detail = ('registered20000-cut cap' if result['cuts'] >= 20000 else result['reason'])
    conclusion = ('The entire order3 slice remains UNKNOWN; this run supplies no certified exclusion.'
                  if result['verdict'] == 'UNKNOWN' else 'The registered order3 slice is certified excluded.')
    closeout = f'''# S043 CLOSED — order3 symmetric slice, decision PIVOT

24 October2026. Verdict **{result['verdict']}**, stopped at {stop_detail}.
No chi>=10 witness;9<=chi_2<=12. {conclusion}
The fixed progress gate failed: neither a certified witness nor a checked
156-edge symmetric pair with<=40 independent four-sets. S044 is queued only
as the short owner-decision audit, FUTURE/UNEXECUTED. S036 remains stopped.

Results: {result['models']} alpha<=3 relaxation models processed,
{result['cuts']} independently justified Kuratowski orbit-support cuts;
{result['planar_layers']} planar layers among those models. No planar pair
was saved. One explicit symmetric78-edge planar layer is a control only.
Search CPU{result['cpu_seconds']:.3f}s, wall{result['wall_seconds']:.3f}s;
search limits1800 CPU s/3600 wall s/20000 cuts, total experimental cap2400
CPU s including any native certification, below the owner's7200 ceiling.
The observed interrupted solve count is{result['calls']-result['models']}
when no UNSAT call occurred; interrupted calls supply no mathematical result.

CLM0144 gives the orbit reduction and sound symmetry breaking. The separate
stdlib checker reconstructs all36200 base clauses (12073 variables), checks
every one of20475 four-sets, the threshold-counter semantics and17 generator
inequalities, then independently traces all subdivision branch paths.
Cut kinds: {json.dumps(replay['kinds'], sort_keys=True)}.
No projection count or percentage of excluded graphs is established.

Acceptance: fresh full271+K9 smoke PASS, all271 chromatic proofs and CNF
hashes checked; retained and fresh native K9 proofs verified. Frozen
S037–S042 replays PASS at entry. S043 corruption controls and full independent
CNF/subdivision replay PASS ({replay['cpu_seconds']:.3f} CPU s for final replay).
No fresh DRAT proof of this capped search is claimed. Native tool hashes,
installed packages and historical source pins: ENVIRONMENT.json and SMOKE.json.

Retained permanent evidence in validation/S043: registered plan/source
hashes, full base/final CNF gzip archives, all cut edges and exact clauses,
encoding, positive control with rotation, result/replay/summary and manifest.
This preserves semantic clauses, not private CDCL state. Search finished;
no process is left running and no next session was executed.

Reproduce verification, not the experiment, from repository root:
`.venv/Scripts/python.exe scripts/check_s043_adversarial.py` then
`.venv/Scripts/python.exe scripts/check_s043_records.py` (stdlib; CI uses
`python`). S043 research/plan explain exactly what was tested and why caps
remain UNKNOWN. Result-specific primary sources were refreshed; no novelty claim.

Entry main7f01c8b57177af18b73d7e455469f04104ceb060, tree
d3f1ddb3516de2a0e9466a6961afad6189dfb64f, sole parent
ef06ec59a6f545e146b00f18101c3da03da545c5. S042 actual hosted
[run40104278114](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/40104278114)
and job120902607015 succeeded. Publish one ordinary commit/push on main;
no PR/merge per the session prompt. Final SHA/tree/parent and actual hosted
job are verified after publication in artifacts/tmp/S043/INTEGRATION.json
and the user-visible closeout. Hosted receipt checks do not constitute DRAT.

The full S044 prompt is identical in authoritative/NEXT_SESSION_PROMPT.md
and sessions/S043/S044_FUTURE_PROMPT.md. S044 is not executed here.
'''
    write('sessions/S043/CLOSEOUT.md', closeout)
    append('sessions/S043/RESEARCH.md', f"## Measured result\n\n{result['verdict']} at {stop_detail}: {result['models']} relaxation models, {result['cuts']} independently checked cuts, {result['planar_layers']} planar layers, {result['cpu_seconds']:.3f} CPU s. {conclusion} Gate PIVOT; no witness or qualifying pair. See CLOSEOUT.md and validation/S043/RESULT.json. No additional source, symmetry class or local search was attempted.")
    state.update(as_of='2026-10-24', last_completed_session='S043', recommended_next_session='S044',
                 headline_status='OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S043',
                 source_status='S029_LANDSCAPE_FROZEN_PLUS_DATED_REFRESH_S043_NO_NOVELTY_CLAIM',
                 current_computation='STOPPED', next_session_status='S044_QUEUED_FUTURE_UNEXECUTED',
                 next_session_is_future_unexecuted=True, latest_session_branch='main',
                 latest_session_entry_main=summary['entry_main'])
    state.pop('active_session', None)
    state['s043_queued']['status'] = 'EXECUTED_CLOSED_S043_PIVOT'
    state['s043_result'] = summary
    state['s044_queued'] = dict(status='FUTURE_UNEXECUTED', installed_date='2026-10-24',
                               prompt='authoritative/NEXT_SESSION_PROMPT.md', archival_copy='sessions/S043/S044_FUTURE_PROMPT.md',
                               objective='Short owner-decision audit of S037–S043; recommend CONTINUE, PAUSE or CHANGE_TARGET; no new slice or search',
                               s036_restart_authorized=False)
    state['latest_session_integration'] = dict(status='VERIFY_PUSHED_COMMIT_AND_HOSTED_JOB_AFTER_PUBLICATION',
                                              entry_main=summary['entry_main'], branch='main', force=False,
                                              authority='S043 existing-main prompt',
                                              verification='artifacts/tmp/S043/INTEGRATION.json and immutable run linked in final report')
    state['open_obligations'][0] = 'S043 CLOSED PIVOT: '+result['verdict']+'. S044 short owner-decision audit FUTURE/UNEXECUTED; no automatic successor. S036 CLEAN_STOPPED.'
    state['open_obligations'].insert(1, 'Order3 layer-preserving156-edge28-vertex alpha<=3 slice: '+result['verdict']+'. Counts of models/cuts are activity, never projected coverage. All nine sorted S11 prefixes remain UNKNOWN.')
    claim = dict(id='CLM-0144', status='PROGRAMME_PROVED', sources=['SRC-0038', 'SRC-0064'],
                 claim='Conditional on CLM0137, the order3 layer-preserving156-edge28-vertex alpha<=3 class is represented without loss by126 size3 pair-orbits, exactly26 per disjoint layer,6831 four-set orbit clauses, two pinned distinct invariant triangles and17 sound subgroup lex-leader constraints. Every recorded Kuratowski orbit-support clause is independently justified.',
                 notes='sessions/S043/PLAN.md and RESEARCH.md; stdlib checker reconstructs all36200 base clauses and checks every subdivision. This encoding theorem and the recorded cuts do not settle a capped class. No global upper-bound consequence or full normaliser canonicalisation is claimed.')
    claims = read('catalogue/CLAIMS.json')
    assert claim['id'] not in {c['id'] for c in claims}
    dump('catalogue/CLAIMS.json', claims+[claim])
    append('catalogue/CLAIMS.md', f"## {claim['id']} — {claim['status']}\n\n{claim['claim']}\n\n{claim['notes']}")
    state['mathematical_results'].append(claim['id'])
    sources = read('catalogue/SOURCES.json')
    for source in sources:
        if source['id'] == 'SRC-0038':
            source.update(access='PROOF_INSPECTED', accessed='2026-10-24')
            source['note'] += ' S043: publisher PDF sections3.1 and5.2 inspected for the lazy subdivision-clause proof and the distinction between union/decomposition symmetry only; executable chain and other results not replayed.'
    new_sources = [
        dict(id='SRC-0064', title='PySAT seqcounter.hh triangular threshold counter implementation', authors='PySAT maintainers',
             year=None, publication_date=None, url='https://github.com/pysathq/pysat/blob/master/cardenc/seqcounter.hh', doi=None,
             access='STATEMENT_INSPECTED', accessed='2026-10-24',
             note='Official source implementation inspected. Installed PySAT1.9.dev15 recorded separately; master/version equality not assumed. Actual generated clauses reconstructed with independent stdlib code and justified by threshold semantics.'),
        dict(id='SRC-0065', title='The Earth–Moon Problem', authors='Epoch AI', year=2026, publication_date=None,
             url='https://epoch.ai/frontiermath/open-problems/earth-moon', doi=None, access='STATEMENT_INSPECTED', accessed='2026-10-24',
             note='Primary problem statement and explicit layers/colouring/non9 requirements inspected. Exact publication date unconfirmed. Limited current context, not an exhaustive novelty audit.')]
    assert not {s['id'] for s in sources} & {s['id'] for s in new_sources}
    dump('catalogue/SOURCES.json', sources+new_sources)
    append('catalogue/SOURCES.md', 'S043 refresh24Oct2026: SRC0038 sections3.1/5.2 PROOF_INSPECTED (scoped); SRC0064 PySAT official counter implementation STATEMENT_INSPECTED; SRC0065 Epoch AI primary problem statement STATEMENT_INSPECTED. SRC0048 refresh failed, no promotion. No novelty claim. See sessions/S043/PRIOR_ART.md.')
    for s in new_sources:
        append('catalogue/SOURCES.md', f"## {s['id']} — {s['title']}\n\n{s['authors']}; {s['url']}; accessed{s['accessed']}; {s['access']}. {s['note']}")
    dump('authoritative/STATE.json', state)
    write('authoritative/NEXT_SESSION_PROMPT.md', (ROOT/'sessions/S043/S044_FUTURE_PROMPT.md').read_text(encoding='utf-8'))
    header = ('# S043 CLOSED — order3 symmetric slice, decision PIVOT (24 October 2026)\n\n'
              f"Verdict {result['verdict']}: {result['models']} relaxation models, {result['cuts']} checked\n"
              'Kuratowski cuts; no certified witness. Bounds9<=chi_2<=12; S11 UNKNOWN.\n'
              'S036 stays stopped. S044 short owner-decision audit is FUTURE/UNEXECUTED;\n'
              'read authoritative/NEXT_SESSION_PROMPT.md. Existing main, normal non-force\n'
              'commit/push, no branch/PR. No further symmetry slice or local search.\n\n')
    for path in ('AGENTS.md', 'authoritative/START_HERE.md'):
        write(path, header+(ROOT/path).read_text(encoding='utf-8'))
    write('campaigns/CAM-0047.md', '# CAM-0047 — S043 exact Z3 slice, CLOSED PIVOT\n\n'
          'Owner `Run s043`,24 October2026. Existing main, no branch/PR. Full271+K9\n'
          'smoke and frozen S037–S042 replays PASS. PLAN and source hash registered\n'
          'before computing.\n\n'+json.dumps(summary, indent=2)+'\n\n'
          'Semantic cuts and full final CNF retained; private CDCL not saved.\n'
          'S044 owner-decision audit FUTURE/UNEXECUTED; S036 remains stopped.\n')
    report = f"S043: {result['verdict']}; {result['models']} models, {result['cuts']} checked Kuratowski cuts; {result['cpu_seconds']:.2f} CPU s; no witness; PIVOT. S044 owner-decision audit FUTURE/UNEXECUTED."
    for p, t in [
        ('docs/SESSION_LEDGER.md', '| S043 |2026-10-24| CAM0047 exact Z3 orbit CEGAR | '+report+' |'),
        ('docs/PHASE_GATE_LEDGER.md', report+' Phase1 NOT PASSED;9..12 unchanged; publication/Lean gates unchanged.'),
        ('docs/DECISION_LOG.md', report+' Registered gate unchanged; no additional class, local search or S036 restart.'),
        ('docs/FAILURE_LEDGER.md', report+' Lazy planarity cuts did not yield a certified construction. A cap remains UNKNOWN and cut counts do not measure coverage.'),
        ('campaigns/README.md', '**CAM-0047 / '+report+'**')]:
        append(p, t)
    print(report)


if __name__ == '__main__':
    main()
