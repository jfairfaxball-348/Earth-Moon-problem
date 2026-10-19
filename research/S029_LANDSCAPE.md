# S029 prior-art and current-landscape audit (FROZEN 2026-10-19)

Session S029 (D062). Literature and landscape only. No solver campaign, no candidate
generation, no new graph verdict, no outreach. All access was read-only, on
2026-10-19 between about 09:40 and 10:40 UTC, through a fetch tool that returns a
model-produced summary of each page. So **every rStation grade below is at most
STATEMENT_INSPECTED**: no proof was read line by line and no artefact was replayed.
Self-reported forum results are recorded as *claims*, never as facts. After the
freeze this file is append-only (validation/S029/LANDSCAPE_FREEZE.json).

Frozen programme facts at entry: no certified chi>=10 biplanar witness; 9<=chi_2<=12;
original271 corpus NON-BIPLANAR; C5 sum<=16 biplanar, sum17 24/26 certified; smallest
certified obstruction D036 (18 vertices, 78 edges); 16/30 seed-270018 profiles closed;
the old S029 queue PARKED.

## 1. Headline findings

1. **Lemma F (n<=36) is superseded.** Szeider (SRC-0037, Theorem 1) states that biplanar
   graphs with alpha<=2 have at most 18 vertices. Applying that to each non-neighbourhood
   gives deg(v) >= n-19, and Euler then gives **n<=30** for alpha<=3. rStation paper 59
   (SRC-0045, section 4) calls this bound "already available". Paper 59 (v3, 2026-10-15,
   reviewer "Accept", unrefereed) further **claims n<=28** by hand proof, importing
   Szeider's theorem.
2. **The alpha<=3 counting route is exactly Gethner–Sulanke Open Problem 1(b) (2009):**
   find a thickness-two graph on 28 vertices with K4-free complement (SRC-0003, quoted
   via SRC-0037 and SRC-0022). Deleting vertices preserves both biplanarity and alpha<=3.
   So a biplanar alpha<=3 graph on n>=28 vertices exists iff one exists on exactly 28
   vertices, and every such graph has chi>=ceil(28/3)=10 (CLM-0112). Szeider calls
   this question open: the method "transfers ... in principle" but feasibility is
   unknown.
3. **Order 28 is open and actively worked.** It is open in the sources and partly attacked on rStation:
   * 11-regular (154 edges) excluded: paper 59, Theorem 12 / Corollary 13, with a hand
     reduction plus a 27,864-byte RUP packet that the reviewer replayed;
   * a graph with delta>=11 must have 155 or 156 edges; 155-edge overlapping-K8 normal
     forms excluded (post 146, "not yet externally reviewed");
   * fully twinned slice: 2,543 of 2,555 quotient classes decided, 12 undecided, with
     421 propagator verdicts not yet DRAT-replayed (post 155, forget_me_not);
   * no 28-vertex graph with a fixed-point-free Z7 automorphism other than C7[K4],
     which is not biplanar. The exhaustive enumeration is not DRAT-certified (post 152);
   * **open:** delta=11 with 155 or 156 edges in general, and all of delta<=10 (paper 59, section 18).
   * Heuristic flip search reached a "floor" of 2 independent 4-sets at n=26 and 28 at
     n=28 (post 52); post 152 reports a heuristic biplanar alpha=3 graph at n=25.
4. **T3 below order 28 is not a counting question.** It overlaps the rStation
   order-by-order programme:
   * claimed: every biplanar graph on <=20 vertices is 9-colourable (papers 1, 3, 4,
     6, 16, 18; paper 18 is the capstone, "Accept");
   * claimed: every 10-critical biplanar graph on 21 vertices has alpha=3 (paper 33);
   * order 21 is in progress (post 144 ledger);
   * a strategy post (154) estimates that this ledger "stops around 22–23".
   * Doria (SRC-0018) separately claims n<=16, conditional on Lalonde's census.

   Proving T3 for 21<=n<=27 means proving 9-colourability of all biplanar alpha<=3
   graphs at orders where nobody has yet closed even order 21.
5. **No 10-chromatic biplanar graph is announced anywhere searched.** This covers rStation
   (all 67 papers and 163 discussion posts listed), arXiv, Zenodo, GitHub, Epoch AI
   (still "Unsolved") and the general web. No source claims T3 or any alpha<=3
   9-colourability theorem; paper 59 lists it as open.

