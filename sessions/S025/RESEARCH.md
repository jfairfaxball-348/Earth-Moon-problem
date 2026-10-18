# S025 RESEARCH — what was actually found

The full dossier is research/S025_C5_OBSTRUCTIONS_CORPUS_CLOSURE.md. Campaigns: CAM-0027 (Arm A), CAM-0028 (Arm B engines and classification), CAM-0029 (exact refutations and transfer). Permanent evidence is in validation/S025.

## Headline outcomes
1. **Original corpus closed.** All 219 BIPLANARITY_UNKNOWN rows of the original 271 exactly-χ10 clique blow-up corpus contain a DRAT-certified non-biplanar 17-vertex C5 clique blow-up as an explicit subgraph. So the whole corpus is NON-BIPLANAR (CLM-0094). Row148, the sole active target of S018–S022, contains C5[2,5,2,6,2] on its bags 3,4,5,7,6. The settling obstructions were:

   | Obstruction | Rows settled |
   |---|---|
   | C5[2,5,2,6,2] | 189 |
   | C5[2,3,4,2,6] | 21 |
   | C5[2,2,5,3,5] | 6 |
   | C5[1,4,4,4,4] | 3 |
2. **C5 threshold.**
   - Every K9-free C5[a] with Σaᵢ ≤ 16 is biplanar: 262 classes, explicit checked splits.
   - Every certified Σaᵢ = 17 class is non-biplanar.
   - The iff-classification awaits the remaining Σ=17 classes (list in C5_CERTIFICATES.json and CAM-0029).
3. **New exact technique.** Cross-layer K9-minor lemmas (Lemma B, and especially the single-layer Lemma C) turn a stalled Kuratowski CEGAR into minutes-scale refutations of 17-vertex blow-ups. Every clause is independently re-justified, and every CNF is regenerable byte-for-byte and DRAT-checked.
4. **No χ ≥ 10 witness.** Arm A's chromatic-certificate frontier (weighted independence over triangulation pairs) stays far from the χ ≥ 10 range at the sizes tried: α≤3 reached n=24 (need 28), α≤4 reached n=32 (need 37), W=3 total 28 at ≥8 bad sets. All of this is heuristic.

## What failed or was retired
- F069: colouring-CEGAR over triangulation pairs.
- F070: the complete triangulation-cover SAT (S024 spec) as a refutation engine; validated but too weak.
- F071: local RAM oversubscription.
- F072: Lemma B alone.
- The overlap-only objective of S024 stays retired.

## Status after S025
- Original 271 corpus: **271 NON-BIPLANAR** (52 certified earlier, 219 in S025).
- Classical **9 ≤ χ₂ ≤ 12**, unchanged.
- No new candidate is known to be biplanar with χ ≥ 10.
