"""Registered star neighborhoods, matched search and protected-core seed arms."""
from collections import Counter
import gzip
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s038_patch import Plane, boundary, candidates, covered, explicit, move_record, universe
from s039_star import core, load_start, seed, star_candidates
from s037_check_pair import check


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')


def enumerate_stars(density):
    start = time.process_time()
    planes, initial, source = load_start(density)
    cover, full = universe(28)
    unique = {}
    best = None
    cases = Counter()
    for value, k, fs, move in star_candidates(planes, cover, full):
        key = k, tuple(map(tuple, move['removed'])), tuple(map(tuple, move['added']))
        if key in unique:
            assert unique[key] == value
        unique[key] = value
        cases['quad' if move['quad_incident'] else 'ordinary'] += 1
        if best is None or value < best['score']:
            trial = list(planes); trial[k] = Plane(28, fs)
            best = dict(score=value, move=move, pair=explicit(trial, value))
    histogram = Counter(unique.values())
    result = dict(source=source, density=density, baseline=initial['independent_four_sets'],
                  neighbors=len(unique), minimum_score=min(histogram),
                  strict_improvements=sum(c for s, c in histogram.items() if s < initial['independent_four_sets']),
                  histogram=dict(sorted(histogram.items())), generated_case_counts=dict(cases), best=best,
                  independent_best_check=check(best['pair'], density), cpu_seconds=time.process_time()-start)
    out = ROOT/f'validation/S039/neighborhood-{density}.json'
    dump(out, result)
    rows = [dict(layer=k, removed=removed, added=added, score=value) for (k, removed, added), value in sorted(unique.items())]
    out.with_suffix('.json.gz').write_bytes(gzip.compress(json.dumps(rows, separators=(',', ':')).encode(), mtime=0))
    print('STAR NEIGHBORHOOD', density, len(unique), 'minimum', min(histogram), 'improving', result['strict_improvements'], flush=True)


def choices(planes, cover, full, method, protected=None):
    protected = protected or (set(), set())
    for value, k, patch, ds, fs in candidates(planes, cover, full, guided_limit=64):
        move = move_record(k, patch, ds, fs, value)
        if set(map(tuple, move['removed'])) & protected[k]:
            continue
        move['kind'] = 'patch'
        new_faces = [f for i, f in enumerate(planes[k].faces) if i not in set(patch['selected'])]+list(fs)
        yield value, k, new_faces, move
    if method == 'star':
        yield from star_candidates(planes, cover, full, protected=protected)


def search(planes, source, number, method, cap=15, plateau=50, sweeps=500, protected=None):
    start_cpu, start_wall = time.process_time(), time.monotonic()
    rng = random.Random(number)
    cover, full = universe(28)
    initial = (full ^ covered(planes[0].edges | planes[1].edges, cover)).bit_count()
    best = explicit(planes, initial)
    trace, history, tabu = [], [], {}
    last = evaluations = 0
    stop = 'SWEEP_CAP'
    for step in range(sweeps):
        if time.process_time()-start_cpu >= cap:
            stop = 'CPU_CAP'
            break
        if step-last >= plateau:
            stop = 'PLATEAU'
            break
        chosen = None
        for value, k, fs, move in choices(planes, cover, full, method, protected):
            evaluations += 1
            removed, added = tuple(map(tuple, move['removed'])), tuple(map(tuple, move['added']))
            if tabu.get((k, removed, added), -1) >= step and value >= best['independent_four_sets']:
                continue
            rank = value, rng.random()
            if chosen is None or rank < chosen[0]:
                chosen = rank, k, fs, move
        if chosen is None:
            stop = 'NO_ADMISSIBLE_MOVE'
            break
        rank, k, fs, move = chosen
        value = rank[0]
        removed, added = tuple(map(tuple, move['removed'])), tuple(map(tuple, move['added']))
        tabu[k, added, removed] = step+7
        move['step'] = step
        trace.append(move)
        planes[k] = Plane(28, fs)
        assert not planes[0].edges & planes[1].edges
        if protected:
            assert all(protected[i] <= planes[i].edges for i in (0, 1))
        if value < best['independent_four_sets']:
            best, last = explicit(planes, value), step
            history.append(dict(step=step, score=value, kind=move['kind'], cpu_seconds=time.process_time()-start_cpu))
        if value == 0:
            stop = 'ALPHA3_REQUIRES_INDEPENDENT_VALIDATION'
            break
    return dict(source=source, seed=number, method=method, best=best, trace=trace, best_history=history,
                protected_core=bool(protected), steps=step+1, candidate_evaluations=evaluations,
                cpu_cap=cap, cpu_seconds=time.process_time()-start_cpu, wall_seconds=time.monotonic()-start_wall,
                stop=stop, verdict='HEURISTIC_UNKNOWN')


