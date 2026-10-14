# S011 — certified χ ≥ 10 biplanar construction (lower bound only) (FUTURE, UNEXECUTED)

STOP. This prompt authorises nothing by itself. A fresh explicit owner invocation permits exactly S011, not S012. No formalisation/Lean, Palomar/registration, manuscript/publication/arXiv/journal, announcement or external correspondence is authorised.

## Target (owner decision D042, 2026-10-14)

Raise the Earth–Moon lower bound from χ₂ > 8 to **χ₂ > 9**: find one finite simple graph G with an explicit edge-disjoint split E = E₁ ⊔ E₂ into two planar layers and **χ(G) ≥ 10**, and certify it completely. Nothing else counts as a headline result.

**Out of scope:** universal upper bounds (χ₂ ≤ 11/10/9), discharging, reducibility, Kempe/palette extension and other 12-critical-graph routes, and any claim to resolve EMP. Do not open new campaigns on those routes. S002–S010 upper-bound claims (e.g. CLM-0060, CLM-0065, CLM-0066) are history only. A certified χ ≥ 10 witness proves χ₂ ≥ 10 and leaves 10..12 open; never describe it as resolving EMP.

**What counts as success** (all five, independently checked, per docs/CERTIFICATE_POLICY.md and AGENTS rule 6):
1. explicit labelled V, E₁, E₂, simple and edge-disjoint;
2. an independent planarity witness (combinatorial rotation system with Euler check) for EACH layer;
3. a proper colouring (evidence of the upper side only);
4. a rigorous proof of **no proper 9-colouring**: a hand proof, or a regenerated CNF with an independently checked LRAT/DRAT refutation; bare UNSAT, timeouts and SAT relaxations never count;
5. cold re-check from a fresh environment, with SHA-256 hashes and exact reproduction commands.

**Acceptable negative output:** a new checked obstruction, a genuinely new exhaustive census of a stated finite domain, or a new candidate family with certified χ ≥ 10. A failed or capped search proves nothing about whether a witness exists, and must not be presented as evidence that χ₂ = 9.

## Entry before writes

**Environment first (D043, cloud).** Confirm the SessionStart hook completed (else run `bash scripts/cloud_setup.sh`), then run `.venv/bin/python scripts/cloud_smoke.py`. Record its verdict, counts and `artifacts/tmp/native/ENVIRONMENT.json` binary hashes in the S011 manifest. A FAIL blocks all scientific computation. Reset the harness-assigned session branch to live main before any write. Follow docs/CLOUD_ENVIRONMENT.md.

Independently pin LIVE remote main SHA/tree/status. Observed when D042 was written (re-verify, do not trust): main a7fe884b62b37f6ca1cc8e764aa97fbf415e8425 = two-parent merge of PR #10 (S010 authored b585c03 on codex/S010-strategic-reset, entry parent 8626b6419f12d706f3ba567f6733d26d6e4dd7be), hosted "Research scaffold checks" run 38614745866 success. The PR listing API returned merged:false for PRs #6–#10 despite merge commits on main; reconcile from commit parents and trees. D042 re-scope integration is recorded in STATE `d042_integration_verified` (PR #11, merge a58df4728f38a30e53d5a9b9595ff823f86bc215); re-confirm it, and reconcile the later D043 cloud-environment governance commit/PR live. Audit all open/recent/competing PRs, branches, workflows, runs, jobs, check-runs, status contexts and protection/rulesets. Zero-context pending is not CI PASS; unavailable endpoints are UNKNOWN.

Read AGENTS, STATE (including programme_scope, execution_environment and retired_upper_bound_obligations_D042), START_HERE, SESSION_PROTOCOL, docs/CLOUD_ENVIRONMENT.md, DECISION_LOG D042/D043, the complete S010 records (CLOSEOUT, RESEARCH, ADVERSARIAL, PRIOR_ART, ENTRY_EVIDENCE, EXECUTED_PROMPT), research/S010_STRATEGIC_AUDIT.md, CAM-0011, validation/S010/SUMMARY.json and the S010 manifest. sessions/S010/S011_FUTURE_PROMPT.md is the pre-D042 prompt and is superseded by this file. Archive the fresh owner invocation and this complete prompt. Preregister exact ranges, completeness and symmetry arguments, environment, commands, launch source/input hashes, checkers, proof formats, caps and stop rules BEFORE any scientific computation. Refresh primary literature on 10-chromatic biplanar constructions and searches, including 2026 work; a search excerpt is not proof inspection or novelty.

## Construction frontier carried over

