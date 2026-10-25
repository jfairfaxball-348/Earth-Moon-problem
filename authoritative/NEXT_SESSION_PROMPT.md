# S047 — calibration-gated mechanism trial: seeded generation versus PAUSE

FUTURE / UNEXECUTED. Written at S046 closeout. A subsequent owner invocation
("run next session" or supplying this prompt) authorises exactly S047 under
D047. Never restart S045's expired campaign or any S035/S036 control. Do not
execute S048 automatically. Existing main, ordinary non-force commit/push, no
branch/PR. The owner may instead decide to PAUSE construction search; that
decision needs no session.

## Purpose and entry

D042 target only: one certified finite simple biplanar graph with chi >= 10.
No witness; 9 <= chi_2 <= 12. No universal upper-bound work, Lean, publication
or outreach. All earlier UNKNOWN domains stay UNKNOWN; do not revive parked
star/patch, apex, nine-S11 or order-3 work because a question remains open.

S046 decided PIVOT / INCONCLUSIVE (sessions/S046/CLOSEOUT.md). Unguided
colouring-partition generation explores easy graphs: 99.676% of all 642381
saved S045 records have an empty 9-core; in 15 matched k=9 arms (orders
24/28/32/40/50; baseline, minimum-degree-9 core filter, core plus lex-leader
symmetry breaking) every analysed candidate had a checked colouring with at
most 8 colours. On the known-feasible k=8 analogue (amendment A1) the same
generator found K6 v C5 only at n=11 and found no 9-chromatic graph in 40 s at
any order 13–24, including arm B at n=15/20 where padded K6 v C5 is in the
domain. S047 tests whether a different mechanism has measured sensitivity
before any further k=9 search.

Read authoritative/STATE.json, sessions/S046/{CLOSEOUT,RESEARCH,ADVERSARIAL,
PRIOR_ART}.md, validation/S046/{REGISTRATION,AMENDMENT_A1,BUDGET}.json and
validation/S046/calibration/A1.json. Reconcile live remote main, parent/tree,
worktree, processes and actual hosted jobs before writing. Use new S047 files
and runtime root artifacts/tmp/S047; S046 tools are reusable read-only
(tools/s046_driver.py, s046_encode.py, s046_analyse.py); never edit an
executed S046 file. Record executor, sources, binaries and inputs.

Before computation preregister mechanisms, ladder, seeds, budgets, caps and
decision gates; run fresh full 271+K9 smoke on pinned tools (Windows:
EMP_DRAT_TRIM and EMP_CADICAL to the S004 executables). Reuse accepted
installations; install additions only when justified and tested.

## 1. Calibration ladder (k = 8)

Target: non-8-colourable biplanar graphs, which exist (K6 v C5 at 11
vertices; padded copies at every larger order in an unrestricted domain).
Register orders 13, 15, 17, 20, 24 and the domain variant for each arm. A hit
requires independently checked planar layers, a drat-trim-verified
non-8-colourability proof and a checked 9-colouring. Existence claims for
minimum-degree-8 domains at a given order must be verified explicitly or cited
with access grade; "not found in cap" is UNKNOWN, never non-existence. The
S046 A1 rows are the frozen baseline (no hit at any order >= 13 in 40 s).

## 2. Mechanisms (equal registered budgets)

- M0 baseline: S046 arm B and C at k=8 (re-run only if the environment or
  binary changed; otherwise cite A1).
- M1 seeded generation: pin a certified biplanar seed as a labelled subgraph
  (for k=8, K8, contained in K6 v C5; record its layers) and search biplanar
  supergraphs at the ladder order with the same checked colouring-partition
  feedback. Justify that pinning is a restriction (it never claims to cover
  graphs without the seed) and label the arm's exact scope.
- M2 co-certificate amplification: for each candidate add several distinct
  checked colouring-partition clauses (for example, alternative colourings
  or splits), with the soundness argument written and controlled.
Optionally one further mechanism if it is genuinely distinct and justified in
writing before computation. No mechanism may assume alpha, regularity, exact
density, triangulation or automorphisms without labelling a restricted arm.

## 3. Gate and conditional k = 9 pilot

A mechanism QUALIFIES if it obtains certified hits at >= 3 of the 5 ladder
orders within its cap and strictly beats the A1 baseline there. Only a
qualifying mechanism may receive a bounded k = 9 pilot (registered orders,
for example 21, 24, 28, with the k = 9 seed K8 or K6 v C5 and a written
reason), at most 600 CPU s, stop on the first non-nine alert. A k = 9 alert is
UNKNOWN until standalone checked: labelled disjoint planar layers, drat-trim
non-9-colourability, and for exact chi = 10 a checked 10-colouring.

## Budgets and resources

One heavy generator plus a serial oracle; 3 GiB aggregate private-memory hard
cap, 1.5 GiB available-RAM floor, 10 GiB disk reserve. At most 1800 CPU s and
3600 wall s of experimental computation in total (calibration, mechanisms and
any k = 9 pilot), allocated before experimenting, with a fresh absolute
experimental deadline; audits, proofs and smoke are verification costs
recorded separately. Charge in-slice audits as verification from the start.
No unattended campaign, automation or long run in S047.

## Decision

- SELECT_FOR_DESIGN: a mechanism qualifies and its k = 9 pilot runs cleanly;
  specify the domain, seed, uncertainty and a resumable future design with
  explicit finite subproblems, durable checkpoints and independent proofs.
  This is an empirical research choice, not evidence that a witness exists.
- PAUSE_RECOMMENDED: no mechanism qualifies; preserve evidence and recommend
  the owner pause construction search (S044/S046 evidence), stating what new
  input would justify re-entry.
A certified k = 9 hit is reported as a candidate witness only after every
standalone check passes; nothing else is a lower-bound claim.

## Deliverables and successor

INPUT/PLAN/RESEARCH/ADVERSARIAL/PRIOR_ART/CLOSEOUT; registration and budget
receipts; ladder table; mechanism soundness arguments and controls; exact
hashes; stdlib-only portable checker for the hosted scaffold; frozen-context
replay for any historical check whose hashed authority files change.
Synchronise authority, source/claim, session/decision/failure/phase/campaign
ledgers; verify ordinary non-force publication and the actual hosted run.
Install byte-identical authoritative and session-local S048 FUTURE/UNEXECUTED
prompts and print the full next prompt. For any proposed long run state
duration, hard-stop policy, two-hour check-ins and acceptance gates; do not
install its automation or launch it in S047. Do not execute S048.

Actions fallback: docs/CLOUD_ENVIRONMENT.md and validation/S011/SUMMARY.json;
same-job pinned setup and full smoke before scientific computation. Scaffold
replay is not a new solver certificate; ephemeral ZIPs must not be the only
evidence copies.
