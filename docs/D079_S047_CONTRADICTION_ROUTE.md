# D079 — owner retargets S047 to a contradiction-route feasibility session (29 October 2026)

Owner instructions (cloud Claude Code conversation, 29 October 2026):

1. Asked whether the lower bound could come "from working rather than just
   looking for a counterexample"; after an explanation of existential versus
   universal statements: "Yes I want to explore this. Specifically the
   contradiction one".
2. After the proposed D079 and S047 retarget: "Yes, replace with new target,
   and do run the session now here".

Effect:

- The queued S047 calibration-gated mechanism trial (written at S046 closeout)
  is SUPERSEDED, never executed. Its text is preserved unchanged in
  sessions/S046/S047_FUTURE_PROMPT.md (S046's executed handover record).
- New S047 target: contradiction-route feasibility. Assume H = "every finite
  biplanar graph is 9-colourable" and study which proof-by-contradiction
  templates could refute H: Mycielski-type colour-transfer operations Phi with
  "a 9-colouring of Phi(G) yields an 8-colouring of G", colour-forcing and
  disjunctive gadget arguments, and genuinely non-constructive routes
  (counting, fractional/LP duality, topological bounds).
- D042 amendment, scope only: an argument-certified or non-constructive proof
  that chi_2 >= 10 (for example a written proof that an explicit or implicitly
  defined finite biplanar graph has no proper 9-colouring) counts toward the
  headline, provided every step is stated, checked and adversarially
  reviewed. Upper-bound work remains out of scope. Finite computations prove
  only their stated finite domains. Every certification rule of AGENTS.md
  (sources, claims, no uncheckable "solver says no") still applies; an
  explicit witness, if one arises, still needs labelled layers and checked
  proofs.
- The full S047 prompt is authoritative/NEXT_SESSION_PROMPT.md as installed
  by this decision (its text is also recorded below). The owner's message (2)
  invokes exactly S047 now under D047, in this cloud session. S048 is not
  authorised.
- Integration: harness-assigned cloud branch ccr-af80f6d5-2qearo (AGENTS
  rule 12, docs/CLOUD_ENVIRONMENT.md) with ordinary non-force commits; the
  owner decides whether it is merged to main. No PR unless requested.

No mathematical result, claim status, source grade or historical UNKNOWN is
changed by this decision. 9 <= chi_2 <= 12.

## S047 prompt as installed by D079

```
# S047 — contradiction-route feasibility (D079)

Invoked by the owner in the D079 conversation (D047); runs now. Never restart
S035/S036/S045 controls. Do not execute S048.

Target: D042 lower bound chi_2 >= 10, read with the D079 scope amendment.
Hypothesis to refute: H = every finite biplanar graph is 9-colourable
(by compactness equivalent to the infinite statement).

1. Logic: state precisely what refuting H requires, which templates are
   constructive in disguise and which are genuinely non-constructive.
2. Prior art (SRC/CLM with honest access grades): Mycielski-type and
   generalised Mycielski constructions, Kostochka-Yancey critical-graph edge
   bounds, Gallai's join theorem, topological lower bounds (Lovasz,
   Simonyi-Tardos zig-zag), thickness-two colouring literature
   (Gethner-Sulanke, Boutin-Gethner-Sulanke), recent 2024-2026 work.
3. Obstructions, written as proofs with mechanical checks:
   (a) no biplanarity-preserving operation can raise chi for every biplanar
       graph; (b) the 10-critical density window; (c) (generalised)
       Mycielskians and the cone against that window.
4. Bounded certified computation testing the template on the only known
   9-chromatic biplanar seed K6 v C5: classify the biplanar non-9-colourable
   supergraphs with t added vertices for small t (exact, DRAT-certified
   completeness), and any further check registered before it runs.
5. Registered gate: PROGRESS if a new certified result materially narrows or
   advances the contradiction route (a theorem excluding a whole template
   family, or a witness); otherwise PIVOT with a stated recommendation
   including PAUSE.

Budget: at most 1800 CPU s / 3600 wall s experimental computation, one heavy
worker, 3 GiB memory cap; fresh full 271+K9 smoke before computation.
Deliverables: INPUT/PLAN/RESEARCH/ADVERSARIAL/PRIOR_ART/CLOSEOUT, registration,
checker script, ledgers, STATE, byte-identical authoritative and session-local
S048 FUTURE/UNEXECUTED prompt printed at closeout.
```
