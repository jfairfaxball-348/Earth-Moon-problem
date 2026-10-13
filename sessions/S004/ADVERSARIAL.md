# S004 adversarial and integrity pass

Internal review by the same agent using distinct checks; no independent
human or external mathematical review is represented.

* Face encoder: completion edges must be allowed outside the input. The
  excess identity counts both noninput occurrences and doubled input edges,
  so it does not smuggle in the false assumption of an exact input union.
  Triangles imply edges only; separating triangles need not be faces.
  All lex inequalities use one primary-variable order. There is no
  additional first-input-edge unit that could conflict with this order.
  Small n<4 is explicitly outside the domain. Cuts with repeated vertices,
  out-of-range indices, v on its cycle, w on its cycle, w=v, empty/all-vertex
  connectivity sets were rejected. 100 seeded positive controls, Sulanke
  and K9-e passed with actual rotation checks; K9 DRAT checked.
* CNF regeneration shares the face generator and cardinality library;
  this is not claimed as an independent second encoder. K9 known theorem
  and positive controls calibrate it; the short written necessary-condition
  proof and all code remain part of the trust base. No formal certification.
* Four apex refutations have a separate much shorter check: explicit K9
  subgraphs. Entire pool exclusions use the actual label set; source graph
  19_12v_57e_w2 omits label 2. Adding an invented isolate before taking an
  apex would change the graph, so it was not done.
* Every one of 271 survivors: independently checked F1/F2/F3, bag and
  vertex 9-colour CNFs refuted with DRAT, and an explicit proper vertex
  10-colouring checked. No feasible colouring is used as a lower bound.
  Archived bag proofs are retained; vertex proofs remain regenerable
  scratch with hashes. Full k=8 completeness was not independently checked;
  two fixed bases were each audited through all 8^8 vectors only.
* The Kempe-lock graph is 4-chromatic and not critical for 12 colours. It
  refutes an unconditional one-swap extension statement. It cannot refute
  multi-swap reducibility, criticality-based lemmas or the D<=11 case.
* Solver caps: soft limits are tested between solves, so hard supervisor
  limits are also imposed. Some 120 s runs stop at 130 s and the short-link
  run returned after 608.516 s. These are actual observations, not exact
  nominal timing claims; every unresolved run stays UNKNOWN. Packing search
  is heuristic and missing edges are not a non-biplanarity proof.

## Detected implementation/protocol issues

1. The first Windows PySAT proof export failed drat-trim (no conflict;
   forcing a terminal empty clause also failed). It was never trusted.
   Export details are not diagnosed conclusively. Pinned standalone
   CaDiCaL was rebuilt; its complete text proof verified. The first MSVC
   checker build needed a time shim/getc replacement; the accepted proofs
   use the later MinGW build of upstream drat-trim, with only the command-line
   getc_unlocked=getc portability definition. No proof-checking logic edited.
2. CaDiCaL manual Windows build required the separately compiled kitten.c,
   NUNLOCKED, and compiler runtime DLLs; first failed builds are documented.
3. A one-line apex-input preparation command had a syntax error. The first
   apex search then exited on missing input; no verdict or result was used.
   Preparation was replaced with an explicit reproducible relabelling loop.
4. Redundant apex Kuratowski work was interrupted after all four K9
   subgraphs were found. Interrupted work is UNKNOWN, not a second checked
   verdict. The face proofs and K9 subgraphs provide the actual exclusions.
5. S003's v4 checker compares newline-normalised text. On Windows a fresh
   v4 CNF has CRLF; S004 explicitly regenerated LF replay bytes and checked
   the original S003 SHA-256 79b87f88... before standalone DRAT. The new face
   encoder and its checker use explicit LF and raw byte comparison.

No citation, graph embedding, proof certificate, hash, hosted result or
outgoing GitHub reference has been anticipated. Publication remains gated.

## Later certificate challenge

The C-runtime flush repair produced a complete K9 proof that VERIFIED;
the full-survivor proof from this repaired Cadical153 path also VERIFIED.
The original 60 s proof cap was extended by preregistered Amendment F;
the standalone 600 s retry VERIFIED too. The independent direct-incidence
encoder with no lex constraints found a relaxed SAT model, not an embedding:
layer 0 is non-planar with four disconnected links, and layer 1 is
non-planar/disconnected. Its ten positive controls passed. Thus the finite
negative verdict was not independently reproduced by this second encoder;
the first generator's necessary-condition proof, valid symmetry/cut
argument and checked refutations remain the evidence. Fixed non-orbit-closed
cut lists can admit false models without lex constraints; no SAT relaxation
is being called a biplanar construction. This limitation is explicit.

The compact core proof extracted from the verified bundled-solver proof
was itself checked against the full CNF and VERIFIED. Its compressed archive
was decompressed and compared byte for byte before replacing the larger
archive. Original proof hashes/logs and reproduction commands remain.
The governance checker initially used Windows' locale decoder on the newly
UTF-8 catalogues; its readers now explicitly use UTF-8 and the local scaffold
check passed. Failed preparation/patch attempts produced no accepted
mathematical results. Text LF policy preserves portable artifact hashes.