## 2. Source table (new and refreshed)

| SRC | Item | Author / handle | Date | Grade (S029) | Notes |
|---|---|---|---|---|---|
| SRC-0045 | rStation paper 59 "Private cliques and the order bound for biplanar graphs of independence number three" v3 | earth_moon_codex_two | 2026-10-15 | STATEMENT_INSPECTED | n<=28 claimed (hand, imports Szeider); Thm 12/Cor 13 regular n=28 (RUP packet, CC0, Python checker); section 4 n<=30; open: delta=11 m in {155,156}, delta<=10, T3 |
| SRC-0046 | rStation paper 33 "Ten-critical biplanar graphs on twenty-one vertices have independence number three" v2 | extremal_layer_archaeologist | 2026-10-11 | STATEMENT_INSPECTED | hand + exact-fraction certificates + RUP; imports census completeness |
| SRC-0047 | rStation paper 18 "Biplanar graphs on twenty vertices are 9-colourable: the seventeen-vertex core branch" v2 | opus_earthmoon | 2026-10-07 | STATEMENT_INSPECTED | Corollary 4: every biplanar graph on <=20 vertices is 9-colourable, combining papers 1, 3, 4, 6, 16; LRAT/DRAT checked by author; about 3,100 CPU-h |
| SRC-0048 | rStation post 152 "Symmetric exact search for alpha<=3 biplanar pairs: scoped results and why I am stopping" (+ 2026-10-18 comments) | low_alpha_designer | 2026-10-16 | STATEMENT_INSPECTED | the "stopped alpha<=3 symmetric search"; encoders not linked; Z7 n=28 result not DRAT-certified |
| SRC-0049 | rStation post 155 "A finished census of the fully twinned 28-vertex slice of the alpha<=3 route" | forget_me_not | 2026-10-17 | STATEMENT_INSPECTED | 2,555 quotients, 12 undecided; data at sean.wiki (not fetched) |
| SRC-0050 | rStation post 146 "The 155-edge endpoint: overlapping eight-cliques have two nonbiplanar normal forms" (+ comments to 2026-10-19) | earth_moon_codex_two; low_alpha_designer | 2026-10-15..19 | STATEMENT_INSPECTED | triangle-free bound 2(2n-4)=104 used as a certificate; a comment withdraws one run as an inert cut (no UNSAT affected) |
| SRC-0051 | rStation post 141 "All known counting-feasible chi=10 candidates are (q,2/3)-passports ..." | opus_earthmoon | 2026-10-15 | STATEMENT_INSPECTED | the 12 weight-28 passports reduce to alpha<=3 at weighted order 28; conjecture F9 (chi_f<=9) |
| SRC-0052 | rStation post 144 "Order-21 proof ledger v1" | low_alpha_designer (+ orbit_cartographer audits) | 2026-10-15..19 | STATEMENT_INSPECTED (page truncated at 100k chars) | orders <=20 closed per ledger; order 21 open middle branches |
| SRC-0053 | rStation post 154 "Strategy check: clustering on t=18 ..." | low_alpha_designer | 2026-10-17 | STATEMENT_INSPECTED (truncated) | ledger ceiling about 22–23; six 21-vertex 114-edge chi=10 alpha=3 "pre-Euler" near-misses |
| SRC-0054 | rStation post 52 "Constructive flip-pair search for OP1(b)/OP2 targets" | selene_opus | 2026-10-06 | STATEMENT_INSPECTED (truncated) | heuristic only; "local-search plateaus prove nothing" |
| SRC-0055 | bipsat2 (CaDiCaL + IPASIR-UP Boyer–Myrvold propagator, persistent Kuratowski lemmas, DRAT replay tool) | seanstock (= forget_me_not per post 155) | undated (2 commits) | STATEMENT_INSPECTED (README) | MIT; candidate independent second oracle |
| SRC-0056 | rStation r/earth_moon full listings: papers (67: 1–67) and discussion (163 posts) | rStation forum authors | listings accessed 2026-10-19 | METADATA_ONLY | titles and one-line summaries only |
| SRC-0037 (refresh) | Szeider arXiv 2609.28102 | Szeider | v1 2026-09-23, no v2 | STATEMENT_INSPECTED | Theorem 1 includes "at most 18 vertices"; Lemma 7(1) n<=19 via Delta(complement)<=8; OP1(b) open, with feasibility unknown; C7[K4] thickness 3 by a 112 > 104 triangle-free count |
| SRC-0039 (refresh) | Szeider Zenodo 22913639 | Szeider | v1 only | METADATA_ONLY | 2.24 GB zip, alpha<=2 only |
| SRC-0018 (refresh) | Doria Zenodo 21824308 | Doria | one version, 2026-08-06 | ABSTRACT_INSPECTED | n<=16, conditional on Lalonde's census |
| SRC-0007 (refresh) | Patil Zenodo 22103613 | Patil | one version, 2026-08-26 | METADATA_ONLY (refresh) | no alpha<=3 or 28-vertex content in metadata |
| SRC-0021 (refresh) | Volkopat/earth-moon-chi10 | Patil | — | METADATA_ONLY | direct fetch 404 again; a search excerpt shows the README sentence "No biplanar graph with chromatic number 10 was found" |
| SRC-0004/0035 (refresh) | Epoch AI open-problem page | Epoch AI | — | STATEMENT_INSPECTED | "Unsolved"; no progress listed |
| SRC-0012 (refresh) | Trivedi Zenodo 22074335 | Trivedi | v1 2026-08-05 | STATEMENT_INSPECTED | all biplanar C5 clique blow-ups 9-colourable, via a triangle-free cross-edge bound |

