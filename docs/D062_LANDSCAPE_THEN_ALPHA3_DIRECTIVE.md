# D062 — landscape audit first, then the alpha<=3 finite programme (owner, 2026-10-19)

**Governance only. No session executed, no science run, no claim or graph status changed.**

## Owner decision

After reviewing S001–S028 the owner directed a pivot away from the capped
28-vertex alpha3 obstruction-closure loop (queued S029 under D061):

1. **S029 = prior-art and current-landscape audit, rStation r/earth_moon first.**
   Literature/landscape only. Its output is FROZEN as the baseline for S030.
2. **S030 = the alpha<=3 finite programme (Option 5)**, drafted below. S029 must
   turn this draft into the full S030 prompt, changed only where the frozen
   audit gives a recorded reason (for example, the result is already published
   or a stronger tool exists).

The previously queued S029 (obstruction-closure queue resume) is **PARKED, not
discharged**. Its 12 NOT_RUN queue graphs, S028-P10-B10-0007 (UNKNOWN), the 9
surviving S027 surplus graphs and C5[3,3,4,3,4], C5[3,3,3,4,4] keep their
recorded statuses. Its text is preserved verbatim at
sessions/S028/S029_FUTURE_PROMPT.md (frozen S028 text, superseded by D062).

## Why (review summary)

* Every candidate since S026 relies on the counting bound chi >= n/alpha. That is
  a fractional certificate; whether any biplanar graph has chi_f > 9 is open
  (rStation SRC-0043 "limits of counting"). The loop may be capped by design.
* The machinery built since S025 (certified obstructions, K9-minor CEGAR with
  DRAT, profile-closure proofs) is strong on the negative side and has never
  produced a positive split.
* Several parallel groups (Szeider SRC-0009/0037, Patil SRC-0007/0017/0021,
  Trivedi SRC-0012, Doria SRC-0018, rStation SRC-0032/0042..0044) work on the
  same questions. Novelty and overlap must be settled before more compute.

## Option 5 statement and the finiteness lemma (to be re-verified in S029/S030)

**T3.** Every biplanar graph with independence number alpha <= 3 is 9-colourable.

**Lemma F (elementary, attribution to be checked).** If G is biplanar on n >= 3
vertices with alpha(G) <= 3, then n <= 36. *Proof sketch:* the complement is
K4-free, so by Turán |E(G)| >= C(n,2) - t(n,3); biplanarity gives
|E(G)| <= 6n - 12. These are incompatible for n >= 38; at n = 37 equality forces
the complement to be T(37,3), i.e. G = K13 + K12 + K12 (disjoint union), which
contains K9, and K9 is not biplanar (SRC-0014). The same inequality gives
n <= 24 for alpha <= 2, matching Szeider's scale. Numerical check (2026-10-19,
governance conversation, not a campaign): the minimum edge counts forced by
alpha<=3 are 117/156 at n=28, 155/180 at n=32, 198/204 at n=36 and 210/210 at
n=37 (forced edges / biplanar maximum).

T3 is therefore a statement about a **finite** domain. Searching it is two-sided:
either T3 holds (closing every alpha<=3 witness route, a direct extension of
Szeider's alpha<=2 theorem), or the search exhibits a biplanar alpha<=3 graph with
chi >= 10, which is the D042 headline witness.

**Scope reading (owner-confirmed in D062):** an exhaustive certified search of
this finite domain is a finite computation proving only its stated domain
(AGENTS rule 7). It is authorised for S030 when invoked. It is NOT
authorisation for universal upper-bound work beyond alpha<=3, discharging, or
claims about chi_2 itself. D042 headline and all certificate rules stay binding.

## Draft S030 plan (FUTURE/UNEXECUTED; S029 finalises it)

1. Re-prove Lemma F and the minimal-counterexample properties in writing: a
   vertex-minimal induced subgraph with chi >= 10 has chi = 10, alpha <= 3,
   minimum degree >= 9, no K9, 10 <= n <= 36 and an edge count in the Lemma F window.
   Use any smaller lower bound on n only if its source is verified, not
   forum-stated.
2. Inspect Szeider's alpha<=2 reduction (exact union of two sphere
   triangulations, filter, SAT, Lean) and record exactly which steps transfer
   to alpha<=3 and which fail.
3. Close the top of the range (about n = 33..36) analytically or by small
   certified computations (the edge window forces near-three-clique structure
   and hence K9).
4. Build and validate a COMPLETE enumerator for the remaining sizes (SAT modulo
   symmetries in the Kirchweger–Scheucher–Szeider style, SRC-0038), with
   positive and negative controls, pruned by the certified obstruction library
   and by proved filters (K9, K6,9, K7 with five common neighbours, Euler
   bounds). Bank each finished n as a certified "no alpha<=3 chi>=10 biplanar
   graph on n vertices" result with checked proofs.
5. Any graph that both splits and survives the 9-colouring check is a WITNESS
   CANDIDATE: stop and verify independently first.
6. Local pins, full smoke before computation, one heavy tree within the resource
   caps, preregistration before science, caps are UNKNOWN not exhaustion.
