# S003 preregistered scope (written before any S003 mathematical computation)

## Prior-art reconnaissance done first (read-only)

Before choosing routes we inspected Patil's public repository
(github.com/Volkopat/earth-moon-biplanar, commit 5cb2ca9f, paper/earthmoon.md)
and Doria's Zenodo record 10.5281/zenodo.21824308. Consequences:

- Small-order Gallai-join attacks (n<=18) are already pursued in depth by
  Doria (n>=17, census-conditional) and Patil (n>=17 certified; n>=19 modulo
  named windows). S003 will NOT duplicate that route.
- Patil Observation 7.1.1 gives n>=89 for 12-chromatic biplanar graphs
  (KY Brooks-type refinement), strictly stronger than S002 CLM-0011 (n>=78+11D
  for D=0). S002 missed this; S003 must record the overlap/supersession.
- Patil lists as open: thickness of apex(C5[K3]) (16v/75e) "strong evidence
  theta=3, unproven"; and the {1,9}-apex lane. Their thickness verdicts use
  SAT-modulo-symmetries with planarity theory lemmas taken as axioms.

## Goals (several substantial routes)

A1. Build a *purely propositional* proof-producing biplanarity decision
    procedure: CNF whose satisfiability is equivalent (via Schnyder's
    theorem: G planar iff G has dimension <=3) to biplanarity; UNSAT proofs
    in DRAT checked by drat-trim, with no theory-lemma axioms. Validate the
    encoding in both directions against an independent planarity test.
A2. Use it on the non-saturated universal-apex route: for every 9-chromatic
    graph H of Patil's public 241-graph corpus with e(H)<=5|H|-6 (the Euler
    precondition for apex(H)), decide biplanarity of apex(H) (a 10-chromatic
    graph if chi(H)=9). Any SAT verdict would be a candidate chi>=10 witness and
    would trigger independent layer checks plus a certified non-8-colourability
    proof of H and full cold audit. Also attack apex(C5[K3]).
A3. Mathematics of face covers: exact characterization of biplanar apex
    graphs; a face-deficit bound on edges with fewer than two common
    neighbours generalizing the saturated bridge obstruction; test against
    named families (apex Hajos towers).
B.  Upper bound through criticality: examine the low-vertex Gallai-forest
    structure of 12-critical biplanar graphs together with the two layers;
    attempt a reducible configuration; if it fails, construct the explicit
    obstruction and isolate the surviving obligation.
C.  Any bridge that emerges (e.g. certified-oracle construction search).

## Stop criteria and honesty rules

A universal claim needs a complete quantified proof. A CAM verdict is only
about its registered fixed graphs. UNSAT is used only with a drat-trim
VERIFIED certificate on a CNF regenerated and hashed by the registered
generator. A feasible colouring is only an upper bound. No S004 execution.
Computation is registered in campaigns/CAM-0003.md.