Other rStation items seen at METADATA_ONLY level (SRC-0056) and relevant to overlap:
paper 13 (linking lemma); paper 10 (odd-cycle blow-ups, OP2 candidates not biplanar);
paper 61 (two 17-vertex C5 blow-ups not biplanar); post 46 (odd-cycle colouring excludes
10-chromatic biplanar clique blow-ups); post 49 (alpha=3 blow-ups at orders 22–23);
post 59 (budget-b face encoding, six n=26 survivors undecided); post 119 (biplanarity
decider benchmark, 97 graphs); post 157 (persistent Kuratowski lemmas, twin lex-leaders);
posts 47 and 12 (line-graph question reduced to four 28-vertex graphs); papers 22 and
36 (SRC-0043/0042: limits of counting, vertex-transitive census); post 159 (all 20
nine-critical biplanar graphs on <=13 vertices).

Search terms (pass 2): "zenodo Earth-Moon biplanar 2026", "Spogreev biplanar zenodo",
"bipsat2 github biplanarity", "Volkopat earth-moon-chi10", "Earth-Moon problem
10-chromatic biplanar graph found", "biplanar graphs independence number three
9-colorable", "thickness two graphs independence number 3 arXiv 2026", "Szeider
biplanar independence number 28 vertices", "Gethner Sulanke open problem independence
ratio biplanar 2026"; plus Zenodo version APIs for SRC-0007/0018/0039 and the arXiv
abstract page.

## 3. Overlap matrix (never "novel")

| Programme result | Classification | Overlapping sources and reason |
|---|---|---|
| C5 threshold (sum<=16 biplanar; sum17 24/26 certified; CLM-0090..0094, 0105) | OVERLAP | Trivedi SRC-0012: every biplanar C5 blow-up is 9-colourable; four 10-chromatic K9-free members classified. rStation paper 61 and post 46; Patil SRC-0017 C5[3,4,3,4,3]. Our certified individual 17-vertex obstructions may be finer-grained, but the family conclusion is prior. |
| Sigma=17 DRAT certificates (individual classes) | OVERLAP | rStation paper 61 hand-excludes two 17-vertex C5 blow-ups; the front-page titles recorded in S027 name C5[2,2,5,2,6] and C5[2,3,4,2,6]. The remaining classes APPEAR_UNCLEARED as individual certificates; there is no novelty claim. |
| original271 corpus closure (CLM-0090..0094) | OVERLAP | Patil SRC-0007 ("exhaustion of the known chi=10 candidates"); rStation post 46 (10-chromatic biplanar clique blow-ups of odd cycles excluded). Our base-order 7–8 clique blow-up census framing APPEARS_UNCLEARED in detail. |
| D036 and the S028 deletion-descent obstructions (CLM-0107) | APPEARS_UNCLEARED | No source found lists GJaVBo[7,3,2,2,1,1,1,1] or an 18-vertex clique blow-up obstruction. rStation has many obstruction catalogues (posts 130, 136, 142, paper 58) that were not inspected at graph level. |
| 28-vertex alpha3 clique blow-up profile closures (CLM-0103, 0109) and S026 P29 (28 vertices, 154 edges) | OVERLAP | The same object class as OP1(b): paper 59 (regular 154-edge case excluded by Thm 12, which covers P29-type 11-regular graphs), post 146 (155/156 edges), post 155 (twinned slice), post 141 (passports), SRC-0042 (orders 25–29 blow-ups). Our closures are fixed-profile finite statements. |
| Lemma C / K9-minor two-branch CEGAR (CLM-0090..) | OVERLAP | rStation paper 13 (linking lemma); SRC-0042 (one-step K9 linking certificates); paper 59 Lemma 14 (rooted transversal via linking). |
| Lemma F (n<=36 for alpha<=3) | DUPLICATE (superseded) | The same complement-degree idea gives n<=30 (paper 59 section 4, conditional on SRC-0037; compare Szeider Lemma 7(1) for alpha<=2). Paper 59 claims n<=28. The Turán form of Lemma F was not found verbatim, but it is strictly weaker and elementary. It is recorded as PROGRAMME_PROVED (CLM-0110) with no novelty. |
| Triangle-free cross-edge bound (2(2n-4)) | DUPLICATE | Trivedi SRC-0012 / Szeider ref [42, Question 7.1]; used widely on rStation. |

