"""Simultaneous disk patches in both planar layers; final disjointness only."""
from collections import Counter
import gzip
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s038_patch import candidates, covered, explicit, fillings, load_start, move_record, universe
from s037_check_pair import check


def raw_moves(plane, r, cover):
    result = {}
    for patch in plane.patches(r):
        if patch['r'] != r:
            continue
        outside = plane.edges-patch['removed']
        for ds, fs in fillings(patch['boundary'], patch['quadrilateral']):
            if ds & outside or ds == patch['removed']:
                continue
            removed, added = tuple(sorted(patch['removed']-ds)), tuple(sorted(ds-patch['removed']))
            es = outside | ds
            # Here cover keys enumerate all edges in deterministic lex order.
            mask = sum(1 << (a*plane.n-a*(a+1)//2+b-a-1) for a, b in es)
            result[removed, added] = dict(patch=patch, diagonals=ds, filling=fs, edges=es,
                                          edge_mask=mask, hits=covered(es, cover))
    return result


def coupled_choices(planes, splits, cover, full):
    raw = {(k, r): raw_moves(planes[k], r, cover) for k, r in {(0, a) for a, b in splits} | {(1, b) for a, b in splits}}
    for a, b in splits:
        for key0, m0 in sorted(raw[0, a].items()):
            for key1, m1 in sorted(raw[1, b].items()):
                if m0['edge_mask'] & m1['edge_mask']:
                    continue
                value = (full & ~(m0['hits'] | m1['hits'])).bit_count()
                yield (a, b), key0, key1, value, m0, m1


def joint_move(split, score, m0, m1):
    return dict(split=split, score=score,
                layers=[move_record(k, m['patch'], m['diagonals'], m['filling'], score) for k, m in enumerate((m0, m1))])


def exhaustive(density):
    start = time.process_time()
    planes, initial, source = load_start(density)
    cover, full = universe(28)
    rows = []
    summaries = {}
    best = None
    for split in ((1, 1), (1, 2), (2, 1)):
        histogram = Counter()
        for _, k0, k1, value, m0, m1 in coupled_choices(planes, (split,), cover, full):
            histogram[value] += 1
            rows.append(dict(split=split, moves=[k0, k1], score=value))
            if best is None or value < best['score']:
                trial = [planes[k].replace(m['patch'], m['filling']) for k, m in enumerate((m0, m1))]
                best = joint_move(split, value, m0, m1)
                best['pair'] = explicit(trial, value)
        summaries[str(split)] = dict(neighbors=sum(histogram.values()),
                                    minimum_score=min(histogram),
                                    strict_improvements=sum(c for s, c in histogram.items() if s < initial['independent_four_sets']),
                                    histogram=dict(sorted(histogram.items())))
    validation = check(best['pair'], density)
    result = dict(source=source, density=density, baseline=initial['independent_four_sets'], neighborhoods=summaries,
                  best=best, independent_best_check=validation,
                  cpu_seconds=time.process_time()-start)
    out = ROOT/f'validation/S038/coupled/neighborhood-{density}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    out.with_suffix('.json.gz').write_bytes(gzip.compress(json.dumps(rows, separators=(',', ':')).encode(), mtime=0))
    print('COUPLED EXHAUSTIVE', density, {k: (v['neighbors'], v['minimum_score'], v['strict_improvements']) for k, v in summaries.items()}, flush=True)
    return result


def search(density, number):
    start_cpu, start_wall = time.process_time(), time.monotonic()
    planes, initial, source = load_start(density)
    cover, full = universe(28)
    rng = random.Random(number)
    best = explicit(planes, initial['independent_four_sets'])
    history, trace, tabu = [], [], {}
    last_improvement = 0
    evaluations = 0
    stop = 'SWEEP_CAP'
    for sweep in range(200):
        if time.process_time()-start_cpu >= 30:
            stop = 'CPU_CAP'
            break
        if sweep-last_improvement >= 30:
            stop = 'PLATEAU_30_SWEEPS'
            break
        chosen = None
        for split, key0, key1, score, m0, m1 in coupled_choices(planes, ((1, 1), (1, 2), (2, 1)), cover, full):
            evaluations += 1
            if tabu.get((key0, key1), -1) >= sweep and score >= best['independent_four_sets']:
                continue
            key = score, rng.random()
            if chosen is None or key < chosen[0]:
                chosen = key, split, key0, key1, m0, m1
        # Single-layer moves remain available, so the diagnostic does not force
        # changing both layers if a simpler improving move exists.
        for score, k, patch, ds, fs in candidates(planes, cover, full, guided_limit=64):
            evaluations += 1
            move_key = tuple(sorted(patch['removed']-ds)), tuple(sorted(ds-patch['removed']))
            if tabu.get((k, move_key), -1) >= sweep and score >= best['independent_four_sets']:
                continue
            key = score, rng.random()
            if chosen is None or key < chosen[0]:
                chosen = key, k, move_key, patch, ds, fs
        assert chosen is not None
        score = chosen[0][0]
        if isinstance(chosen[1], tuple):
            _, split, key0, key1, m0, m1 = chosen
            trace.append(dict(sweep=sweep, **joint_move(split, score, m0, m1)))
            planes = [planes[k].replace(m['patch'], m['filling']) for k, m in enumerate((m0, m1))]
            tabu[(key0[1], key0[0]), (key1[1], key1[0])] = sweep+7
        else:
            _, k, move_key, patch, ds, fs = chosen
            trace.append(dict(sweep=sweep, single_layer=move_record(k, patch, ds, fs, score)))
            planes[k] = planes[k].replace(patch, fs)
            tabu[k, (move_key[1], move_key[0])] = sweep+7
        assert not planes[0].edges & planes[1].edges
        if score < best['independent_four_sets']:
            best, last_improvement = explicit(planes, score), sweep
            history.append(dict(sweep=sweep, score=score, cpu_seconds=time.process_time()-start_cpu))
        if score == 0:
            stop = 'ALPHA3_REQUIRES_INDEPENDENT_VALIDATION'
            break
    return dict(source=source, density=density, seed=number, method='coupled', best=best,
                trace=trace, best_history=history, sweeps=sweep+1, candidate_evaluations=evaluations,
                cpu_seconds=time.process_time()-start_cpu, wall_seconds=time.monotonic()-start_wall,
                cpu_cap=30, stop=stop, verdict='HEURISTIC_UNKNOWN')


if __name__ == '__main__':
    assert json.loads((ROOT/'validation/S038/CONTROLS.json').read_text())['status'] == 'PASS'
    for density in (156, 155):
        exhaustive(density)
    rows = []
    for density in (156, 155):
        for number in (3810, 3811):
            result = search(density, number)
            out = ROOT/f'validation/S038/coupled/arm-{density}-{number}.json'
            out.write_text(json.dumps(result, indent=2)+'\n', newline='\n')
            rows.append({k: v for k, v in result.items() if k not in ('best', 'trace', 'best_history')})
            rows[-1]['best_violations'] = result['best']['independent_four_sets']
            (out.parent/'SUMMARY.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
            print(json.dumps(rows[-1]), flush=True)
            if result['best']['independent_four_sets'] == 0:
                break