def seed_variant(number, record):
    planes = [Plane(28, fs) for fs in record['faces']]
    _, protected, colours, proof = core()
    cover, full = universe(28)
    density = len(planes[0].edges)+len(planes[1].edges)
    deleted = None
    if number % 2 and density == 156:
        def score(e):
            return (full ^ covered(planes[0].edges | (planes[1].edges-{e}), cover)).bit_count()
        deleted = min(sorted(planes[1].edges-protected[1]), key=score)
        selected = planes[1].inc[deleted]
        quad = boundary([planes[1].faces[i] for i in selected])
        assert quad and len(quad) == 4
        planes[1] = Plane(28, [f for i, f in enumerate(planes[1].faces) if i not in selected]+[quad])
    value = (full ^ covered(planes[0].edges | planes[1].edges, cover)).bit_count()
    return planes, explicit(planes, value), deleted


def main():
    out = ROOT/'validation/S039'
    assert json.loads((out/'CONTROLS.json').read_text())['status'] == 'PASS'
    for density in (156, 155):
        enumerate_stars(density)
    rows = []
    for density in (156, 155):
        for number in (3900, 3901):
            for method in ('patch', 'star'):
                planes, _, source = load_start(density)
                result = search(planes, source, number, method)
                dump(out/f'arms/{density}-{number}-{method}.json', result)
                rows.append({k: v for k, v in result.items() if k not in ('best', 'trace', 'best_history')})
                rows[-1]['best_violations'] = result['best']['independent_four_sets']
                dump(out/'arms/SUMMARY.json', rows)
                print(json.dumps(rows[-1]), flush=True)
                if result['best']['independent_four_sets'] == 0:
                    return
    seed_summary = []
    _, protected, _, _ = core()
    for number in (3910, 3911, 3912, 3913):
        start = time.process_time()
        record = seed(number)
        if 'pair' not in record:
            dump(out/f'seeds/{number}.json', record)
            seed_summary.append(dict(seed=number, status=record['status'], cpu_seconds=time.process_time()-start))
            continue
        cover, full = universe(28)
        record['pair']['independent_four_sets'] = (full ^ covered(set(map(tuple, record['pair']['E1'])) | set(map(tuple, record['pair']['E2'])), cover)).bit_count()
        planes, variant, deleted = seed_variant(number, record)
        record.update(variant=variant, variant_faces=[p.faces for p in planes], deleted_edge=deleted,
                      generation_cpu_seconds=time.process_time()-start)
        source = f'validation/S039/seeds/{number}.json'
        dump(ROOT/source, record)
        result = search(planes, source, number, 'star', cap=20, plateau=40, sweeps=150, protected=protected)
        dump(out/f'protected/{number}.json', result)
        seed_summary.append(dict(seed=number, density=variant['density'],
                                 initial_violations=variant['independent_four_sets'],
                                 best_violations=result['best']['independent_four_sets'],
                                 generation_cpu_seconds=record['generation_cpu_seconds'], cpu_seconds=result['cpu_seconds'],
                                 stop=result['stop']))
        dump(out/'protected/SUMMARY.json', seed_summary)
        print('PROTECTED', json.dumps(seed_summary[-1]), flush=True)
        if result['best']['independent_four_sets'] == 0:
            return


if __name__ == '__main__':
    main()
