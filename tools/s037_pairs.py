"""Bounded discovery over combinatorial triangulations; every failure is UNKNOWN.

Faces are unordered triples on a sphere. A legal diagonal flip preserves its
embedding. Random walks are not exhaustive and no mixing claim is made.
"""
import argparse
import itertools as it
import json
import math
from pathlib import Path
import random
import time

ROOT = Path(__file__).resolve().parents[1]


def edge(a, b):
    return tuple(sorted((a, b)))


class Tri:
    def __init__(self, n, faces):
        self.n = n
        self.faces = set()
        self.inc = {}
        for f in faces:
            self.add(f)

    def add(self, f):
        f = tuple(sorted(f))
        assert f not in self.faces
        self.faces.add(f)
        for e in it.combinations(f, 2):
            self.inc.setdefault(e, set()).add(f)

    def remove(self, f):
        self.faces.remove(f)
        for e in it.combinations(f, 2):
            self.inc[e].remove(f)
            if not self.inc[e]:
                del self.inc[e]

    def flip(self, e):
        fs = list(self.inc[e])
        assert len(fs) == 2
        a, b = [next(v for v in f if v not in e) for f in fs]
        new = edge(a, b)
        if new in self.inc:
            return None
        for f in fs:
            self.remove(f)
        self.add((a, b, e[0]))
        self.add((a, b, e[1]))
        return new

    def relabel(self, a, b):
        def p(x):
            return b if x == a else a if x == b else x
        return Tri(self.n, [tuple(p(x) for x in f) for f in self.faces])


def seed(n, kind, rng):
    if kind == 'bipyramid':
        rim = list(range(2, n))
        t = Tri(n, [(h, rim[i], rim[(i+1) % len(rim)]) for h in (0, 1) for i in range(len(rim))])
    else:
        t = Tri(n, it.combinations(range(4), 3))
        for v in range(4, n):
            f = rng.choice(sorted(t.faces))
            t.remove(f)
            for a, b in it.combinations(f, 2):
                t.add((a, b, v))
    for _ in range(30*n):
        t.flip(rng.choice(sorted(t.inc)))
    assert len(t.inc) == 3*n-6 and len(t.faces) == 2*n-4
    assert all(len(fs) == 2 for fs in t.inc.values())
    return t


def masks(n):
    cover = {e: 0 for e in it.combinations(range(n), 2)}
    sets = list(it.combinations(range(n), 4))
    for i, vs in enumerate(sets):
        for e in it.combinations(vs, 2):
            cover[e] |= 1 << i
    return sets, cover, (1 << len(sets))-1


def independent(t, cover, full):
    covered = 0
    for e in t.inc:
        covered |= cover[e]
    return full ^ covered


def serialise(ts, density, cover, full, metadata):
    es = [set(t.inc) for t in ts]
    overlap = es[0] & es[1]
    if density == 155:
        if overlap:
            assert len(overlap) == 1
            deleted = next(iter(overlap))
        else:
            # Best deletion includes its newly exposed four-sets, not an estimate.
            def value(e):
                other = 0
                for x in (es[0] | es[1]) - {e}:
                    other |= cover[x]
                return (full ^ other).bit_count()
            deleted = min(sorted(es[1]), key=value)
        es[1].remove(deleted)
    assert not (es[0] & es[1])
    covered = 0
    for e in es[0] | es[1]:
        covered |= cover[e]
    return dict(n=ts[0].n, V=list(range(ts[0].n)), E1=sorted(es[0]), E2=sorted(es[1]),
                independent_four_sets=(full ^ covered).bit_count(),
                density=density, metadata=metadata)


