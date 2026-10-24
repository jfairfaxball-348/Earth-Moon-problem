"""POST-HOC explanatory diagnostic (not part of the registered D077 gate).

For each saved state, exact effect on the independent-four-set count of every
single union-edge swap (remove e in the union, add an absent pair f), with NO
planarity, layer or move-family constraint:
    delta(e,f) = |{Q: Q meets the union only in e, f not in Q}| - |{Q in H: f in Q}|.
If min delta >= 0, no single swap of ANY kind lowers the count: the obstruction is
the fixed-edge-budget four-set landscape itself, not layer occupancy or moves.
Stdlib only; each delta is cross-checked by direct recount on a sample.
"""
import itertools as it
import json
from pathlib import Path
import random
import time

ROOT = Path(__file__).resolve().parents[1]
FOURS = list(it.combinations(range(28), 4))


def analyse(es):
    union = set(map(tuple, es[0])) | set(map(tuple, es[1]))
    absent = [e for e in it.combinations(range(28), 2) if e not in union]
    H_mask, only = 0, {e: 0 for e in union}
    by_pair = {e: 0 for e in it.combinations(range(28), 2)}
    for i, q in enumerate(FOURS):
        inside = [e for e in it.combinations(q, 2) if e in union]
        bit = 1 << i
        for e in it.combinations(q, 2):
            by_pair[e] |= bit
        if not inside:
            H_mask |= bit
        elif len(inside) == 1:
            only[inside[0]] |= bit
    base = H_mask.bit_count()
    kill = {f: (H_mask & by_pair[f]).bit_count() for f in absent}
    best, histogram = None, {}
    for e in union:
        for f in absent:
            d = (only[e] & ~by_pair[f]).bit_count()-kill[f]
            histogram[d] = histogram.get(d, 0)+1
            if best is None or d < best[0]:
                best = d, e, f
    rng = random.Random(4040)
    for e, f in [(best[1], best[2])]+[(rng.choice(sorted(union)), rng.choice(absent)) for _ in range(20)]:
        new = (union-{e}) | {f}
        direct = sum(not any(p in new for p in it.combinations(q, 2)) for q in FOURS)
        assert direct-base == (only[e] & ~by_pair[f]).bit_count()-kill[f]
    critical = sorted(only[e].bit_count() for e in union)
    return dict(independent_four_sets=base, union_edges=len(union), absent_pairs=len(absent), swaps=len(union)*len(absent),
                min_swap_delta=best[0], min_swap=[list(best[1]), list(best[2])],
                improving_swaps=sum(c for d, c in histogram.items() if d < 0),
                neutral_swaps=histogram.get(0, 0), max_kill=max(kill.values()), min_critical=critical[0],
                free_union_edges=critical.count(0), best_kill_pair=list(max(kill, key=kill.get)),
                critical_quartiles=[critical[len(critical)*i//4] for i in range(4)]+[critical[-1]])


def main():
    start = time.process_time()
    states = [(f'validation/S039/arms/{d}-{s}-star.json', 'best') for d, s in ((156, 3900), (155, 3901))]
    states += [(str(p.relative_to(ROOT)).replace('\\', '/'), 'best') for p in sorted((ROOT/'validation/S040/arms').glob('*.json'))
               if p.name != 'SUMMARY.json']
    rows = []
    for path, key in states:
        data = json.loads((ROOT/path).read_text())[key]
        r = analyse((data['E1'], data['E2']))
        r['path'] = path
        rows.append(r)
        print(json.dumps(r), flush=True)
    out = dict(status='POSTHOC_EXPLANATORY_NOT_REGISTERED', rows=rows, cpu_seconds=time.process_time()-start)
    (ROOT/'validation/S040/POSTHOC_SWAPS.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')


if __name__ == '__main__':
    main()
