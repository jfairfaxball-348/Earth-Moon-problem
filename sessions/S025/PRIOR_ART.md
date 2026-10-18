# S025 PRIOR_ART — status 2026-10-16

- **[SRC-0005], [SRC-0014]** Classical Euler bounds and K9 having thickness 3 (Battle–Harary–Kodama 1962; Tutte 1963).
  - Every S025 negative depends on K9's thickness 3.
  - Programme copy: S003 DRAT certificate, re-verified in today's local smoke (retained and fresh proofs).
- **[SRC-0041] NEW, METADATA_ONLY.** D. Eppstein, *On the Biplanarity of Blowups*, arXiv:2301.09246 (2023).
  - Seen only in a search excerpt: it disproves Gethner's conjecture that 2-blowups of planar graphs are biplanar.
  - Relevant prior art on blow-ups and biplanarity. Not opened, not compared in detail.
  - Its blow-ups are of planar graphs. Ours are clique blow-ups of C5, a different family as far as the excerpt shows.
- **[SRC-0014] (existing, PROOF_INSPECTED in earlier sessions).** Biniaz, *A short proof of the non-biplanarity of K9*, arXiv:2008.05186. It is the literature source for the K9 dependency of Lemmas B and C.
- **[SRC-0037]/[SRC-0039]** Szeider 2026 (α ≤ 2 ⇒ 9-colourable), STATEMENT_INSPECTED / METADATA_ONLY as before.
  - Our α≤2 annealing minima (0 at n=16; 1 and 2 at n=17, 18) are consistent with it. They neither reprove nor test it.
- **[SRC-0038]** Kirchweger–Scheucher–Szeider 2023. SAT planarity methodology, eager and lazy Kuratowski: prior art for our CEGAR backbone.
- **S004 (programme history).** Counted the same 297 feasible C5 orbits and left the frontier UNKNOWN at 120 s caps. S025 reproduces that count independently.

**Search performed.** Two web searches (thickness of C5 clique blow-ups; contraction/K9 arguments for thickness two, 2026). Neither returned a classification of C5[K_a…] thickness or the contraction Lemmas B/C. That is weak evidence only; a dedicated literature search remains an owner-gated novelty-audit task.

**Novelty: NOT claimed.** Contracting connected sets to obtain K9 is classical in spirit; Lemma C may well be folklore. The C5 threshold statement has had no priority check beyond the two searches.
