# Exact simultaneous recolouring as equality constraints

Let T_1,...,T_t be the heavy K8 noncut cores, F=G-union T_i and B_i=A_i union{z_i}. CLM-0052 proves that a proper11-colouring of F extends to all cores exactly when every five-vertex B_i repeats a colour. Actual criticality says every such exterior colouring has at least one bad boundary, possibly changing with the colouring. It does not say all boundaries are bad in the same colouring.

## An exact logical reformulation

Fix R=union B_i and a proper11-colouring psi of F-R. Give each v in R the list

    L(v)={0,...,10} minus psi(N_F(v) minus R).

The following is an equivalence for this FIXED exterior colouring, not a claim that its conditions can always be met. Choose one unordered nonadjacent pair p_i within each B_i; impose equality on the endpoints of all chosen pairs. Let the equivalence classes be connected components of the selected-pair graph on R, including isolated vertices. The equality constraints and proper colouring of F[R] can be satisfied iff:

1. Every class is independent in F[R].
2. The quotient graph whose classes are joined when F[R] has a cross edge has a proper list colouring, with class list the intersection of ALL L(v) in that class.

Proof: any satisfying colouring is constant on equality components; it forbids an internal edge, lies in every constituent list, and assigns different colours to adjacent classes. Conversely expand a proper quotient list colouring constantly within each class. The lists preserve all edges to F-R, independence preserves edges within classes, and proper quotient colours preserve every cross edge. These are all edges of F. Every B_i has its selected repeated pair, hence uses at most4 colours and extends through its core. Conversely any extending exterior recolouring has a repeated nonadjacent pair in each five-set B_i, and supplies the corresponding quotient colouring. This covers t=0, empty/singleton R, overlap, isolated classes, empty intersections and cross edges. A repeated pair may involve z_i; restricting all choices to A_i would supply only a sufficient tactic, not the equivalence.

This quotient is a LOGICAL colouring instance. No assertion that vertex identification preserves either planar layer is made; CLM-0013's obstruction remains. No contraction-based planar theorem or polynomial-time method follows. Selecting pairs can require10^t choices, and arbitrary proper list colouring remains in the quotient; equivalence is not a completeness reduction to a bounded graph universe or a new algorithmic novelty claim.

SRC0033's primary survey Section2 describes classical same-colour vertex contraction and attributes that branching idea to Mehrotra–Trick1996. Our proof spells out the fixed-list/boundary application; it is not a claim to invent equality contraction. Original algorithmic source not proof-inspected.

## Acyclic pair constraints still need global list intersection

Three independent variables have lists{0,1},{1,2},{0,2}. Select equality pairs01 and12, a tree. Each individual pair has a feasible equal assignment, but their common component has empty intersection, so no simultaneous assignment exists. Every vertex still has two options; pairwise list intersections and absence of cycles do not suffice. The registered exhaustive7^3*3=1029 list/pair controls corroborate this logical distinction using independent assignment enumeration, not SAT text or actual critical graph evidence.

If R is independent, there are no quotient edges, and nonempty common intersections in every class DO suffice (choose any colour independently). With cross edges, independently choosing class colours may fail; the exact proper quotient-list obligation must remain. Hall support representatives/colour distinctness do not prove these intersections or boundary equalities. An abstract list trap is not an actual biplanar12-critical witness.

## Universal route challenge

Attempted sufficient tactics require a pair choice with independent classes and nonempty lists, plus quotient flexibility. Support expansion supplies no list information; Q>=4t supplies no spare colours. Light components need their own published unequal-neighbour-set extension obligations; changing high vertices can destroy those palettes. SRC-0027 Lemma3 concerns unequal actual neighbour-set pairs and a finite edge budget, not arbitrary simultaneous equality requests. Its local induction proof was re-inspected and remains attributed; it has not been generalised beyond e_H+c<=65.

No all-order proof guarantees an appropriate exterior colouring, compatible pair choices or quotient list colouring. Large deficit/order remains uncontrolled. The universal theorem route is blocked at these existence steps, not resolved by the reformulation or finite controls. Universal11-colouring, external independent review and all later gates remain unpassed.
