"""Adversarial control for the S027 domain formulas' edge bound (no new claim).

For profiles 0..29 the generator encodes 'blow-up edges <= 156' by copying each
base-edge variable w_a*w_b times and applying a pysat sequential counter. A too
strong encoding would make domain UNSAT claims unsound. For every profile and
seeded random base graphs, fix the base-edge variables by unit assumptions and
check SAT exactly when the explicit blow-up edge count is <= 156, including
graphs pushed to counts 155, 156, 157 by greedy edge addition.
"""
import itertools as it, json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from s027_source import profiles

rng = random.Random(270099); tests = 0; boundary = 0
for no, (n, w) in enumerate(profiles()):
    pairs = list(it.combinations(range(n), 2)); idx = {e: i + 1 for i, e in enumerate(pairs)}
    top, units, cls = len(pairs), [], []
    for e, x in idx.items():
        for _ in range(w[e[0]] * w[e[1]]):
            top += 1; cls += [[-x, top], [x, -top]]; units.append(top)
    inside = sum(x * (x - 1) // 2 for x in w)
    card = CardEnc.atmost(units, 156 - inside, top_id=top, encoding=EncType.seqcounter)
    with Solver(name='cadical195', bootstrap_with=cls + card.clauses) as s:
        for t in range(40):
            order = pairs[:]; rng.shuffle(order); E = set(); cnt = inside
            target = rng.choice([150, 155, 156, 157, 160])
            for e in order:
                if cnt + w[e[0]] * w[e[1]] <= target:
                    E.add(e); cnt += w[e[0]] * w[e[1]]
            if t % 2:
                extra = [e for e in order if e not in E]
                if extra: E.add(extra[0]); cnt += w[extra[0][0]] * w[extra[0][1]]
            ok = s.solve(assumptions=[idx[e] if e in E else -idx[e] for e in pairs])
            assert ok == (cnt <= 156), (no, cnt, ok)
            tests += 1; boundary += cnt in (155, 156, 157)
print(json.dumps({'profiles': 30, 'tests': tests, 'near_boundary_counts': boundary, 'verdict': 'PASS'}))
