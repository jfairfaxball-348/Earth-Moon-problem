# Heavy-core excess with arbitrary overlap

Work in an actual finite simple12-critical biplanar G. Set L={v:deg(v)=11}, H={v:deg(v)>=12}, q_v=deg(v)-12 on H. Gallai/extension prerequisites are source-attributed to SRC-0027; CLM-0048's published-method blocking argument gives sum_(v in A_i)q_v>=13 for every heavy K8 endblock. Each of its seven noncut low vertices is adjacent to its four independent common high neighbours A_i. Distinct K8 low blocks are vertex-disjoint: a vertex in two would have at least14 low neighbours, impossible at degree11. These hypotheses are essential; this is not a theorem about arbitrary degree11 neighbourhoods.

## Removing the maximum-overlap hypothesis

Select t such cores and let r_v count how many A_i contain v. Distinct cores give deg(v)>=7r_v, so r_v<=floor((q_v+12)/7). Truncate a local demand at13: since q_v>=0 and sum_A_i q_v>=13, also sum_A_i min(q_v,13)>=13. This avoids charging a huge excess more than a core actually needs.

For every nonnegative integer q and integer r with7r<=q+12,

    4r min(q,13) <=13q.

Complete proof: q=0 is immediate. For1<=q<=8, r<=2, so r q<=2q<=13q/4. For9<=q<=12, r<=3, so r q<=3q<=13q/4. For13<=q<=15, r<=3 and r min(q,13)<=39<=13q/4. Forq>=16, r<=(q+12)/7<=q/4 because4q+48<=7q; multiplying by13 proves the bound. These four cases cover allq and include both integer endpoints. No finite enumeration supplies the all-order step.

Sum the truncated demands over cores, then use the inequality at each support vertex:

    13t <= sum_v r_v min(q_v,13) <= (13/4)sum_v q_v.

Therefore the UNWEIGHTED support excess obeys

    sum_(v in union A_i)(deg(v)-12) >=4t.

This improves the earlier multiplicity-dependent charge without asserting the false13t unweighted bound, a maximum overlap, or distinct high-excess representatives. It holds for every selected subfamily. Emptyt gives0<=0. Excess outside the selected support is nonnegative, hence totalQ>=4t as well. A high vertex may still support several cores.

Equality in the elementary charge system forces every positive support vertex to have q=16 and r=4; every core has exactly one such vertex, since its truncated demand must be exactly13. q=0 vertices have r<=1. Thus t must be divisible by4 when positive equality holds. This is an inequality-system observation, not existence or classification of critical graphs.

The registered abstract equality model has four cores, one common support of q16/r4, and three private q0 supports per core. It meets every local13 demand and degree-multiplicity inequality, with Q16=4t. For each subfamily, union size3s+1 meets both S008 and the stronger expansion below. It does NOT exhibit actual high degrees, planar layers or12-criticality. Sharpness claimed only for this arithmetic relaxation, not for the graph class or a new mathematical method.

## Include the low cut vertices in Euler accounting

S008 counted only seven noncut vertices per block. All eight low vertices of each K8 block can instead be retained; the cut vertices are distinct and disjoint from H and from other selected blocks. Each block contributes28 internal edges plus28 noncut-to-A_i edges. All56t counted edges are distinct, even with high overlap. Its selected subgraph has8t+a vertices, a=|union A_i|, and order>=12 for t>0. Thickness-two Euler therefore gives

    56t <=6(8t+a)-12,
    a>=ceil((8t+12)/6).

Any omitted cut-to-high/high-to-high/other edges increase the count, never rescue a violation. There is no shared planar embedding assumption. This is an elementary strengthening of the previous ceil((7t+12)/6) expansion; classical Hall still gives support vertices, not available colours.

## Attempt at a universal contradiction

The exact degree-sum identity is Q=l-24-2D, with D=6n-12-m and all low degrees11/high degrees12+q. Combining gives l>=4t+24+2D. Since disjoint K8 blocks already require l>=8t, this is compatible with arbitrarily many blocks and arbitrary other low vertices. It yields no upper bound on order/deficit and no simultaneous colouring.

