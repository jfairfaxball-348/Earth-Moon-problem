# S002 fresh internal adversarial pass

This is a separate internal proof/checking pass by the same session agent,
with an independently implemented certificate checker. It is not an
independent human review or an externally verified full theorem.

1. Odd-cycle colouring induction: verified the zero-support path case,
   k=0, existence of a slack-degree vertex, perfect matching of the even
   path after deletion, exactly one degree decrement at matched vertices,
   and preservation of the total-weight constraint. A maximum independent
   set alone would not suffice; the matching construction supplies the
   extension. C3 is explicitly separate. For longer cycles the bound
   8s+4<=9s starts at s=4, not s=3. C7's forced equality and C5's lower
   bound w_i>=N-16 supply the missing short cases. No solver dependency.
2. Triangle-free cross-edge accounting uses a spanning subgraph of the
   two planar layers, so the bound is inherited. Disconnected layers do
   not invalidate the standard n>=3 bound. Internal clique edges are
   discarded, never double-counted as cross edges.
3. Apex candidate: the bridge's common-neighbour set is exactly the
   apex. The deleted incident edges prevent the shared Hajós vertex
   from becoming a second common neighbour. Equality in the two Euler
   bounds forces BOTH layers to be triangulations. The proof deliberately
   does not reject non-saturated apices with the same argument.
4. Critical density: use a minimal non-11-colourable subgraph, not a
   vertex-critical-only assumption in an edge-critical theorem. It is
   12-chromatic by colouring after deleting a vertex and adding a fresh
   colour. At n=78 equality is possible arithmetically, so no invented
   n>=79 bound. The proof has no finite upper bound on counterexample n.
5. Degree witness: minimum degree 11 refutes 10-degeneracy, not
   11-colourability. Its actual 7-colouring refutes any inference from
   saturation to chromatic number 12. Its two degree-five sets are
   disjoint; simultaneous low degree in both layers is not forced.
6. Certificates: NetworkX LR and separate stdlib rotation/face/Euler
   checker agree. Sulanke rotation is independently obtained from source
   coordinates. Tests reject a duplicated rotation neighbour, a genus-
   altering cyclic-order mutation, omitted edge, overlapping edges,
   improper colouring and malformed endpoints. Neither checker certifies
   the 42-vertex chromatic lower bound; none is claimed.
7. Initial source-extraction scratch assertion guessed equal layer sizes
   26/26 and failed on actual 26/24. The assertion was corrected against
   source vectors and all 50 edges independently checked; no edges were
   invented or graph repaired. The manifest records the final source
   checksum and reproducible extraction script.
8. No priority claim: the C5/C7 and saturated-cone exclusions overlap
   existing 2026 work. Szeider's computational theorem is SOURCE_STATED,
   not programme-FORMALLY_CERTIFIED; native_decide and classical
   planarity assumptions remain explicit. Imported archive checks were
   not run. The generic sparse-critical results have range restrictions
   that cannot be silently specialized to k=12.

Residual gaps: neither unrestricted construction nor universal improved
upper bound; no independent novelty audit; no full external certificate
replay. The next session must attack the surviving mathematical frontier.
