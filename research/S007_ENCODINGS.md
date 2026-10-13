# S007 necessary encodings and independent global challenge

The target is exact thickness-two chromatic number. No SAT relaxation is a planar witness. The completion premise is the classical planar augmentation fact, also inspected in SRC-0009(X2). The existing Cover necessity/lex proof (CLM-0028) remains the starting point; arbitrary deficits permit shared pairs and edges outside the input.

## StrongCover necessity at any deficit

For any genuine biplanar n>=4 input, independently complete its two planar layers to sphere triangulations on the same vertex set. For every vertex set S, a completed layer induced on S is simple planar and has at most3|S|-6 edges when |S|>=3. StrongCover uses every union of closed-twin bags and every one-vertex complement as selected necessary instances of this inequality. It also forbids monochromatic input K5s, because each layer is planar. Neither set of cuts claims a complete planarity characterization. Vertex sets of sizes0..2 are deliberately omitted from the Euler3s-6 formula. Auxiliary cardinality variables admit every primary solution obeying those inequalities.

The existing common-order layer-swap/input automorphism lex constraints are sound by selecting the lexicographically least primary edge vector among all completed solutions in its symmetry orbit. Listed permutations are checked as input automorphisms. The extra cuts are true in every actual planar completion, whether or not the chosen bag partition is invariant under a permutation. No isolated first-edge unit from Cegar is inserted into Cover. Connectivity/link cut syntax and necessity remain as in the original Cover. A lack of a satisfying relaxed model requires an actually checked DRAT proof before any exclusion; a satisfying model still needs both actual layers/rotations and all colouring obligations.

## Distinct global faces for D<=2

For input edges E and completed layers T1,T2, let o(e) in{0,1,2} be occurrence multiplicity. Input pairs have o>=1. The exact surplus identity is

    D=6n-12-|E|=sum_(e in E)(o(e)-1)+sum_(e notin E)o(e).

If the same labelled triangle is facial in both layers, each of its three pairs has o=2. Each input pair costs one surplus, and each noninput pair costs two. Thus D>=3. Therefore when D<=2, the two sets of facial triples are disjoint. This proves the new extension beyond the inherited D<=1 shortcut; it NEVER permits a distinct-global-face premise at D>=3. D3 can have three doubled input pairs forming a common face; no contrary assertion is made.

For D=2, combine the two actual facial sets into a single0/1 selection. Every pair has exactly2o(e) incident selected faces. Input pairs have one surplus bit, noninput pairs two monotone multiplicity bits; total surplus is2. A selected triangle has at most two noninput pairs, since three already cost>=3. This yields the separate no-lex global incidence CNF. The converse is absent: layer consistency, connectivity and vertex links are deliberately forgotten. Its SAT assignments cannot decide biplanarity. It shares the classical completion premise, PySAT library and native solver with other encodings; its independent numbering/no symmetry and direct projected-incidence counts are separate checks, not external formal verification.

## Controls, scope and trust

Before new verdicts, all40 retained full S005/S006 refutations and K9/row165 were cold regenerated and freshly native-checked. All271 chromatic archive/CNF hashes and explicit10-colourings were audited; exactly the four D2 targets' lower proofs were freshly checked. The23 positive examples were run through the stronger model and independently checked as exact disjoint splits with two sphere rotations. A further23 actual completions were pinned against StrongCover, checking every primary constraint admits suitable auxiliaries.

Those23 examples do not by themselves exercise the D<=2 premise. Three exact D2 deletion controls on the known42-vertex disjoint-triangulation witness independently checked actual rotations/triangular faces and every global face/multiplicity bit against the new CNF. These exercise two new noninput pairs; they do not establish test coverage of every possible D2 overlap type. The all-order surplus proof, not the controls, establishes necessity for every type.

The four global D2 models were independently cold regenerated. Every native SAT assignment satisfied every generated clause, then a direct count checked pair multiplicities, coverage, total surplus2 and selected-face count4n-8. Their projections and native logs are retained. All four are SAT_RELAXATION, leaving biplanarity UNKNOWN. They show that surplus/distinct global incidence by itself fails on these four targets.

The four full-layer searches have a separately registered900/920s budget and a two-final-UNKNOWN stop rule. Exact observed outcomes are in validation/S007/search_results.json and SUMMARY, not inferred here. Caps/NOT_RUN never count as a negative result. The original D2 stratum contains42 rows; selecting four does not exhaust it. No smaller/minimality/containment theorem or full k8/k9 census is claimed by this encoding work.

The separate heavy K7-I5 Kuratowski challenge has no sphere premise: every actual planar partition forbids each monochromatic checked K5/K3,3 subdivision. It retains checked input automorphism lex plus a first-edge layer-swap unit in a consistent original-edge order. Every retained lemma is structurally checked and independently nonplanar by LR; its CNF is byte-regenerated before proof acceptance. Partial syntactic lemmas are not a refutation. That local graph is8-chromatic, so even a planar split is not a chi>=10 witness.
