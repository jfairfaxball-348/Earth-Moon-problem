# S040 adversarial audit

No subagent or external review is claimed. This is the executor's independent
algorithmic replay and deliberate falsification, not independent authorship.

- The D077 criterion was hashed (REGISTRATION.json, 12:04:01Z) before any
  S040 objective value; the experiment asserts the hash. The only earlier
  computation counted components/pairs (disclosed) and a debug smoke on the
  historical S038 inputs whose outputs were discarded. The criterion was not
  changed; the post-hoc addendum is registered separately and cannot alter it.
- "No strict improvement" is exact only for the registered one-star-per-layer
  family at two fixed embeddings. Coordinated flips, patches inside pairs,
  multi-star moves, degree2/>6 stars and re-embeddings are unsearched, not
  excluded. The post-hoc swap census shows downhill directions do exist off
  the move families; it supports the PIVOT reason, it does not refute it.
- Compatibility is checked three ways: numpy containment test, Python-int
  final-layer intersection on full cartesian products, and per-move replay of
  both components on the pre-move layers with conflicts recomputed. Nine
  malformed pair certificates are rejected (dropped/extra conflict, wrong type,
  swapped layers, foreign component, duplicate addition, missing effect, fake
  target, protected core removal).
- Neighborhood scores use two different algorithms (OR masks and delta counts
  over touched four-sets); both regenerate components by chord subsets and
  polygon splitting without importing the S038 filling recursion.
- tau, tau_safe and both packings are certified by explicit sets checked in
  code (pair-disjointness and hitting). RC2 only finds them. tau bounds a
  label-fixed edit, not relabelled or arbitrary graphs.
- The alpha<=3 repairs are checked by direct enumeration, but each contains
  K10, so none is a candidate; no biplanarity search was attempted and no
  biplanarity statement is made about any repaired graph.
- Equal ceilings do not mean equal consumed CPU: coord arms used ~8-13x the
  CPU of star arms and still found nothing. All arms stopped at plateau.
- Every saved graph has an explicit <=9-colouring; bare UNSAT/caps are absent.
  Protected results keep the K6-join-C5 core in its original layers.
- REGISTRATION.json also recorded the then-current hash of
  tools/s040_coordinated.py. Before the experiment one line was added
  (`Table.index`, a key-to-row map used only for tabu lookups); generation,
  compatibility and scoring code are unchanged. The experiment asserts only
  the PLAN hash, as registered.
- First pair-validation call used an unsupported solver flag; six attempts
  were UNKNOWN and the run was repeated before records were kept. No negative
  colourability conclusion was ever drawn from it.

Frozen S036-S039 artifacts and sources are unchanged; S039 is replayed through
the hash-pinned checker. S036 stays stopped; nine sorted prefixes UNKNOWN.
