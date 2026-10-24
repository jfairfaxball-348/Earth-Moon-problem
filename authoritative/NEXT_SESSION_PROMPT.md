# S042 — Certified apex-leaf census for non-alpha chi>=10 joins (route R3)
FUTURE / UNEXECUTED — queued by the S041 comparative audit, 24 October 2026

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

The owner's next invocation or provision of this prompt authorises exactly
S042 under D047. Do not execute S043 automatically. Use existing main and an
ordinary non-force commit/push; no new repository, branch or PR. Never restart
S036, its old controls or schedulers. No unattended run. Bounds remain
9<=chi_2<=12; the target is a certified chi>=10 biplanar construction, not a
universal upper bound (F9 and other universal colouring bounds stay out of
scope, D042) or full EMP resolution. Publication/Lean gates remain.

Read live AGENTS, STATE, D077 and S041 INPUT/PLAN/PLAN_ADDENDUM/RESEARCH/
ADVERSARIAL/PRIOR_ART/CLOSEOUT. Pin remote main, verify S041's commit/tree and
frozen manifest; run check_s037_records.py, check_s038_records.py,
check_s040_handoff.py, check_s040_records.py and check_s041_records.py. Run a
fresh full scripts/cloud_smoke.py with pinned native tools before any
computation. A cloud fallback must run scripts/cloud_setup.sh and full smoke in
the SAME job. Historical runner receipts: validation/S011/SUMMARY.json and
docs/CLOUD_ENVIRONMENT.md. Hosted scaffold success is not acceptance.

Why R3. S041 ranked the non-alpha join route first: chi(K_a v H)=a+chi(H) is
certified by construction, so a witness does not need chi_f>9 (rStation F9
risk). Counting with Kostochka-Yancey leaves only K1vH9, K2vH8 and K3vH7 with
omega(H)<=8-a; Mycielski constructions never fit. Hajos composites of
9-critical biplanar graphs are biplanar (BGS), but every composite contains each
leaf minus one edge. S041 certified, by Lemma-B/C K9-minor CEGAR with pinned
DRAT, that the apex leaf graphs of Sulanke K6vC5, K3vHajos(K6,K6) and
K2vHajos(K7,K7) are NOT biplanar, each in under a second. The live question is
whether ANY admissible leaf survives. Do not resume four-set hill-climbing,
symmetric OP1(b) search or the S11 cells in this session.

Task: an exact, certified census of apex leaves. A leaf for K_avH is a
(10-a)-critical graph L with an edge e (or, for a>=2, a registered small edge
set) such that omega(L-e)<=7-(a-1), the apex budget holds, and K_av(L-e) is
biplanar. Register before computing: (1) the candidate list and its
provenance: complete graphs, odd cycles, k-Ore/Hajos graphs of cliques, Gallai
joins of these on <=16 vertices, and published 9-critical biplanar graphs
(Boutin-Gethner-Sulanke SRC-0002/0003, including the 17/25/33-vertex ones if
their data can be obtained; record access grades); state exactly what is and is
not complete; (2) the deduplication by isomorphism; (3) the decision engine:
tools/s025_minor_cegar.py --lemmaC 5 for negatives (pinned DRAT plus
tools/s025_check_minor_cert.py), tools/s025_cover_anneal.py for positives
(independently checked layers and rotations), per-graph caps; caps are UNKNOWN.
Re-derive the S041 counting filters in code before use. Audit closed ranges
(CLM0072-0076, CLM0137-0140) so nothing closed is recomputed as new.

Solid-progress gate (D077 style; fix it before any census output, never lower
it): PROGRESS iff (A) a certified chi>=10 biplanar witness (explicit V,E1,E2,
checked planar layers, edge-disjointness, and chi>=10 by a written Hajos/join
argument plus, where feasible, verified DRAT non-9-colourability), or (B) a
live leaf: K_av(L-e) certified biplanar by explicit checked layers with omega
<=8, L independently re-verified (10-a)-critical, apex slack >=1 (so two copies
can absorb a Hajos junction), reproduced from the archived data by a separate
checker, plus a written account of how it evades Lemma B/C. Anything else,
including UNKNOWN caps or more negative leaves, is PIVOT: record the certified
census closure, park R3 apex search, and queue S043 to the next S041-ranked
route (R1: exact layer-preserving Z3 class at order28) or a fresh audit.
If (B) holds, build at least one composite K_av Hajos(L1,L2) from live leaves
and decide it exactly within the caps.

One experiment process, <=3600 cumulative CPU s, short per-graph caps, explicit
stop criteria. Saved graphs: explicit edges, hashes, layers/rotations or
certificates. Refresh result-specific primary sources; no novelty claim.
Close with measured results/limitations, synced catalogues/state/ledgers,
independent portable checks, normal commit/push and actual hosted job results.
Install identical full S043 FUTURE/UNEXECUTED prompts in authoritative/ and
sessions/S042/, print the full next prompt with verified links, and stop.
