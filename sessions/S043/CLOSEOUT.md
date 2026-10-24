# S043 CLOSED — order3 symmetric slice, decision PIVOT

24 October2026. Verdict **UNKNOWN**, stopped at registered20000-cut cap.
No chi>=10 witness;9<=chi_2<=12. The entire order3 slice remains UNKNOWN; this run supplies no certified exclusion.
The fixed progress gate failed: neither a certified witness nor a checked
156-edge symmetric pair with<=40 independent four-sets. S044 is queued only
as the short owner-decision audit, FUTURE/UNEXECUTED. S036 remains stopped.

Results: 10000 alpha<=3 relaxation models processed,
20000 independently justified Kuratowski orbit-support cuts;
0 planar layers among those models. No planar pair
was saved. One explicit symmetric78-edge planar layer is a control only.
Search CPU1026.703s, wall1028.672s;
search limits1800 CPU s/3600 wall s/20000 cuts, total experimental cap2400
CPU s including any native certification, below the owner's7200 ceiling.
The observed interrupted solve count is1
when no UNSAT call occurred; interrupted calls supply no mathematical result.

CLM0144 gives the orbit reduction and sound symmetry breaking. The separate
stdlib checker reconstructs all36200 base clauses (12073 variables), checks
every one of20475 four-sets, the threshold-counter semantics and17 generator
inequalities, then independently traces all subdivision branch paths.
Cut kinds: {"K33": 17653, "K5": 2347}.
No projection count or percentage of excluded graphs is established.

Acceptance: fresh full271+K9 smoke PASS, all271 chromatic proofs and CNF
hashes checked; retained and fresh native K9 proofs verified. Frozen
S037–S042 replays PASS at entry. S043 corruption controls and full independent
CNF/subdivision replay PASS (1.125 CPU s for final replay).
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
