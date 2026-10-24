"""S041 registered probes P1 (order-13 layer symmetry) and P2 (counting tables), one process."""
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s041_z13 import A, B, N, S, classify, count_four, independent_four, layers, orbits
import s041_counting

OUT = ROOT/'validation/S041'


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')


def registered():
    reg = json.loads((OUT/'REGISTRATION.json').read_text())
    assert hashlib.sha256((ROOT/'sessions/S041/PLAN.md').read_bytes()).hexdigest() == reg['sha256']['sessions/S041/PLAN.md']


def p1():
    start = time.process_time()
    orb = orbits()
    records, planar = [], []
    tally = {}
    for names in layers(orb):
        r = classify(names, orb)
        key = 'PLANAR' if r['planar'] else r['certificate']['test']
        tally[key] = tally.get(key, 0)+1
        records.append(r)
        if r['planar']:
            planar.append(r)
    classify_cpu = time.process_time()-start
    pairs, alpha3, best = 0, [], None
    rng = random.Random(4100)
    sample_checks = 0
    for i, j in it.combinations(range(len(planar)), 2):
        L1, L2 = planar[i]['orbits'], planar[j]['orbits']
        if L1[0] == L2[0] or L1[1] == L2[1] or set(L1) & set(L2):
            continue
        pairs += 1
        edges = [e for n in L1+L2 for e in orb[n]]
        assert len(set(edges)) == 156
        witness = independent_four(edges)
        count = count_four(edges)
        assert (witness is None) == (count == 0)
        if witness is not None:
            es = set(edges)
            assert not any(tuple(sorted(p)) in es for p in it.combinations(witness, 2))
        if rng.random() < 0.05 or count < 60:
            es = set(edges)
            assert count == sum(not any(p in es for p in it.combinations(q, 2)) for q in it.combinations(range(28), 4))
            sample_checks += 1
        if best is None or count < best['independent_four_sets']:
            best = dict(layers=[L1, L2], independent_four_sets=count, example=witness)
        if count == 0:
            alpha3.append([L1, L2])
            break
    result = dict(status='FINISHED', vertex_labels=dict(N=N, S=S, A=A, B=B), orbit_names=sorted(orb),
                  layer_candidates=len(records), certificate_tally=tally, planar_layers=len(planar),
                  valid_pairs=pairs, alpha3_pairs=alpha3, best_pair=best, full_enumeration_cross_checks=sample_checks,
                  classify_cpu_seconds=classify_cpu, cpu_seconds=time.process_time()-start)
    dump(OUT/'P1_Z13.json', dict(result, planar_layer_records=planar))
    (OUT/'P1_Z13_layers.json.gz').write_bytes(gzip.compress(json.dumps(records, separators=(',', ':')).encode(), mtime=0))
    print('P1', json.dumps({k: v for k, v in result.items() if k not in ('orbit_names', 'vertex_labels')}), flush=True)
    return result


def p2():
    start = time.process_time()
    result = s041_counting.run()
    result['cpu_seconds'] = time.process_time()-start
    dump(OUT/'P2_COUNTING.json', result)
    print('P2 mycielski feasible', result['mycielski']['counting_feasible'][:5], 'chi10 join types', result['chi10_join_types'],
          'unbounded', result['chi10_unbounded_types'], flush=True)
    return result


def main():
    registered()
    r1 = p1()
    r2 = p2()
    total = r1['cpu_seconds']+r2['cpu_seconds']
    assert total < 1800
    dump(OUT/'PROBES.json', dict(status='FINISHED', p1_cpu_seconds=r1['cpu_seconds'], p2_cpu_seconds=r2['cpu_seconds'],
                                 total_cpu_seconds=total, witness_stop=bool(r1['alpha3_pairs'])))
    print('PROBES FINISHED', total, flush=True)


if __name__ == '__main__':
    main()
