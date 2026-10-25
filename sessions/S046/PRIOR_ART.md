# S046 prior-art admission and scope matrix

Refreshed 25 October 2026 through a fetch/search tool that returns
model-produced page summaries. No proof was read line by line and no external
artefact was replayed, so every forum grade below is at most
STATEMENT_INSPECTED. Forum results are claims, never filters. This limited
search is not a novelty guarantee. Starting points: research/S029_LANDSCAPE.md
and sessions/S045/PRIOR_ART.md.

## Order / family matrix

| Domain | Status | Source (grade) | Scope and dependencies |
|---|---|---|---|
| all biplanar graphs, n <= 13 | stated 9-colourable | Kirchweger–Scheucher–Szeider SAT 2023, SRC-0038 (this statement seen only in a search summary this session; S043 inspected sections 3.1/5.2) | computer-assisted SAT modulo planarity/symmetries |
| n <= 18 | claimed 9-colourable | rStation paper 1 / post 2 (METADATA_ONLY via listing); EpsilonPhoenix/earth_moon_small_order GitHub, SRC-0073 (METADATA_ONLY) | unrefereed; repository reports a partial Lean formalisation |
| n <= 19 | claimed | rStation paper 3 (METADATA_ONLY via listing) | unrefereed |
| n <= 20 | claimed 9-colourable | rStation paper 18 Cor. 4, SRC-0047 (STATEMENT_INSPECTED, S029) | combines papers 1,3,4,6,16; author LRAT/DRAT; not replayed |
| n = 21 | claimed partial | paper 33, SRC-0046: a 10-critical biplanar graph on 21 vertices has alpha=3; paper 64 v7, SRC-0068 (STATEMENT_INSPECTED): order-21 analysis of a minimum 10-chromatic biplanar graph citing alpha=3, omega<=8, delta>=9, e<=114, with Theorem 4 closing stated orbit branches under stated hypotheses | paper 64 itself says the unrestricted problem remains open; order 21 is NOT closed in any inspected source |
| n = 22–23 | open | post 49 (METADATA_ONLY): density-feasible alpha=3 blow-ups, K9-linked | candidate scans, not closures |
| n = 24–27 | open | none found | — |
| n = 28, alpha <= 3 (OP1(b)) | open | paper 59, SRC-0045: 11-regular excluded (RUP replayed in S030); post 168, SRC-0069 (STATEMENT_INSPECTED): 22 sampled delta=10, m=156 graphs all non-biplanar (DRAT); post 155 twinned slice partial | post 168 is a sample, not the class; programme S030/S031 delta=11 strata UNKNOWN |
| alpha <= 2, any n | proved 9-colourable, n <= 18 | Szeider, SRC-0037 (STATEMENT_INSPECTED) | Lean-checked enumeration assuming three planar facts; not replayed |
| alpha <= 3 | n <= 28 claimed | paper 59 (hand, imports SRC-0037); n <= 30 conditional on SRC-0037 (CLM-0111) | — |
| C5 clique blow-ups | biplanar ones 9-colourable | Trivedi SRC-0012; programme CLM-0090..0105 | family result |
| biplanar line graphs | claimed 9-colourable | paper 13 (METADATA_ONLY via listing) | — |
| fractional chromatic number | max chi_f = 9 among about 102 verified biplanar graphs | post 171, SRC-0070 (STATEMENT_INSPECTED) | search-limited census, not a bound |
| arbitrary n >= 21 (except the above slices) | open | Epoch AI SRC-0065; no announced chi>=10 biplanar graph found | — |

## Method prior art

- SAT modulo planarity with lazy Kuratowski clauses: SRC-0038 and the bipsat2
  implementation SRC-0055 (our native core is derived from it).
- Colouring-partition feedback is a co-certificate learning loop: a 9-colouring
  certifies failure of the target co-NP property and becomes a learned clause.
  This is the method of Kirchweger, Peitl and Szeider, "Co-Certificate Learning
  with SAT Modulo Symmetries", IJCAI 2023, SRC-0071 (METADATA_ONLY: search
  summary only), used there for Kochen–Specker systems. CLM-0146 is an
  elementary encoding lemma, not a novelty claim.
- SAT modulo symmetries (Kirchweger–Szeider) gives complete isomorph rejection
  by a minimality-check propagator. It was not run: CaDiCaL accepts one external
  propagator and ours is the planarity propagator (registered BLOCKED arm).
- Static lex-leader graph symmetry breaking: Codish, Miller, Prosser and
  Stuckey, "Constraints for symmetry breaking in graph representation",
  Constraints 24 (2019), SRC-0072 (METADATA_ONLY). Our CS rule is proved
  self-contained in RESEARCH.md; attribution, not adoption of their theorem.
- 10-critical structure: minimum degree, connectivity, no cut vertex are
  classical (proved in RESEARCH.md); Kostochka–Yancey edge bound SRC-0011
  (STATEMENT_INSPECTED) is recorded but not encoded.

## Admission consequences for target selection

No inspected source excludes any order in the registered spread 24/28/32/40/50,
even by unverified claim. If the forum closures of n <= 20 are correct, the
smallest witness has at least 21 vertices; S046 does not adopt that as a filter.
Orders 21–23, 25–27, 29–31, 33–39 and 41–49 are not searched by the pilots and
remain open within the programme. No parked star/patch, apex or nine-S11 route
is revived. No source supports a novelty claim for any S046 output.
