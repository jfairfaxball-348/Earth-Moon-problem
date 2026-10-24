"""Meaningful positive, negative, objective and embedding-move controls."""
import itertools as it
import json
from pathlib import Path
import random
import sys
import time
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_pairs import seed, masks, independent
from s037_check_pair import check


def main():
    start = time.process_time()
    smoke = json.loads((ROOT/'validation/S037/SMOKE.json').read_text())
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == 271
    rng = random.Random(3699)
    checked_flips = 0
    for kind in ('stacked', 'bipyramid'):
        t = seed(12, kind, rng)
        for _ in range(500):
            e = rng.choice(sorted(t.inc))
            before = set(t.faces)
            inverse = t.flip(e)
            if inverse:
                assert len(t.inc) == 30 and len(t.faces) == 20
                assert all(len(fs) == 2 for fs in t.inc.values())
                assert nx.is_planar(nx.Graph(t.inc.keys()))
                assert t.flip(inverse) == e and t.faces == before
                t.flip(e)
                checked_flips += 1
        sets, cover, full = masks(12)
        expected = sum(all(edge not in t.inc for edge in it.combinations(vs, 2)) for vs in sets)
        assert independent(t, cover, full).bit_count() == expected
        a, b = rng.sample(range(12), 2)
        u = t.relabel(a, b)
        assert independent(u, cover, full).bit_count() == expected
        assert nx.is_planar(nx.Graph(u.inc.keys()))
    known = json.loads((ROOT/'validation/S003/splits/J1.split.json').read_text())
    n = 1+max(v for k in ('E1', 'E2') for e in known[k] for v in e)
    known = dict(n=n, V=list(range(n)), **{k: sorted(tuple(sorted(e)) for e in known[k]) for k in ('E1', 'E2')})
    positive = check(known)
    assert positive['alpha_at_most_3']
    rejected = []
    for name in ('overlap', 'nonplanar', 'false_objective', 'duplicate'):
        bad = json.loads(json.dumps(known))
        if name == 'overlap':
            bad['E2'].append(bad['E1'][0])
        elif name == 'nonplanar':
            bad['E1'] = list(it.combinations(range(5), 2))
        elif name == 'false_objective':
            bad['independent_four_sets'] = 1
        else:
            bad['E1'].append(bad['E1'][0])
        try:
            check(bad)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('corrupt candidate accepted: '+name)
    # K3,3: independent negative planarity control, no SAT involved.
    assert not nx.is_planar(nx.complete_bipartite_graph(3, 3))
    result = dict(status='PASS', seed=3699, legal_flips_checked=checked_flips,
                  positive_J1=dict(n=n, alpha_at_most_3=True), rejected=rejected,
                  bitset_vs_direct=True, K33_nonplanar=True, cpu_seconds=time.process_time()-start)
    (ROOT/'validation/S037/CONTROLS.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    print(result)


if __name__ == '__main__':
    main()
