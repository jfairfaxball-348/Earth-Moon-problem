# S048 — re-entry gate after the contradiction-route audit (PAUSE recommended)

FUTURE / UNEXECUTED. Written at S047 closeout (D079). A subsequent owner
invocation ("run next session" or supplying this prompt) authorises exactly
S048 under D047. The owner may instead simply PAUSE; that needs no session.
Never restart S035/S036/S045 controls. Do not execute S049 automatically.
Integration as the executing environment allows: on the owner's laptop the
existing main with ordinary non-force commit/push; in a cloud container the
harness-assigned branch (AGENTS rule 12), no PR unless requested.

## Entry

Target: D042 lower bound chi_2 >= 10, read with the D079 amendment
(argument-certified or non-constructive proofs count; upper-bound work stays
out of scope). No witness; 9 <= chi_2 <= 12. Read authoritative/STATE.json,
sessions/S047/{CLOSEOUT,RESEARCH,ADVERSARIAL,PRIOR_ART}.md,
docs/D079_S047_CONTRADICTION_ROUTE.md and validation/S047. Reconcile live
remote main/branch, parent/tree, worktree, processes and hosted runs before
writing. Run fresh full 271+K9 smoke before any computation.

Standing facts from S047 (do not re-derive): O1 no uniform chi-raising
biplanarity-preserving operation (CLM-0152); O2 10-critical window
ceil((88n-70)/18) <= m <= 6n-12 (CLM-0155); O3 no (generalised)
Mycielskian of a graph with chi >= 9 is biplanar (CLM-0154); O4 10-chromatic
Schrijver graphs k <= 3 not biplanar (CLM-0156); no biplanar chi >= 10 graph
contains K6 v C5 plus at most five vertices (CLM-0153); six or more UNKNOWN
(CLM-0157). Szeider: alpha <= 2 biplanar graphs are 9-colourable (SRC-0009).
All earlier UNKNOWN domains stay UNKNOWN.

## 1. Re-entry evidence (no heavy computation)

- Prior-art refresh since 29 October 2026: any claimed chi >= 10 biplanar
  graph, new small-order or alpha results, new sparse colour-forcing or
  transfer constructions. Honest SRC grades; unrefereed claims are not
  filters.
- Any owner-supplied idea, recorded verbatim.

## 2. Re-entry test (written)

A proposed route RE-ENTERS only if it states, before computation:
(a) the explicit graph or operation and why it lands in the O2 window;
(b) why it escapes O1 (one-shot hypothesis named) and O3/O4;
(c) for seeded constructions, a seed other than the K6 v C5 neighbourhood
    already excluded, or a forcing argument for >= 6 added vertices;
(d) a calibration on a known k = 8 instance (K6 v C5 from K5 v C5 or a BGS
    9-critical graph) that the method reproduces;
(e) a finite certified next step whose success would yield a witness
    (layers, planarity, drat-trim non-9-colourability).

## 3. Optional bounded check

Only if a route passes section 2: one registered experiment, at most
600 CPU s / 1200 wall s, one worker, 3 GiB, stop on the first k = 9 alert;
any alert is UNKNOWN until standalone checked.

## Decision

RE-ENTER (route passes the test; specify its registered S049 design, budget,
checkpoints and stop rules, not executed) or STAY_PAUSED (record what new
input would change this). Deliverables: INPUT/PLAN/RESEARCH/ADVERSARIAL/
PRIOR_ART/CLOSEOUT, registration, checker, ledgers, STATE, byte-identical
authoritative and session-local S049 FUTURE/UNEXECUTED prompt printed at
closeout. No unattended run, automation, Lean, publication or outreach.
