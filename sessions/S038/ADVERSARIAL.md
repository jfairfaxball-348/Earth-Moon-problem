# S038 adversarial boundaries

- The original91/125 states, all43 single flips and the223 nonextension proofs
  were reproduced through the immutable S037 checker before new experiments.
- A patch must have simple connected boundary and no interior vertex. Tree
  face sets with repeated boundary vertices, extra internal edges or disconnected
  rims are rejected. The result is about this selected family only.
- Recursive triangulation is cross-checked by brute noncrossing chord subsets
  for polygons4..8. The near-layer generator leaves exactly one quadrilateral;
  it never assumes the77-edge layer extends to a disjoint triangulation.
- Eighty actual moves are checked with NetworkX/direct enumeration. The portable
  checker separately replays every stored search transition by checking boundary,
  chord noncrossing, face gluing, exact edge changes, final disjointness and score.
- Coupled moves are atomic. Temporary overlap is permitted only for an edge
  simultaneously removed by the other layer; final overlap always fails.
- All finite neighborhood tables are independently reconstructed by a different
  removal/chord enumeration. Scores agree for every family member, not just the
  best one. Count overlaps across support families are not new distinct graphs.
- The radius-four diagnostic covers one-layer4 and joint2+2, not joint1+3/3+1.
  Strict local minima do not certify absence of a non-monotone escape path.
- Equal CPU caps are not equal actual CPU consumption; plateau rules stopped
  arms early. There is no statistically established method superiority.
- A smaller independent-four-set count is not a chromatic lower bound. Saved
  best123 states are actually8-colourable; all22 checked records are<=9-colourable.
- S037 nonplanar hitting assignments remain negative controls, never witnesses.
  No historical UNKNOWN cell, capped heuristic, template or full stratum is
  promoted to UNSAT. Nine sorted S11 prefixes remain UNKNOWN;9..12 unchanged.
- No scientific source novelty or global flip connectivity claim is assumed.
  The new simultaneous-flips reference was read only at abstract/metadata grade.
- No S036 archive/process/scheduler action. S039 is a proposed next direction,
  not executed in this session.
