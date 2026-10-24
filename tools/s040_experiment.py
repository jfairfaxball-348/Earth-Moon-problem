"""S040 registered experiment: exact coordinated neighborhoods, diagnostics, matched arms."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from check_s038_records import edges_of, patch_replay
from check_s039_records import star_replay
from s038_patch import Plane, covered, explicit, universe
from s039_experiment import choices, search as s039_search
from s039_star import core
from s040_coordinated import Table, faces_after, load_pair, pair_scores, single_scores
from s040_diagnose import diagnose
from s037_check_pair import check

OUT = ROOT/'validation/S040'
INPUTS = {156: 'validation/S039/arms/156-3900-star.json', 155: 'validation/S039/arms/155-3901-star.json'}
PROTECTED_INPUT = 'validation/S039/protected/3912.json'


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')


def registered():
    reg = json.loads((OUT/'REGISTRATION.json').read_text())
    assert hashlib.sha256((ROOT/'sessions/S040/PLAN.md').read_bytes()).hexdigest() == reg['sha256']['sessions/S040/PLAN.md']
    assert json.loads((OUT/'CONTROLS.json').read_text())['status'] == 'PASS'


def edge_list(xs):
    return [list(e) for e in sorted(xs)]


def pair_move(t, i, j, kind, score):
    comps = []
    for k, idx in ((0, i), (1, j)):
        rem, add = t[k].keys[idx]
        conflicts = add & t[1-k].plane.edges
        comps.append(dict(t[k].effects[idx]['move'], layer=k, conflicts=edge_list(conflicts)))
    return dict(kind='pair', type=int(kind), components=comps, score=int(score))


def neighborhood(density):
    start = time.process_time()
    planes, data = load_pair(INPUTS[density])
    cover, full = universe(28)
    base = data['independent_four_sets']
    t = [Table(planes[k], planes[1-k].edges, cover) for k in (0, 1)]
    singles = []
    for k in (0, 1):
        legal, scores = single_scores(t[k], covered(planes[1-k].edges, cover))
        singles += [(k, int(i), int(s)) for i, s in zip(legal, scores)]
    I, J, T, S = pair_scores(t[0], t[1])
    rows = []
    for k, i, s in singles:
        rem, add = t[k].keys[i]
        rows.append(json.dumps(['single', k, edge_list(rem), edge_list(add), s], separators=(',', ':')))
    for i, j, kind, s in zip(I.tolist(), J.tolist(), T.tolist(), S.tolist()):
        (r0, a0), (r1, a1) = t[0].keys[i], t[1].keys[j]
        rows.append(json.dumps(['pair', kind, edge_list(r0), edge_list(a0), edge_list(r1), edge_list(a1), s], separators=(',', ':')))
    rows.sort()
    digest = hashlib.sha256('\n'.join(rows).encode()).hexdigest()
    per = {}
    single_scores_all = [s for _, _, s in singles]
    per['single'] = dict(count=len(singles), minimum=min(single_scores_all),
                         strict_improvements=sum(s < base for s in single_scores_all),
                         histogram=dict(sorted(Counter(single_scores_all).items())))
    bests = {}
    for kind in (0, 1, 2):
        mask = T == kind
        scores = S[mask]
        per[f'type{kind}'] = dict(count=int(mask.sum()), minimum=int(scores.min()) if scores.size else None,
                                 strict_improvements=int((scores < base).sum()),
                                 histogram={int(a): int(b) for a, b in zip(*np.unique(scores, return_counts=True))})
        if scores.size:
            pick = np.nonzero(mask)[0][int(np.argmin(scores))]
            i, j = int(I[pick]), int(J[pick])
            new = [Plane(28, faces_after(planes[0], t[0].effects[i])), Plane(28, faces_after(planes[1], t[1].effects[j]))]
            pair = explicit(new, int(S[pick]))
            bests[f'type{kind}'] = dict(move=pair_move(t, i, j, kind, S[pick]), pair=pair,
                                        independent_check=check(pair, density))
    k, i, s = min(singles, key=lambda x: x[2])
    new = list(planes)
    new[k] = Plane(28, faces_after(planes[k], t[k].effects[i]))
    pair = explicit(new, s)
    bests['single'] = dict(move=dict(t[k].effects[i]['move'], layer=k, score=s), pair=pair,
                           independent_check=check(pair, density))
    result = dict(source=INPUTS[density], density=density, baseline=base, components=[t[0].size, t[1].size],
                  conflicted_components=[int(t[0].conflicted.sum()), int(t[1].conflicted.sum())],
                  by_kind=per, bests=bests, canonical_table_sha256=digest, table_rows=len(rows),
                  cpu_seconds=time.process_time()-start)
    dump(OUT/f'neighborhood-{density}.json', result)
    table = dict(components=[[[edge_list(r), edge_list(a)] for r, a in tt.keys] for tt in t],
                 singles=singles, pairs=[I.tolist(), J.tolist(), T.tolist(), S.tolist()])
    (OUT/f'neighborhood-{density}.json.gz').write_bytes(gzip.compress(json.dumps(table, separators=(',', ':')).encode(), mtime=0))
    print('NEIGHBORHOOD', density, json.dumps({k: (v['count'], v['minimum'], v['strict_improvements']) for k, v in per.items()}),
          'cpu', round(result['cpu_seconds'], 3), flush=True)
    return result


def search_coord(planes, source, number, method, cap=150, plateau=30, sweeps=400, protected=None):
    start_cpu, start_wall = time.process_time(), time.monotonic()
    rng = random.Random(number)
    cover, full = universe(28)
    types = (0,) if method == 'pair0' else (0, 1, 2)
    prot = [frozenset(x) for x in protected] if protected else [frozenset(), frozenset()]
    initial = (full ^ covered(planes[0].edges | planes[1].edges, cover)).bit_count()
    best = explicit(planes, initial)
    trace, history, tabu = [], [], {}
    last = evaluations = pair_evaluations = 0
    stop = 'SWEEP_CAP'
    for step in range(sweeps):
        if time.process_time()-start_cpu >= cap:
            stop = 'CPU_CAP'
            break
        if step-last >= plateau:
            stop = 'PLATEAU'
            break
        bound = best['independent_four_sets']
        chosen = None
        for value, k, fs, move in choices(planes, cover, full, 'star', protected):
            evaluations += 1
            removed, added = tuple(map(tuple, move['removed'])), tuple(map(tuple, move['added']))
            if tabu.get((k, removed, added), -1) >= step and value >= bound:
                continue
            rank = value, rng.random()
            if chosen is None or rank < chosen[0]:
                chosen = rank, ('single', k, fs, move)
        t = [Table(planes[k], planes[1-k].edges, cover, prot[k]) for k in (0, 1)]
        I, J, T, S = pair_scores(t[0], t[1], types)
        pair_evaluations += len(I)
        ok = np.ones(len(I), dtype=bool)
        for key, expiry in tabu.items():
            if expiry >= step and key[0] == 'pair':
                i, j = t[0].index.get(key[1]), t[1].index.get(key[2])
                if i is not None and j is not None:
                    ok &= ~((I == i) & (J == j) & (S >= bound))
        if ok.any():
            m = int(S[ok].min())
            ties = np.nonzero(ok & (S == m))[0]
            pick = int(ties[rng.randrange(len(ties))])
            rank = m, rng.random()
            if chosen is None or rank < chosen[0]:
                chosen = rank, ('pair', pick)
        if chosen is None:
            stop = 'NO_ADMISSIBLE_MOVE'
            break
        rank, choice = chosen
        value = rank[0]
        if choice[0] == 'single':
            _, k, fs, move = choice
            removed, added = tuple(map(tuple, move['removed'])), tuple(map(tuple, move['added']))
            tabu[k, added, removed] = step+7
            planes[k] = Plane(28, fs)
        else:
            pick = choice[1]
            i, j, kind = int(I[pick]), int(J[pick]), int(T[pick])
            move = pair_move(t, i, j, kind, value)
            keys = t[0].keys[i], t[1].keys[j]
            tabu['pair', (keys[0][1], keys[0][0]), (keys[1][1], keys[1][0])] = step+7
            planes = [Plane(28, faces_after(planes[0], t[0].effects[i])), Plane(28, faces_after(planes[1], t[1].effects[j]))]
        assert not planes[0].edges & planes[1].edges
        assert (full ^ covered(planes[0].edges | planes[1].edges, cover)).bit_count() == value
        if protected:
            assert all(protected[k] <= planes[k].edges for k in (0, 1))
        move['step'] = step
        trace.append(move)
        if value < best['independent_four_sets']:
            best, last = explicit(planes, value), step
            history.append(dict(step=step, score=value, kind=move['kind'], type=move.get('type'),
                                cpu_seconds=time.process_time()-start_cpu))
        if value == 0:
            stop = 'ALPHA3_REQUIRES_INDEPENDENT_VALIDATION'
            break
    return dict(source=source, seed=number, method=method, best=best, trace=trace, best_history=history,
                protected_core=bool(protected), steps=step+1, candidate_evaluations=evaluations,
                pair_evaluations=pair_evaluations, cpu_cap=cap, cpu_seconds=time.process_time()-start_cpu,
                wall_seconds=time.monotonic()-start_wall, stop=stop, verdict='HEURISTIC_UNKNOWN')


def replay_best_faces(result, planes):
    """Replay the trace with the frozen stdlib replayers up to the saved best."""
    fs = [list(p.faces) for p in planes]
    stop = result['best_history'][-1]['step'] if result['best_history'] else -1
    for m in result['trace'][:stop+1]:
        if m['kind'] == 'pair':
            fs = [star_replay(fs[c['layer']], c) for c in m['components']]
        elif m['kind'] == 'star':
            fs[m['layer']] = star_replay(fs[m['layer']], m)
        else:
            fs[m['layer']] = patch_replay(fs[m['layer']], m)
    assert [edges_of(f) for f in fs] == [set(map(tuple, result['best'][k])) for k in ('E1', 'E2')]
    return fs


def arm(path, seed, method, protected=None):
    planes, _ = load_pair(path)
    initial = list(planes)
    if method == 'star':
        result = s039_search(planes, path, seed, 'star', cap=150, plateau=30, sweeps=400, protected=protected)
        result['pair_evaluations'] = 0
        for h in result['best_history']:
            h['type'] = None
    else:
        result = search_coord(planes, path, seed, method, protected=protected)
    result['best_faces'] = replay_best_faces(result, initial)
    return result


def main():
    registered()
    total = 0.0
    hoods = [neighborhood(d) for d in (156, 155)]
    total += sum(h['cpu_seconds'] for h in hoods)
    diag = {}
    for density, path in INPUTS.items():
        start = time.process_time()
        planes, _ = load_pair(path)
        diag[f'input-{density}'] = d = diagnose(planes)
        d.update(source=path, cpu_seconds=time.process_time()-start)
        total += d['cpu_seconds']
        print('DIAGNOSTIC', density, d['independent_four_sets'], d['tau']['lower_packing'], d['tau']['upper_hitting'],
              json.dumps(d['summary']), 'locked', d['locked_four_sets'], flush=True)
        dump(OUT/'diagnostics'/f'input-{density}.json', d)
    rows = []
    witness = False
    _, protected_sets, _, _ = core()
    plan = [(f'{d}-{s}-{m}', INPUTS[d], s, m, None) for d in (156, 155) for s in (4000, 4001) for m in ('star', 'pair0', 'coord')]
    plan += [(f'protected-{s}-{m}', PROTECTED_INPUT, s, m, protected_sets) for s in (4010, 4011) for m in ('star', 'coord')]
    for name, path, seed, method, protected in plan:
        result = arm(path, seed, method, protected)
        total += result['cpu_seconds']
        dump(OUT/'arms'/f'{name}.json', result)
        row = {k: v for k, v in result.items() if k not in ('best', 'trace', 'best_history')}
        row.update(name=name, best_violations=result['best']['independent_four_sets'],
                   new_best_types=[h['type'] for h in result['best_history']])
        rows.append(row)
        dump(OUT/'arms'/'SUMMARY.json', rows)
        print('ARM', json.dumps(row), flush=True)
        assert total < 7200
        if result['best']['independent_four_sets'] == 0:
            witness = True
            break
    for row in rows:
        start = time.process_time()
        prot = [frozenset(x) for x in protected_sets] if row['name'].startswith('protected') else [frozenset(), frozenset()]
        planes = [Plane(28, f) for f in json.loads((OUT/'arms'/f"{row['name']}.json").read_text())['best_faces']]
        d = diagnose(planes, prot)
        d.update(source=f"validation/S040/arms/{row['name']}.json", cpu_seconds=time.process_time()-start)
        total += d['cpu_seconds']
        diag[row['name']] = d
        dump(OUT/'diagnostics'/f"{row['name']}.json", d)
        print('DIAGNOSTIC', row['name'], d['independent_four_sets'], d['tau']['lower_packing'], d['tau']['upper_hitting'],
              json.dumps(d['summary']), 'locked', d['locked_four_sets'], flush=True)
    summary = dict(status='FINISHED', witness_stop=witness, experimental_cpu_seconds=total,
                   neighborhood_cpu_seconds=sum(h['cpu_seconds'] for h in hoods),
                   arm_cpu_seconds=sum(r['cpu_seconds'] for r in rows),
                   diagnostic_cpu_seconds=sum(d['cpu_seconds'] for d in diag.values()), arms=len(rows))
    dump(OUT/'EXPERIMENT.json', summary)
    print('EXPERIMENT FINISHED', json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
