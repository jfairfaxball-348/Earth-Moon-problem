# S002 primary-source frontier and overlap audit

Searches on 2026-10-12 covered Earth–Moon, biplanar, thickness two, critical
graphs, cycle substitutions, Empire/map colouring, source titles/DOIs and
recent 2026 records. This is a scoped session audit, not an exhaustive
novelty guarantee. Classical and current 9–12 bounds remain intact.

SRC-0002: retrieved author-hosted 12 September 2007 preprint of the 2008
paper, https://academics.hamilton.edu/mathematics/dboutin/ThicknessTwo.pdf.
Read the permuted-layer/Hajós/Catlin arguments and visually inspected
Figure 3. Recovered both actual layers; not all forty catalogue graphs
were independently audited. Publisher edition not fully compared.
SRC-0003: original Springer abstract inspected, full proof unavailable.
SRC-0016: Gethner's author-uploaded 2018 survey is accessible on
ResearchGate; sampled statements, not a complete proof audit.

SRC-0009: Szeider, arXiv:2609.28102v1, 23 September 2026. Textual proof
inspected: every biplanar graph with alpha<=2 is 9-colourable, so a
10-chromatic witness needs alpha>=3. The proof combines finite certified
exclusions and a matching reduction. It assumes classical planarity
facts, and uses compiled native_decide checks rather than only kernel
evaluation. We did not replay certificates. SRC-0010 primary archive:
10.5281/zenodo.22913639, version v1, contains Lean/certificate reproduction
files. Its stated trust base is preserved; no programme formal result
is claimed. The paper also gives the known C7[K4] cross-edge obstruction.

SRC-0007: OpenAlex W7204280229 resolved the indexed Patil work to concept
DOI 10.5281/zenodo.22103612. Its primary Zenodo API resolves to version
record 22103613, DOI 10.5281/zenodo.22103613, published 26 August 2026,
first/only indexed version, licence CC BY 4.0. Exact title is in the source
catalogue. Downloaded PDF and README; inspected Sections 3.3 and 3.3a and
verification limitations. Section 3.3 already proves our saturated cone
exclusion. The deposit supplies three refutation/encoding/lemma-log
triples; README explicitly leaves lex-leader independence unverified.
The 241-graph corpus is attributed to https://github.com/Volkopat/earth-moon-biplanar,
path data/graphs/pool/, not independently checked here. Reported SAT,
criticality and small-order claims remain SOURCE_STATED. No certification
claim from the abstract is adopted without its residual trust caveat.

SRC-0012: Trivedi, DOI 10.5281/zenodo.22074335, v1, published 5 August
2026. Primary record states the C5 weighted blow-up exclusion. We did
not inspect its complete PDF; keep access STATEMENT_INSPECTED. Our C5
proof is a reconstruction, not new. The all-odd-length weighted extension
has a complete in-repo argument but no defensible originality claim yet.

SRC-0011: Kostochka–Yancey primary Theorem 3 inspected, not its complete
proof rebuilt. It is an explicit external dependency for n>=78+11D.
SRC-0013/0015: stronger sparse/clique-free results retain k>=33 or
sufficiently-large restrictions; they cannot prove the desired k=12 case.
SRC-0014: Biniaz's six-page author PDF K9 non-biplanarity proof inspected;
its classical conclusion supplies the cycle-clique bound.

Release decision: no novelty gate, formalisation gate or publication gate
advances. Avoid already closed alpha<=2, C5 substitutions, uniform C7[K4]
and the saturated Hajós cone. Prioritise a genuinely different alpha>=3
mechanism and a criticality-specific universal colouring argument.
