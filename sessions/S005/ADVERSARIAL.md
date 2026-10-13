# S005 adversarial and integrity review

Internal review by the same agent using distinct generators and checkers;
no independent external reviewer or formal certification is represented.
No universal colouring theorem was obtained, so its independent adversarial
review gate was not bypassed.

## Mathematical challenge

* The exact target remains chi_2 of all finite simple biplanar graphs.
  Seventeen D=0 exclusions are a stratum of one fixed 271-row blow-up list,
  not a universal saturation theorem. Additional D=1 exclusions are likewise
  finite. Chromatic numbers come from separately certified non-9-colourability
  and proper 10-colourings, never from a feasible colouring alone.
* Completion edges outside the input are still allowed. D=1 means one
  surplus occurrence, which may be a new edge or a double input edge. Both
  cases have actual positive controls. Distinct selected facial triangles
  follow only because D<=1; the 0/1 argument was not extended to D>=3.
* The small D=0 layer relaxation deliberately omits connectivity, cyclic
  links and positive layer degree. Several models satisfy it while the
  stronger necessary Cover is refuted. These are compatible observations:
  relaxed SAT is not a planar witness. No converse is asserted.
  The cached-model audit directly checked every clause and triangle-edge
  incidence for all 17 relaxed models. Each of the eight displayed layer
  models has multiple isolates in both layers and structurally checked
  Kuratowski subdivisions: actual false-converse evidence.
* Lex-leader constraints use one total primary-edge order; every vertex
  permutation is checked to preserve the input graph. Each sphere completion
  orbit has a least representative that survives. Fixed cut lists need not
  preserve all relaxed models under automorphisms: their soundness follows
  from each cut being true in every genuine sphere completion. No extra
  conflicting first-edge symmetry unit was introduced in Cover.
* Link/connectivity cuts are syntactically validated during cold regeneration.
  Second-encoder Kuratowski cuts independently check the stored subdivision
  by suppressing degree-two paths; they may use completion edges. A timeout
  or nonplanar relaxed model has no negative or positive biplanarity verdict.
* Separate reduced generators omit lex and use different variable numbering;
  the full second incidence encoder uses direct face clauses/totalizer edge
  counts. They share classical completion premises, Python/PySAT and the
  native proof checker. This is separate implementation, not external review.
* The new Gallai block bound needs Delta<=11. Removing this hypothesis is
  false: two K8 blocks sharing one vertex have l=15,c=1,e=56, exceeding
  (31/8)15-3=55.125. Their shared vertex has degree14. K7/K8 blocks are
  vertex-disjoint under the actual degree hypothesis; contraction then uses
  the block-incidence forest, including singleton components. The critical
  application explicitly depends on source-stated Gallai's theorem.
* The two Kempe swaps resolve only the explicit S004 gadget lock. The graph
  is4-chromatic, far from12-critical. The high-subgraph deficit and compulsory
  palette equalities supply no reducible configuration and no upper bound on
  counterexample order. Palette equality is not actual-neighbour equality;
  layer-switching chains still defeat a copied planar separation argument.

## Computational and protocol challenge

Cold baseline: K9 and row165 completion CNFs reproduce byte-for-byte; both
archived DRAT certificates VERIFIED; row165 bag chromatic proof VERIFIED;
all271 upper colourings, bag-CNF hashes and public proof hashes audited.
First Cover had23 positive controls; second incidence13; reduced D=0 had
eleven relabellings of one actual42v witness; D=1 had actual new-edge and
doubled-edge controls. Label relabellings are not independent graph families.

Every accepted full search has its CNF regenerated and original DRAT checked.
Extracted compact proofs are checked afresh against the original CNF before
public replacement. Public compression is checked by decompression/hash and
fresh generator comparison. General and restricted embedding maps are expanded
and checked independently on every obstruction edge. Negative embedding SAT
results lack certificates and are only failed transfer attempts.

Detected issues, preserved without accepting affected outputs:

1. Windows CaDiCaL rejects -t. Four reduced solve processes failed immediately;
   failed_option_results.json/log record them. Retry used an external180s cap,
   with no formula change. No failed-option process is a mathematical result.
2. A first machine entry capture used git/commits/main, an endpoint requiring a
   commit SHA. It returned no sha and the assertion stopped before writing.
   Correct branches/main API capture then verified the unchanged entry main.
3. The first long worker stopped during row179's proof export; process/tool
   inventory at13:42:05 UTC had no remaining worker and unavailable supervisor.
   Cause UNKNOWN. Partial proof size/hash and UNKNOWN status were preserved;
   resumed solve overwrote only scratch proof and needed a fresh checker verdict.
4. Early supervisors enforced wall time, while private memory was observed only
   by snapshots. Later supervisors continuously observe descendant private memory
   and kill trees at12GiB or the wall cap. Do not retroactively claim continuous
   memory monitoring. Windows inventory after timeouts found no orphan challenge.
5. The general embedding supervisor used a7s total cap including encoding and
   startup; a separate5s in-solver limit was not available. No uncertified
   negative or timeout was promoted. Exact commands and actual times are retained.

Novelty, full k=8/9 census, C5 classification, independent external archive
replay and universal improved colouring remain open. Only S005 is executed.
No Lean, Palomar, publication, announcement, arXiv, journal or outreach.
