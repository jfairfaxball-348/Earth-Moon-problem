# S011 RESEARCH — three executed lanes and hand proof

Full proof, values and warnings in [research/S011_CONSTRUCTION.md](../../research/S011_CONSTRUCTION.md). Reproducibility references in [validation/S011/SUMMARY.json](../../validation/S011/SUMMARY.json). Exactly S011 executed; all native computations on dedicated GitHub Actions runners after full D043 smoke PASS (271/271 archived chi proofs and byte-matching CNFs, K9 and fresh K9 refutation).

**CAM0012**: run38623187997, 219 fixed biplanarity UNKNOWN graphs, two positive random greedy layer-construction trials each (438 total),25 partial repair checks. None yielded an edge-disjoint complete planar split. Best row15624v128e needs11 still-unplaced edges. This cannot exclude row156 or any of219; none reclassified.

**CAM0013**: run38623722547, fixed rows2,55,59,61,199,200; 40 selected edges per graph, 240/240 exploratory 9-SAT successes on G-e, zero edges deleted preserving certified10, no split. This is NOT itself a proof of each graph's full edge-criticality; CAM0014 addresses that independently.

**CAM0014**: run38624616691, full source-scoped census of all863 edges on six fixed labelled graphs. For every G-e an explicit proper nine-colouring recorded. Separate stdlib checker freshly expands the graph6 base, independently checks proper10 of original graph and all863 9-colourings on G-e and deleted-edge monochromatic property; PASS for six complete rows. Paired with cold 271/271 S004 verified non9 proofs, establishes CLM-0070: six graphs exactlychi10 and edge-critical. Raw JSON SHA256 ca6d78fb348c4647be916d5907df03ef03ddbee93418a5981f4f1e3bf99424e1; permanently preserved as `validation/S011/edge_critical_witnesses.json.gz` SHA256 d43bfe323a52666a7811630f8cff549e7eed8fd8b628f2ff6a1cf84cbf26e554, not dependent on temporary artifact downloads. This finite result is a construction filter, not biplanarity or priority certification.

**Independent mathematics**: CLM-0069: if chi(G)>=9, choose 9-critical induced H, delta(H)>=8, |E(H)|>=4n; ordinary Mycielski M(H) has2n+1 vertices and3m+n>=13n edges, violating biplanar Euler bound12n-6; M(H) induced in M(G), so M(G) not biplanar. K6 join C5 example M has23v161e >126. This rules out that specific lift route, not other vertex splittings.

**Headline** unchanged: no explicit chi>=10 biplanar labelled split; `9<=chi_2<=12`. None of219 UNKNOWN rows excluded and no new exact universal colouring theorem. A complete four-fold construction certificate is still required.
