# S011 — lower-bound-only construction investigation (2026-10-14)

## Governing target and result

Construct a finite simple graph of thickness <=2, chromatic number at least10, with explicit E1/E2, rotations/Euler and a cold checked proof of no9-colouring. **NO SUCH WITNESS FOUND IN S011**; 9<=chi_2<=12 unchanged. The fixed S003 pool is still 52 confirmed non-biplanar of271, with219 biplanarity UNKNOWN.

## CAM-0012 — direct *positive* split search, not exclusion

Hosted run https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/38623187997 on WIP head99df83c. The D043 cloud toolchain built and same-job smoke PASS (271/271 non9 DRAT, 271/271 CNF byte matches, K9 retained and fresh proof checks). Two greedy randomized edge-disjoint planar-layer constructions on every one of the219 UNKNOWN original graphs: **438 trials**, 25 best partials subjected to a one-edge transfer repair; **no full split**. Best partial row156 is24v128e with11 original edges unplaced; runner wall of scientific work58.08s. All219 remain UNKNOWN; 0 exclusions. Explicit successful graph only could advance headline, and none was found. Artifact ID11923795092, zip SHA256 6eb2e9ab4e454a3d97c9a73dbcb0210a43c14d1455ef9d3ef130b96d904fc776.

## CAM-0013 — experimental edge deletion

Hosted run https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/38623722547, WIP b5ae360. Registered exact six lowest-density indices [2,55,59,61,199,200]; for each, 40 sampled edges. All **240 of240** single-edge deletions reported SAT with a9-colouring (exploratory in this lane); zero edges tentatively removed, no complete planar split. Each six graph remains biplanarity UNKNOWN; no edge deletion is an exclusion certificate. Runtime16.91s. Artifact11924345243, SHA256 82cc4c73144da4619ba62b4c1bff4de806c5ec1bf948d79cd0fa91437d75c1ec.

## CAM-0014 — six full edge-critical certificates (CLM-0070)

Hosted run https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/38624616691 on WIP head96810e6. Same-job mandatory cold smoke PASS. Enumerated **every** edge of each of these six exact-chi10 graphs: rows2 has n26,m133, and rows55,59,61,199,200 each has n28,m146; total **863 edges**. Independently re-expanded graph6 bases without NetworkX, checked original proper10 and every one of **863 explicitly recorded proper9-colourings** on G-e; each deleted edge itself is monochromatic, consistent with the cold-checked original non9 proof. Independent stdlib checker `tools/s011_edgecheck.py` returned PASS, all_six_complete=true. This proves each *fixed* graph is 10-edge-critical: any proper edge-deleted subgraph is 9-colourable. Does not prove any is biplanar or exclude any of the219; does not generalize to the whole candidate pool. Archive validation/S011/edge_critical_witnesses.json.gz SHA256 **d43bfe323a52666a7811630f8cff549e7eed8fd8b628f2ff6a1cf84cbf26e554**, decoded witness JSON SHA256 ca6d78fb348c4647be916d5907df03ef03ddbee93418a5981f4f1e3bf99424e1. GitHub artifact ID11923611772 SHA256 dafd52da91486e7adbb2d633564f2bac2753d4cbf9b06a6ab07ec97613f278ae. Preservation run https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/38625149681 redownloaded/checksummed/rechecked and committed deterministic gzip to never-merged WIP before final session integration.

## Hand proof: ordinary Mycielski lift is impossible (CLM-0069)

Write M(G) for the standard Mycielski construction: original n vertices, a clone of each, one root; retain every original edge, add two original-clone edges per original edge and n root-clone edges. Hence |V(M(G))|=2n+1 and |E(M(G))|=3m+n.

If chi(G)>=9, choose an induced vertex-minimal subgraph H with chi(H)>=9. Removing a vertex decreases chromatic number by at most one; thus chi(H)=9 and H is vertex-critical. Consequently every vertex has degree at least8, so m(H)>=4n(H). Thus M(H) has 2n+1 vertices and at least 13n edges. But any biplanar graph on 2n+1 vertices has at most 2(3(2n+1)-6)=12n-6 edges. Since 13n>12n-6, M(H) is not biplanar. The construction on induced H is an induced subgraph of M(G), and thickness<=2 is subgraph-closed; M(G) is therefore not biplanar.

Adversarial checks: count *both* clone edges per original edge; root contributes n; choose a **vertex**-critical 9-chromatic H, not an arbitrary 9-colouring of G; apply Euler bound to the induced lifted H, not necessarily the whole G. No assumption that M(G) itself has exactly10 colours is needed. Example Sulanke K6 join C5 has n11,m50, M has23v161e, exceeding126 allowed by35. This elementary filter likely overlaps existing density machinery; novelty UNCHECKED. It neither proves 9-colourability for all biplanar graphs nor provides a headline.

## Research significance and limits

The entire inspected direct heuristic is nonexhaustive and has no negative semantics. The six fully edge-critical finite instances establish a genuine checked property but by itself only closes plain sparsification on those six. A promising S012 source is **chromatic-restoring edge swaps G-e+f**, complete layer-aware repair, or direct pairs of planar graph layers. Any future χ>=10 candidate requires fresh, independent non9 LRAT/DRAT plus actual labelled E1/E2 and sphere rotations; prior χ10 proofs on the original graph do not automatically transfer to a modified graph. All downstream gates remain unpassed.