The S005 and S006 low-forest inequalities have distinct component corrections and remain unchanged. This necessary charge can constrain heavy-core campaigns; it does not eliminate smaller heavy blocks, heavy odd cycles, light blocks, all large deficits, or all12-critical biplanar graphs. The all-order universal11-colouring target remains OPEN. No external independent universal review, novelty, Lean or publication claim.

## Mixed long odd blocks: same high vertices, one common budget

The charge can be summed across different block TYPES without double counting high excess, provided all selected removed cores are disjoint. A whole low component cannot share vertices with another selected component; different endblocks have disjoint noncut cores even if their low cuts coincide. Core vertices have no membership in other selected cores. Select actual independent pairs in the common9-element high boundary for each odd type (K9 exclusion guarantees an independent pair). For the clique type use its actual four-element independent A.

Let counts be t8 (K8 endblocks), e11/e9 (heavy odd endblocks of lengths11/9), and w9/w7 (whole heavy odd components of lengths9/7). CLM0048/0055 supply respective local demands13,7,3,5,1. Adjacent core sizes are7,10,8,9,7. Each support vertex v has multiplicities r_j and therefore sum_j weight_j*r_j<=deg(v)=q_v+12.

For one type define truncated charge c_j*min(q,d_j)/d_j, with (weight,demand,c) equal to

| Type | Core size | Local demand | Assigned charge |
|---|---:|---:|---:|
| K8 endblock |7|13|4|
| C11 endblock |10|7|4|
| C9 endblock |8|3|2|
| whole C9 |9|5|3|
| whole C7 |7|1|1|

Each support set receives at least its assigned charge, since nonnegative excess totalling at least d has truncated excess totalling at least d. It remains to bound total incoming charge at a shared support vertex by q, including mixed types.

Forq>=16, each type's truncated charge divided by its core size is at most4/7 (largest is K8's4/7). Hence the incoming charge is at most4(q+12)/7<=q. Forq=0 all contributions vanish. Forq1..8, capacityq+12<21 allows at most two nonzero core incidences (every core size>=7). Checking the five singleton types and15 unordered type-pairs with sum sizes within capacity gives maximum preciselyq. Achieving choices, in q order1..8, are: C7; C7+C7; C7+C9-end; C9-end+C9-end; C9-end+C9-whole; C9-whole+C9-whole; C11-end+C9-whole; C11-end+C11-end. Their charges are1,2,3,4,5,6,7,8; all other admissible pairs have no larger charge by substituting the table's fractions. Exact independently checked maxima are retained in mixed_charge_controls.json, not decimal approximations.

Forq9..11 there are at most three incidences. With at most two, each individual contribution<=4, hence total<=8<q. With three, C11 (size10) is impossible because10+7+7>q+12. Atq9/10 a wholeC9 incidence is also impossible with three because9+7+7>q+12. Every remaining contribution<=4q/13 (C9-end<=2, C7-whole<=1, K8=4q/13; atq11 the wholeC9 contribution3<=44/13). Total<=12q/13<q. Forq12..15 at most three incidences and each contributes<=4, so total<=12<=q. This covers all nonnegative integer excesses. Independent Cartesian0..3 multiplicity enumeration and capacity knapsack cover exactly q0..15 and corroborate these finite cases; no unrestricted computation is assumed.

Sum charges over the union of ALL selected support sets. Every high vertex pays at most its own q exactly once, even with cross-type overlap, giving

    Q >=4t8+4e11+2e9+3w9+w7.

This is an all-order necessary mixed-family inequality conditional on the actual heavy/criticality premises. It does not require independent support UNION (only each chosen odd pair), a maximum overlap or distinct support representatives. It may be used on any selected subfamily. Empty choices yield0. It leaves short heavyC5/C7 endblocks, smaller cliques, light blocks and exterior colouring flexibility open; Q remains unbounded, so no universal contradiction or headline advance follows.