- **Primary candidate pool:** 271 α ≥ 3 clique blow-ups of 7–8-vertex bases from CAM-0004, all exactly χ = 10 (checked). 52 rows are proven non-biplanar (checked DRAT); **219 rows are biplanarity UNKNOWN**; 31/42 original D2 rows UNKNOWN. Exact indices and lane statuses are in validation/S010/SUMMARY.json. Proving ANY one row biplanar, with explicit checked layers, meets the target (its χ = 10 proof already exists and must be cold re-checked).
- Open sub-items: row 165 no-lex and the S005 23-vertex row-158 deletion are UNKNOWN; C5 maximal-13 pattern and its children open; no independent exhaustive whole-k8/k9 blow-up census exists (only two fixed samples audited).
- **Closed families (do not repeat without a new idea):** biplanar graphs with α ≤ 2 are 9-colourable (Szeider 2026, source-stated); every biplanar odd-cycle clique blow-up is 9-colourable (in-repo proof); blow-ups of bases on ≤ 6 vertices give no χ ≥ 10 biplanar graph (CLM-0019); the saturated Hajós/two-Sulanke cone is non-biplanar; all 159 pinned corpus apices are excluded; K6 ∨ I6 is biplanar but only χ = 7, with no lift.
- **Prior art to check before any novelty statement:** Patil 2026 (SRC-0007) reports exhausting the then-known χ = 10 candidates; Patil's earth-moon-chi10 repository (SRC-0021) has been 404 every session; rStation discussion (SRC-0032) claims unverified small-order results. None is a programme bound.

## Candidate filters (proved; use only to discard candidates)

- K₉ is not biplanar (DRAT-verified).
- No biplanar graph contains K5,13, K6,9 or K7,7 (CLM-0064, hand proof). None of the 271 rows contains one (CLM-0068), so these filters alone exclude no remaining row.
- Every K₇ in a biplanar graph has at most 4 common outside neighbours (CLM-0063).
- |E| ≤ 6n − 12, and every subgraph obeys the same bound.

## Suggested routes (pursue several; pivot when blocked)

1. **Positive search on the 219 rows.** Spend effort on FINDING planar layer pairs, not on longer refutation caps: layer-pair SAT/local search with explicit layer extraction and independent planarity checking. One success meets the target.
2. **Genuinely new candidate sources.** Registered exhaustive whole-k8/k9 clique-blow-up census with a canonical base universe and an all-weight completeness reduction; or non-blow-up families (α ≥ 3 partial joins, layer-compatible identifications of 9-critical graphs, non-saturated apex face covers), each with a written proof that its operation preserves thickness ≤ 2 or an explicit layer check.
3. **Direct generation from planar layer pairs.** Generate pairs of planar graphs on a common vertex set (for example, triangulation pairs with controlled overlap), take the union, and test χ ≥ 10 with proof-producing SAT. A bounded negative result needs a stated finite domain with symmetry and completeness justification.
4. **New obstructions** only when they decide many remaining rows at once, not one-row refutations at longer caps.

## Tools and reproduction hazards

Cloud toolchain per docs/CLOUD_ENVIRONMENT.md: `.venv/bin/python` (Python 3.12, python-sat 1.9.dev15, networkx 3.5) and Linux builds of the S004-pinned CaDiCaL c6073042 and drat-trim 2e3b2dc0 in `artifacts/tmp/native/bin/`. Legacy `artifacts/tmp/S004/*.exe` paths are symlinks to them, so historical scripts run unedited. Never edit preserved S004–S010 scientific scripts; put new code in new files. The Linux binaries are a new environment: record their hashes, and never claim byte reproduction of Windows results. Historical README commands using `.venv/Scripts/python.exe` translate to `.venv/bin/python`.

CRITICAL: importing s008_tree globally patches triangulation_cover.CardEnc, so sequential Cover and totalizer/tree generators MUST run in separate fresh processes, otherwise cold CNF bytes change (F045). Native checker failures and caps remain FINAL UNKNOWN; two consecutive such outcomes stop a lane and later targets are NOT_RUN. Linux CaDiCaL supports `-t`, but still enforce registered wall/memory caps externally. **Container limits:** 4 CPUs and about 15.7 GiB RAM, so preregister at most one heavy worker at 12 GiB or two at 6 GiB each, and watch the disk allowance (delete uncompressed scratch after hashing). **Persistence:** the container is reclaimed when idle; checkpoint results under `artifacts/tmp/`, size campaigns to finish within the session, push never-merged `wip/S011-…` backup snapshots if pausing, and treat targets lost with a container as UNKNOWN/NOT_RUN. Take immutable source/input/native snapshots before launch. Do not edit generator code while it is running. Never refute from partial/initial/last-cut CNFs, bare UNSAT or SAT_RELAXATION, and never treat a SAT relaxation as planar without extracted, independently checked layers.

## Exit

Sync paired sources/claims MD+JSON, state, phase/session/decision/failure/campaign ledgers and complete S011 records (INPUT, PLAN, RESEARCH, ADVERSARIAL, PRIOR_ART, CLOSEOUT, SUMMARY, manifest). One atomic authored session commit, ordinary PR, non-force two-parent merge, independent verification of final main/parents/tree/actual jobs. Scaffold CI is a governance check, not a mathematical proof. Prepare an S012 prompt marked FUTURE/UNEXECUTED, keeping the D042 lower-bound-only scope unless the owner changes it. No fake citations, certificates, hashes, PRs, CI results, embeddings, novelty or claims that χ₂ ≥ 10 is established without all five checks.
