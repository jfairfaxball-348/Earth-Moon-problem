#!/usr/bin/env python3
"""S027 controls for the learned-obstruction machinery (no mathematical claim).

1. Agreement: on seeded random base graphs for two profiles, the in-loop
   (assumption) containment solver, the audit-form CNF and, for C5 obstructions,
   the S025 backtracking find_map give the same contains/avoids answer.
2. Support lemma: every found map stays a valid embedding into random supersets
   of its support only.
3. Negative controls: the independent learned-clause checker must REJECT a
   CONTAIN clause with one support edge removed, a non-weight-preserving
   permutation, and an EULER clause one edge short.
Usage: s027_selftest.py OUTDIR
"""
import copy
import gzip
import itertools as it
import json
from pathlib import Path
import random
import subprocess
import sys

import networkx as nx
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s027_contain import encode, decode, explicit_map, support, load_obstructions   # noqa: E402
from s025_transfer import find_map                                                 # noqa: E402


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(27001)
    obs = load_obstructions()
    c5 = [H for H in obs if H['name'].startswith('C5-')]
    rec = {'agreement_tests': 0, 'contains': 0, 'avoids': 0, 'backtrack_agreements': 0,
           'support_superset_tests': 0}
    for w in ([4, 4, 4, 3, 3, 3, 2, 2, 2, 1], [3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2]):
        n = len(w)
        pairs = list(it.combinations(range(n), 2))
        loops = {}
        for H in c5[:8] + [H for H in obs if not H['name'].startswith('C5-')]:
            cls, top, x, _ = encode(H, w, pairs=pairs)
            loops[H['name']] = (Solver(name='cadical195', bootstrap_with=cls), x, H)
        for trial in range(25):
            p = rng.choice([0.55, 0.65, 0.75])
            E = sorted(e for e in pairs if rng.random() < p)
            B = nx.Graph(); B.add_nodes_from(range(n)); B.add_edges_from(E)
            assume = [i + 1 if e in set(E) else -(i + 1) for i, e in enumerate(pairs)]
            for name, (s, x, H) in loops.items():
                s.conf_budget(200000)
                a = s.solve_limited(assumptions=assume)
                cls2, top2, x2, _ = encode(H, w, B=B)
                with Solver(name='cadical195', bootstrap_with=cls2) as s2:
                    s2.conf_budget(200000)
                    b = s2.solve_limited()
                if a is None or b is None:
                    continue
                assert a == b, (name, w, trial)
                rec['agreement_tests'] += 1
                if a:
                    rec['contains'] += 1
                    f = decode(H, w, set(v for v in s.get_model() if v > 0), x)
                    explicit_map(H, w, f, E)
                    S = support(H, f)
                    for _ in range(3):
                        extra = [e for e in pairs if e not in S and rng.random() < 0.3]
                        explicit_map(H, w, f, S + extra)
                        rec['support_superset_tests'] += 1
                else:
                    rec['avoids'] += 1
                if name.startswith('C5-'):
                    A = nx.from_graph6_bytes(H['g6'].encode())
                    m = find_map({i: set(A[i]) for i in A}, H['u'], B, w)
                    assert (m is not None) == a, ('backtrack disagreement', name, trial)
                    rec['backtrack_agreements'] += 1
        for s, _, _ in loops.values():
            s.delete()
    assert rec['contains'] > 0 and rec['avoids'] > 0
    # Negative controls on a genuine learned file from a tiny seeded run.
    from s027_source import Profile
    w = [4, 4, 4, 3, 3, 3, 2, 2, 2, 1]
    P = Profile(10, len(w), w, obs, None)
    with Solver(name='cadical195', bootstrap_with=P.base) as gen:
        loops = [(H, *encode(H, w, pairs=P.pairs)) for H in c5]
        sol = [(H, Solver(name='cadical195', bootstrap_with=c), x) for H, c, t, x, k in loops]
        learned_kinds = set()
        for _ in range(40):
            if not gen.solve():
                break
            m = set(v for v in gen.get_model() if v > 0)
            E = sorted(e for e in P.pairs if P.idx[e] in m)
            Es = set(E)
            assume = [P.idx[e] if e in Es else -P.idx[e] for e in P.pairs]
            from s027_source import euler_violation
            ev = euler_violation(len(w), w, E)
            if ev:
                P.learn('EULER', ev['edges'], {'T': ev['T'], 'count': ev['count'], 'bound': ev['bound']}, gen)
                learned_kinds.add('EULER')
                continue
            for H, s, x in sol:
                if s.solve(assumptions=assume):
                    f = decode(H, w, set(v for v in s.get_model() if v > 0), x)
                    P.learn('CONTAIN', support(H, f), {'obstruction': H['name'], 'f': f, 'model': 0}, gen)
                    learned_kinds.add('CONTAIN')
                    break
            else:
                P.blocks.append({'name': 'b', 'edges': E})
                gen.add_clause([-P.idx[e] if e in Es else P.idx[e] for e in P.pairs])
        for _, s, _ in sol:
            s.delete()
    good = {'profile': 10, 'n': len(w), 'w': w, 'pairs': P.pairs, 'learned': P.learned, 'blocks': P.blocks}
    checker = ROOT / 'tools/s027_check_learned.py'

    def run(d, name):
        p = out / name
        with gzip.open(p, 'wt') as g:
            json.dump(d, g)
        return subprocess.run([sys.executable, str(checker), str(p)], capture_output=True, text=True).returncode

    assert run(good, 'good.json.gz') == 0
    rec['genuine_learned_clauses_accepted'] = len(P.learned)
    negs = {}
    c = next(L for L in P.learned if L['kind'] == 'CONTAIN')
    bad = copy.deepcopy(good)
    L = next(L for L in bad['learned'] if L['kind'] == 'CONTAIN')
    L['source_edges'] = L['source_edges'][1:]
    L['edges'] = sorted(map(list, L['source_edges']))
    negs['contain_missing_support_edge'] = run(bad, 'bad1.json.gz')
    bad = copy.deepcopy(good)
    L = next(L for L in bad['learned'] if L['kind'] == 'CONTAIN')
    L['perm'] = [3, 1, 2, 0] + list(range(4, len(w)))
    L['edges'] = sorted(sorted((L['perm'][a], L['perm'][b])) for a, b in L['source_edges'])
    negs['non_weight_preserving_perm'] = run(bad, 'bad2.json.gz')
    if 'EULER' in learned_kinds:
        bad = copy.deepcopy(good)
        L = next(L for L in bad['learned'] if L['kind'] == 'EULER')
        L['source_edges'] = L['source_edges'][:-1]
        L['edges'] = sorted(map(list, L['source_edges']))
        negs['euler_one_edge_short'] = run(bad, 'bad3.json.gz')
    assert all(v != 0 for v in negs.values()), negs
    rec['negative_controls_rejected'] = negs
    (out / 'SELFTEST.json').write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec))


if __name__ == '__main__':
    main(sys.argv[1])