def experiment(seed_number, density, mode, cpu_cap=30, proposals=15000):
    start_cpu, start_wall = time.process_time(), time.monotonic()
    rng = random.Random(seed_number)
    n = 28
    sets, cover, full = masks(n)
    kinds = ['stacked', 'bipyramid'] if seed_number % 2 else ['bipyramid', 'stacked']
    ts = [seed(n, kind, rng) for kind in kinds]
    inds = [independent(t, cover, full) for t in ts]
    budget = 156-density
    overlaps = len(ts[0].inc.keys() & ts[1].inc.keys())
    violations = (inds[0] & inds[1]).bit_count()
    score = 2000*max(0, overlaps-budget)+violations
    best = None
    first_feasible = None
    accepted = flips = swaps = invalid = 0
    progress = []
    stale = 0
    for step in range(proposals):
        if time.process_time()-start_cpu >= cpu_cap:
            break
        k = rng.randrange(2)
        old = ts[k]
        use_swap = rng.random() < (0.4 if overlaps > budget else (0.15 if mode == 'mixed' else 0.0))
        if mode == 'kick' and stale > 1200:
            use_swap = True
        if use_swap:
            a, b = rng.sample(range(n), 2)
            candidate = old.relabel(a, b)
            swaps += 1
            undo = None
        else:
            e = rng.choice(sorted(old.inc))
            undo = old.flip(e)
            if undo is None:
                invalid += 1
                continue
            candidate = old
            flips += 1
        overlap_new = len(candidate.inc.keys() & ts[1-k].inc.keys())
        # Once packed, every searched state stays in the required disjoint class.
        if overlaps <= budget and overlap_new > budget:
            if undo is not None:
                assert old.flip(undo) == e
            stale += 1
            continue
        ind = independent(candidate, cover, full)
        new_violations = (ind & inds[1-k]).bit_count()
        new_score = 2000*max(0, overlap_new-budget)+new_violations
        temperature = 1200 if overlaps > budget else (0.5+3.0*(1-(step % 2500)/2500))
        accept = new_score <= score or rng.random() < math.exp(max(-700, (score-new_score)/temperature))
        if accept:
            ts[k], inds[k] = candidate, ind
            overlaps, violations, score = overlap_new, new_violations, new_score
            accepted += 1
            if overlaps <= budget:
                if first_feasible is None:
                    first_feasible = step
                # Exact 155 objective includes deletion when underlying pair is disjoint.
                if best is None or violations < best['independent_four_sets']:
                    state = serialise(ts, density, cover, full, dict(seed=seed_number, mode=mode, step=step))
                    if best is None or state['independent_four_sets'] < best['independent_four_sets']:
                        best = state
                        stale = 0
                        progress.append([step, best['independent_four_sets'], round(time.process_time()-start_cpu, 4)])
            if best and best['independent_four_sets'] == 0:
                break
        elif undo is not None:
            assert old.flip(undo) == e
        stale += 1
    return dict(seed=seed_number, mode=mode, density=density, seed_kinds=kinds,
                proposals=step+1, accepted=accepted, flips=flips, swaps=swaps,
                invalid_flips=invalid, final_overlap=overlaps,
                first_feasible_step=first_feasible, best=best,
                progress=progress, cpu_seconds=time.process_time()-start_cpu,
                wall_seconds=time.monotonic()-start_wall, verdict='HEURISTIC_UNKNOWN')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cpu-per-arm', type=float, default=40)
    ap.add_argument('--steps', type=int, default=15000)
    ap.add_argument('--arms', type=int, default=12)
    args = ap.parse_args()
    assert 0 < args.cpu_per_arm <= 50 and 0 < args.arms <= 12 and args.steps <= 15000
    gate = json.loads((ROOT/'validation/S037/SMOKE.json').read_text())
    assert gate['verdict'] == 'PASS' and gate['chromatic_rows_verified'] == 271
    assert json.loads((ROOT/'validation/S037/SYMMETRY.json').read_text())['status'] == 'PASS'
    assert json.loads((ROOT/'validation/S037/CONTROLS.json').read_text())['status'] == 'PASS'
    out = ROOT/'validation/S037/pairs'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(args.arms):
        density = 156 if i % 2 == 0 else 155
        mode = ('flips', 'mixed', 'kick')[(i//2) % 3]
        r = experiment(3700+i, density, mode, args.cpu_per_arm, args.steps)
        path = out/f'arm-{i:02d}.json'
        path.write_text(json.dumps(r, indent=2)+'\n', newline='\n')
        rows.append({k: v for k, v in r.items() if k not in ('best', 'progress')})
        rows[-1]['best_violations'] = r['best']['independent_four_sets'] if r['best'] else None
        print(json.dumps(rows[-1]), flush=True)
        (out/'SUMMARY.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
        if r['best'] and r['best']['independent_four_sets'] == 0:
            break


if __name__ == '__main__':
    main()