## 4. The alpha<=3 question: who has proved, claimed, attempted or abandoned what

* **Proved (refereed or formally checked):** alpha<=2 implies 9-colourable and n<=18
  (Szeider, Lean-checked computation under three planar hypotheses; not replayed here).
* **Claimed, unrefereed, rStation "Accept":** alpha<=3 implies n<=28 (paper 59); no
  11-regular biplanar alpha<=3 graph on 28 vertices (paper 59, RUP); every biplanar graph
  on <=20 vertices is 9-colourable (papers 1, 3, 4, 6, 16, 18); 10-critical biplanar on
  21 vertices implies alpha=3 (paper 33).
* **Claimed, not reviewed:** post 146 (155-edge overlapping-K8 normal forms); post 155
  (2,543/2,555 twinned quotients); post 152 (Z7 fixed-point-free, n=28).
* **Attempted and abandoned or stopped:** symmetric exact search (post 152; "not a
  productive route"); the delta=11 SAT ladder (post 146 comment, 2026-10-19, stopped at
  30-minute caps; "the bottleneck is ... encoding Lemma 14 compactly"); flip search
  (post 52).
* **In progress (as of 2026-10-19):** a 72-hour bipsat2 run on the 16 undecided twinned
  splits (post 155); the order-21 ledger (post 144).
* **Nobody claims T3.** Paper 59 explicitly lists "nine-colorability for independence
  number three" as open.
* **Tools available:** Szeider's SMS + LRAT + Lean pipeline (SRC-0038/0039; archive
  2.24 GB, licence "copyright author", no permissive licence); bipsat2 (MIT, DRAT replay);
  paper 59's RUP packet (CC0, stdlib checker); tightbip (private); plus our own pinned
  CaDiCaL/drat-trim CEGAR stack.
* **Attribution obligations for any S030 output:** Gethner–Sulanke OP1(b) (SRC-0003);
  Szeider (alpha<=2, the n<=18 bound, the complement method; SRC-0037); the paper 59
  authors (n<=30 and n<=28, the regular case, the private-clique method); forget_me_not
  (twinned census, bipsat2); low_alpha_designer (symmetric search, delta=11 ladder);
  Trivedi and Szeider (the 2(2n-4) triangle-free bound); Kirchweger–Scheucher–Szeider
  (SAT modulo symmetries). Any n=28 sub-result must say where it duplicates these.

## 5. Second novelty pass (rule 13)

The second pass searched different terms: "thickness-two graph K4-free complement 28
vertices", "Gethner Sulanke Open Problem 1(b) solved", "ten-chromatic thickness two
graph 2026", "\"thickness two\" chromatic number ten construction", "Ringel Earth-Moon
lower bound improved 10". It also checked the Zenodo version endpoints (SRC-0007/0018/0039
each have a single version) and arXiv 2609.28102 (v1 only). Change from pass 1: it
confirmed through Szeider's own text and Weaver SRC-0022 that the 28-vertex
K4-free-complement question is Gethner–Sulanke OP1(b). It found no OP1(b) solution, no
10-chromatic thickness-two graph and no alpha<=3 colouring theorem. The rStation
listings were enumerated once (167 items in total); individual items read are listed above.

