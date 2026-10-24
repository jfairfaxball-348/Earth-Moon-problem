# S042 adversarial audit

No subagent or external review is claimed; this is the executor's own
falsification and replay.

- Order: PLAN hashed 13:35:57Z before any census output; the type table was
  written by the first run, which was then stopped for cost (about 900 CPU s,
  counted). The addendum (symmetry reduction, PARTIAL Ore members of
  unresolved types, CEGAR-first order) was hashed at 13:48:22Z before any leaf
  output. Two restarts failed immediately (an escaping error; a node-label
  bug after the reduction control); no decision was produced by either.
- Completeness rests on Gallai's join theorem (SRC-0027), Kostochka-Yancey
  including Theorem 6 of SRC-0020 (statement-level access), the Aut(K_k)
  reduction (proved; controlled on 6-Ore/11 and 7-Ore/13) and isomorphism
  deduplication (WL buckets plus VF2; independently replayed by VF2-only
  mapping). The census is complete only for the RESOLVED types listed; thirty
  UNRESOLVED non-Ore windows are named, not excluded.
- The leaf lemma covers Hajos composites and edge-deleted DHGO operands; a
  vertex-split operand is not covered. Non-composite chi9 graphs H (K1vH
  direct) lie in the UNRESOLVED windows when small; larger ones are untouched.
- Every negative is a DRAT-verified UNSAT with full clause re-justification;
  no Kuratowski lemma was needed, so the refutations rest on Lemma B/C and
  K9 non-biplanarity (CLM0022). No cap, timeout or heuristic plateau was used.
- Archive: CNF and lemma files (234 MB) are kept locally and pinned by SHA-256;
  they regenerate byte-identically from committed edge lists (checked for every
  leaf by the local verifier, which also re-runs drat-trim on the committed
  DRAT). CI verifies hashes, receipts, the type table and small families, not
  DRAT itself.
- PARTIAL results (three 16-vertex leaves from 7-Ore/13) do not resolve their
  type; the 42-43-edge non-Ore window remains open.
- The D077 gate was fixed before computing and is not relaxed: negatives are
  learning, not progress.

Frozen S036-S041 artifacts and sources unchanged; S036 stopped.
