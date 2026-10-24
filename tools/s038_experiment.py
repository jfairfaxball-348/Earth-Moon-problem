"""Registered finite neighborhoods followed by matched capped discovery arms."""
from collections import Counter
import gzip
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s038_patch import candidates, covered, explicit, load_start, move_record, universe


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8', newline='\n')


def enumerate_start(density):
    start = time.process_time()
    planes, data, source = load_start(density)
    cover, full = universe(28)
    output, rows = {}, []
    for r in (1, 2, 3):
        unique = {}
        best_move = None
        for score, k, patch, ds, fs in candidates(planes, cover, full, sizes=(r,)):
            removed = tuple(sorted(patch['removed']-ds))
            added = tuple(sorted(ds-patch['removed']))
            key = k, removed, added
            if key in unique:
                assert unique[key] == score
            unique[key] = score
            if best_move is None or score < best_move['score']:
                best_move = move_record(k, patch, ds, fs, score)
        hist = Counter(unique.values())
        output[str(r)] = dict(distinct_neighbors=len(unique), histogram=dict(sorted(hist.items())),
                              minimum_score=min(hist), strict_improvements=sum(c for s, c in hist.items() if s < data['independent_four_sets']),
                              best_move=best_move)
        rows.extend(dict(support_size=r, layer=k, removed=removed, added=added, score=score)
                    for (k, removed, added), score in sorted(unique.items()))
    out = ROOT/f'validation/S038/neighborhood-{density}.json'
    result = dict(density=density, source=source, baseline=data['independent_four_sets'],
                  neighborhoods=output, cpu_seconds=time.process_time()-start)
    dump(out, result)
    raw = json.dumps(rows, separators=(',', ':')).encode()
    out.with_suffix('.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    print('EXHAUSTIVE', density, {r: (v['distinct_neighbors'], v['minimum_score'], v['strict_improvements']) for r, v in output.items()}, flush=True)
    return result


def search(density, number, method):
    start_cpu, start_wall = time.process_time(), time.monotonic()
    planes, initial, source = load_start(density)
    cover, full = universe(28)
    rng = random.Random(number)
    value = initial['independent_four_sets']
    best = explicit(planes, value)
    history = []
    trace = []
    tabu = {}
    last_improve = 0
    evaluations = 0
    sizes = (1,) if method == 'single' else (1, 2, 3)
    stop = 'SWEEP_CAP'
    for sweep in range(2000):
        if time.process_time()-start_cpu >= 20:
            stop = 'CPU_CAP'
            break
        if sweep-last_improve >= 100:
            stop = 'PLATEAU_100_SWEEPS'
            break
        choices = []
        for score, k, patch, ds, fs in candidates(planes, cover, full, sizes=sizes,
                                                guided_limit=64 if method == 'patch' else None):
            evaluations += 1
            removed, added = tuple(sorted(patch['removed']-ds)), tuple(sorted(ds-patch['removed']))
            if tabu.get((k, removed, added), -1) >= sweep and score >= best['independent_four_sets']:
                continue
            choices.append((score, rng.random(), k, patch, ds, fs))
        if not choices:
            stop = 'NO_ADMISSIBLE_MOVE'
            break
        score, _, k, patch, ds, fs = min(choices, key=lambda x: x[:2])
        move = move_record(k, patch, ds, fs, score)
        move['sweep'] = sweep
        trace.append(move)
        removed, added = tuple(sorted(patch['removed']-ds)), tuple(sorted(ds-patch['removed']))
        tabu[k, added, removed] = sweep+7
        planes[k] = planes[k].replace(patch, fs)
        value = score
        assert not planes[0].edges & planes[1].edges
        if value < best['independent_four_sets']:
            best, last_improve = explicit(planes, value), sweep
            history.append(dict(sweep=sweep, score=value, support_size=patch['r'],
                                actually_removed=len(removed), cpu_seconds=time.process_time()-start_cpu))
        if value == 0:
            stop = 'ALPHA3_REQUIRES_INDEPENDENT_VALIDATION'
            break
    return dict(source=source, method=method, seed=number, density=density, best=best,
                best_history=history, trace=trace, sweeps=sweep+1, candidate_evaluations=evaluations,
                stop=stop, cpu_cap=20, cpu_seconds=time.process_time()-start_cpu,
                wall_seconds=time.monotonic()-start_wall, verdict='HEURISTIC_UNKNOWN')


def main():
    v = ROOT/'validation/S038'
    assert json.loads((v/'SMOKE.json').read_text())['verdict'] == 'PASS'
    assert json.loads((v/'CONTROLS.json').read_text())['status'] == 'PASS'
    for density in (156, 155):
        enumerate_start(density)
    summary = []
    for density in (156, 155):
        for number in (3800, 3801, 3802):
            for method in ('single', 'patch'):
                row = search(density, number, method)
                name = f'{density}-{number}-{method}'
                dump(v/f'arms/{name}.json', row)
                summary.append({k: val for k, val in row.items() if k not in ('best', 'best_history', 'trace')})
                summary[-1]['best_violations'] = row['best']['independent_four_sets']
                dump(v/'arms/SUMMARY.json', summary)
                print(json.dumps(summary[-1]), flush=True)
                if row['best']['independent_four_sets'] == 0:
                    return


if __name__ == '__main__':
    main()