## 6. Go/no-go for S030: **GO-MODIFIED**

Reasons, all recorded above:

1. *Lemma F is superseded* (finding 1). S030 must not spend effort re-proving the
   n<=36 bound; it is filed as CLM-0110.
2. *T3 for 21<=n<=27 is redirected out of S030.* At these orders alpha<=3 does not
   force chi>=10, so T3 there is a general 9-colourability question. The rStation
   order-21 programme (thousands of CPU-hours, several contributors) is the frontier,
   with a projected ceiling of about 22–23. A "complete enumerator for the remaining
   sizes" (D062 draft step 4) would duplicate it and is not plausibly finishable. That
   part of T3 is PARKED, not discharged.
3. *Order 28 alone carries the whole alpha<=3 witness route* (CLM-0112). It is
   two-sided in exactly the D042 sense: any biplanar alpha<=3 graph on 28 vertices is
   the headline witness, and a certified exclusion closes OP1(b), i.e. the alpha<=3
   counting route.
4. *Overlap and coordination risk.* The order-28 strata are partly owned on rStation.
   S030 must start from the open strata (delta<=10 entirely; delta=11 with m=155 or 156
   outside the published exclusions). It must treat rStation results as SOURCE_STATED
   prioritisation only, never as discard filters unless independently re-proved or
   replayed, and it must not contact rStation (outreach stays owner-gated).
5. *Feasibility is unknown* (Szeider). S030 therefore starts with a measured
   feasibility stage and pre-registered caps. A capped stratum is UNKNOWN, not exhaustion.

A REDIRECT was considered and rejected. Order 28 is still open, and our 28-vertex
alpha3 machinery and certified obstruction library are directly relevant. Nobody has
announced an exhaustive order-28 run. The full S030 prompt is in
authoritative/NEXT_SESSION_PROMPT.md (= sessions/S029/S030_FUTURE_PROMPT.md).

## 7. Written proofs recorded this session (elementary; no novelty)

**CLM-0110 (Lemma F).** Let G be biplanar on n>=3 vertices with alpha(G)<=3. Then n<=36.
*Proof.* The complement H is K4-free, so by Turán's theorem e(H)<=t(n,3), with equality
iff H=T(n,3). Biplanarity gives e(G)<=2(3n-6)=6n-12. Put f(n)=C(n,2)-t(n,3)-(6n-12).
Then e(G)>=C(n,2)-t(n,3) forces f(n)<=0. Adding a vertex to a smallest part of
T(n,3) adds n-floor(n/3) edges, so f(n+1)-f(n)=n-(n-floor(n/3))-6=floor(n/3)-6>0 for
n>=21. Also t(37,3)=(37^2-13^2-12^2-12^2)/2=456 and C(37,2)=666, so f(37)=666-456-210=0.
Hence f(n)>0 for all n>=38, and no such G exists. At n=37 every inequality is tight, so
H=T(37,3) and G is the disjoint union K13+K12+K12. That contains K9, which is not
biplanar (SRC-0014), and biplanarity is closed under subgraphs. So n<=36. QED.
(For alpha<=2 the same argument with t(n,2) gives n<=23; Szeider's n<=18 is stronger.)

**CLM-0111 (n<=30, conditional on SRC-0037 Theorem 1).** For any v, the graph
G-N[v] is biplanar with alpha<=2, since an independent triple there together with v
would be an independent 4-set. By SRC-0037, |V(G-N[v])|<=18, so deg(v)>=n-19. Summing
degrees gives n(n-19)<=2e(G)<=12n-24, i.e. n^2-31n+24<=0. That fails at n=31
(961-961+24>0) and beyond. So n<=30. Source-stated in paper 59 section 4; re-derived
here. Its validity inherits Szeider's computer-assisted theorem.

**CLM-0112 (order-28 reduction).** If a biplanar graph with alpha<=3 has n>=28 vertices,
then any 28-vertex induced subgraph is biplanar with alpha<=3 and has chi>=ceil(28/3)=10.
So "some biplanar alpha<=3 graph has chi>=10 by counting" is equivalent to OP1(b).
Every biplanar alpha<=3 graph on <=27 vertices that has chi>=10 must be found by a
non-counting argument.
