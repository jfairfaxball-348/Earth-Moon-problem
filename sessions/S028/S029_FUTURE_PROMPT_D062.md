# S029 — prior-art and current-landscape audit, rStation first (FUTURE / UNEXECUTED)

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

The owner's submission of this prompt, its link, or 'run next session' invokes exactly S029 under D047. No second confirmation. Stop before S030. Governing decision: D062 (docs/D062_LANDSCAPE_THEN_ALPHA3_DIRECTIVE.md). D042 lower-only headline unchanged.

**Scope: literature and landscape only.** No solver campaigns, no candidate generation, no new graph verdicts. Elementary hand checks (e.g. re-deriving Lemma F of D062) are allowed; if any script is executed, run scripts/cloud_smoke.py first and record it. Read-only access to external sites: no posting, commenting, account creation, correspondence or outreach on rStation or anywhere else. No Lean, registration or publication.

## Entry
Read live remote main SHA/tree, PR parents, actual checks/jobs, open PRs/branches/rulesets before writes. Read AGENTS, STATE, START_HERE, SESSION_PROTOCOL, D062, catalogue/SOURCES.json and CLAIMS.json, research/PRIOR_ART_BASELINE.md, research/S023_UPPER_VS_LOWER_AUDIT.md, and the S025–S028 CLOSEOUT and PRIOR_ART files. Frozen facts: no chi>=10 biplanar witness; 9<=chi_2<=12; original271 corpus NON-BIPLANAR; C5 sum<=16 biplanar, sum17 24/26 certified; smallest certified obstruction D036 (18 vertices, 78 edges); 16/30 seed-270018 profiles closed; the old S029 queue is PARKED with its statuses unchanged.

## Pass 1 — rStation r/earth_moon (priority 1)
Enumerate EVERY paper and post in rstation.ai r/earth_moon (papers listing, problem page, discussion threads), including those already registered (SRC-0032, SRC-0042..0044). For each: URL, title, handle(s), posted/revised dates, version, claimed statements, proof status (full proof / sketch / computation / claim only), artefacts (code, certificates, data) and whether they can be fetched. Grade access honestly (METADATA_ONLY ... PROOF_INSPECTED). Specifically locate:
- any alpha<=3 (or alpha<=k) 9-colourability claim, search or partial result, including the "stopped alpha<=3 symmetric search";
- small-order claims (<=18, <=19, 20 vertices 9-colourable) and their methods/certificates;
- the linking lemma (paper 13), minimal non-biplanar graphs on <=10 vertices, blob-union sufficiency, the vertex-transitive census, fractional records and "limits of counting" (SRC-0043);
- hand exclusions of C5 blow-ups and any C5 iff classification;
- anything that duplicates or overlaps our certified results (CLM-0090..0109), Lemma F, or the D062 S030 plan.

## Pass 2 — wider landscape (2025–2026 emphasis)
Szeider arXiv 2609.28102 (any v2, follow-ups, Zenodo SRC-0039 contents, whether alpha<=3 is announced or in progress); Patil (Zenodo SRC-0007, GitHub earth-moon-biplanar and earth-moon-chi10); Trivedi SRC-0012; Doria SRC-0018; Epoch AI open-problem page status (SRC-0004); Kirchweger–Scheucher–Szeider SAT modulo symmetries and its available code; Eppstein blow-ups SRC-0041; Gethner/Sulanke/Boutin line; arXiv, Zenodo, Google Scholar, MathOverflow and GitHub searches for "biplanar", "thickness two", "Earth-Moon", "independence number three", "9-colorable" and chromatic-number/thickness pairs. Register every new source as SRC-#### with date, author, URL/DOI and honest grade. Do not invent citations.

## Second novelty pass
Rule 13 requires two independent checks: repeat the targeted searches with different terms after Pass 2 and record any change.

## Deliverables (then FREEZE)
1. research/S029_LANDSCAPE.md: the source table; an overlap matrix classifying each programme result (C5 threshold, Sigma=17 certificates, original271 closure, D036 and descent obstructions, profile closures, Lemma F) as DUPLICATE / OVERLAP / APPEARS_UNCLEARED (never "novel"); a section on the alpha<=3 question (who has proved, claimed, attempted or abandoned it; available tools; attribution obligations).
2. A go/no-go for S030: GO as drafted in D062, GO-MODIFIED (state changes and reasons), or REDIRECT (if T3 is already settled or clearly about to be, recommend the next target, e.g. alpha<=4 with its own finiteness bound, or a non-counting route) with evidence.
3. validation/S029/LANDSCAPE_FREEZE.json: freeze date, list of SRC ids with grades and access timestamps, sha256 of research/S029_LANDSCAPE.md. After freeze the baseline is append-only: later sessions may add a dated refresh but never rewrite it.
4. Paired sources/claims MD+JSON (new claims only if genuinely supported; Lemma F may be recorded as PROGRAMME_PROVED only with a full written proof and an attribution search), ledgers, campaign registry entry if any, truthful STATE.

## Closeout
Commit full S029 INPUT/PLAN/RESEARCH/ADVERSARIAL/PRIOR_ART/CLOSEOUT/MANIFEST/OWNER_INVOCATION/EXECUTED_PROMPT. Write the COMPLETE S030 prompt from the D062 draft plan, adjusted only by the frozen audit with reasons, byte-identical at authoritative/NEXT_SESSION_PROMPT.md and sessions/S029/S030_FUTURE_PROMPT.md. One atomic commit, ordinary PR, non-force two-parent merge (locally via the owner's jfairfaxball-348 credential per D061; in cloud via the harness branch); verify main, parents, tree and hosted governance jobs. The final report includes verified links, the go/no-go and the FULL S030 prompt. Do not execute S030.
