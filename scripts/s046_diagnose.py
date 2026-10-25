"""S046 E1: census of all saved S045 candidates plus the registered stratified sample."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import s046_analyse as A
from s045_verify import check_pair, check_colouring as check_s045_colouring
from s045_search import colouring as s045_oracle

OUT = ROOT / 'validation/S046/diagnostics'
WORK = ROOT / 'artifacts/tmp/S046/diagnostics'
N, PAIRS = 50, 1225
IU, JU = np.triu_indices(N, 1)


def census_batch(rows, stats, seen_union, seen_layers, dup):
    arr = (np.frombuffer(''.join(rows).encode('ascii'), dtype=np.uint8).reshape(len(rows), 2 * PAIRS) - 48).astype(bool)
    l1, l2 = arr[:, 0::2], arr[:, 1::2]
    assert not (l1 & l2).any(), 'layer overlap in archived bits'
    union = l1 | l2
    adj = np.zeros((len(rows), N, N), dtype=np.float32)
    adj[:, IU, JU] = union
    adj[:, JU, IU] = union
    deg = adj.sum(2).astype(np.int32)
    alive = np.ones((len(rows), N), dtype=bool)
    while True:
        d = np.matmul(adj, alive.astype(np.float32)[:, :, None])[:, :, 0]
        nxt = alive & (d >= 8.5)
        if (nxt == alive).all():
            break
        alive = nxt
    core = alive.sum(1)
    stats['m'].extend(union.sum(1).tolist())
    stats['m1'].extend(l1.sum(1).tolist())
    stats['m2'].extend(l2.sum(1).tolist())
    stats['min_degree'].extend(deg.min(1).tolist())
    stats['max_degree'].extend(deg.max(1).tolist())
    stats['isolated'].extend((deg == 0).sum(1).tolist())
    stats['core9'].extend(core.tolist())
    for u, full in zip(np.packbits(union, axis=1), np.packbits(arr, axis=1)):
        ku, kl = u.tobytes(), full.tobytes()
        if ku in seen_union:
            dup['union'] += 1
            if kl in seen_union[ku]:
                dup['layers'] += 1
            seen_union[ku].add(kl)
        else:
            seen_union[ku] = {kl}


def summary(xs):
    xs = np.asarray(xs)
    return dict(min=int(xs.min()), max=int(xs.max()), mean=round(float(xs.mean()), 3),
                quartiles=[float(q) for q in np.percentile(xs, [25, 50, 75])])


def main():
    reg = json.loads((ROOT / 'validation/S046/REGISTRATION.json').read_text())
    assert time.time() < reg['experimental_deadline_epoch']
    assert A.pinned_ok()
    index = json.loads((ROOT / reg['e1']['archive_index']).read_text())
    assert A.sha(ROOT / reg['e1']['archive_index']) == reg['e1']['archive_index_sha256']
    # Verification cost: archive bytes against the frozen index.
    t0 = time.monotonic()
    for j in index['journals']:
        assert A.sha(ROOT / j['archive']) == j['archive_sha256'], j['archive']
    verify_seconds = time.monotonic() - t0
    wanted = {}
    for name, idx in reg['e1']['sample_indices'].items():
        for i in idx:
            wanted[i] = name
    ledger = A.Ledger('E1')
    stats = {k: [] for k in ('m', 'm1', 'm2', 'min_degree', 'max_degree', 'isolated', 'core9')}
    seen_union, seen_layers, dup = {}, None, dict(union=0, layers=0)
    per_file, sample, g = [], {}, 0
    for j in index['journals']:
        count, batch = 0, []
        with gzip.open(ROOT / j['archive'], 'rt', encoding='utf-8') as f:
            for line in f:
                assert line.endswith('\n') and line.startswith('{"n":50,"k":9,')
                p = line.rfind('"bits":"') + 8
                bits = line[p:p + 2 * PAIRS]
                assert line[p + 2 * PAIRS] == '"'
                batch.append(bits)
                if g in wanted:
                    sample[g] = (line, j['archive'], count)
                g += 1
                count += 1
                if len(batch) == 4096:
                    census_batch(batch, stats, seen_union, seen_layers, dup)
                    batch = []
        if batch:
            census_batch(batch, stats, seen_union, seen_layers, dup)
        per_file.append(dict(archive=j['archive'], records=count))
    assert g == reg['e1']['expected_records'], g
    census_cpu, census_wall = ledger.cpu(), ledger.wall()
    total = g
    core9 = np.asarray(stats['core9'])
    census = dict(records=total, per_file=per_file,
                  empty_core9=int((core9 == 0).sum()), empty_core9_fraction=round(float((core9 == 0).mean()), 6),
                  core9_order=summary(core9), labelled_duplicate_unions=dup['union'],
                  labelled_duplicate_layer_assignments=dup['layers'],
                  **{k: summary(v) for k, v in stats.items() if k != 'core9'})
    # Stratified sample: full parse, independent checks, structure and colouring.
    rows, drat_seconds, oracle, graphs = [], 0.0, [], []
    for gi in sorted(sample):
        line, archive, local = sample[gi]
        r = json.loads(line)
        layers = [[tuple(e) for e in ls] for ls in r['layers']]
        check_pair(N, r['layers'], r['rotations'])
        check_s045_colouring(N, r['layers'], r['colours'], 9)
        bits = r['bits']
        pairs = [(a, b) for a in range(N) for b in range(a + 1, N)]
        assert [list(e) for i, e in enumerate(pairs) if bits[2 * i] == '1'] == r['layers'][0]
        edges = sorted(set(layers[0]) | set(layers[1]))
        graphs.append((N, edges))
        s = A.structure(N, edges)
        # numpy census must agree with the independent NetworkX core numbers.
        assert s['core9_order'] == stats['core9'][gi], gi
        t = time.monotonic()
        ok, _ = s045_oracle(N, r['layers'], 9, 60)
        oracle.append(time.monotonic() - t)
        assert ok is True
        if s['best_colours'] <= 8:
            sat8, how = 'SAT', 'explicit_greedy'
        else:
            res, cols = A.sat_colour(N, edges, 8, reg['e1']['caps']['sat8_seconds'], s['clique'])
            sat8, how = res, 'pysat_cadical195'
        cert = None
        if sat8 == 'UNSAT':
            cert, sec = A.drat_certify(N, edges, 8, s['clique'], WORK / f'drat-{gi}',
                                       reg['e1']['caps']['drat_solve_seconds'], reg['e1']['caps']['drat_check_seconds'])
            drat_seconds += sec
        s.pop('best_colouring')
        rows.append(dict(index=gi, stratum=wanted[gi], archive=archive, local_index=local,
                         layer_edges=[len(layers[0]), len(layers[1])], sat8=sat8, sat8_method=how,
                         non8_certificate=cert, **s))
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'sample_rows.json').write_text(json.dumps(rows), encoding='utf-8')
    (WORK / 'census.json').write_text(json.dumps(census), encoding='utf-8')
    classes = A.iso_classes(graphs)
    row = ledger.close(census_cpu=round(census_cpu, 3), census_wall=round(census_wall, 3),
                       note='second E1 execution; the first computed the same quantities but crashed in report formatting before any output was printed or inspected')
    in_multi = sum(len(c) for c in classes if len(c) > 1)
    by = lambda key: {name: dict(count=sum(1 for r in rows if r['stratum'] == name),
                                 **{str(k): sum(1 for r in rows if r['stratum'] == name and key(r) == k)
                                    for k in sorted({key(x) for x in rows})})
                      for name in ('early', 'middle', 'late')}
    certified = sum(1 for r in rows if r['non8_certificate'] == 'VERIFIED_NON_K_COLOURABLE')
    nonempty = sum(1 for r in rows if r['core9_order'] > 0)
    verdicts = dict(
        mainly_easy=census['empty_core9_fraction'] >= 0.5,
        mainly_redundant=in_multi / len(rows) >= 0.5,
        plausible_cores=sum(1 for r in rows if r['core9_order'] > 0 and
                            r['non8_certificate'] == 'VERIFIED_NON_K_COLOURABLE') / len(rows) >= 0.5)
    result = dict(status='COMPLETE', scope='saved S045 records only; descriptive, not coverage or witness probability',
                  census=census, sample_size=len(rows), sample_nonempty_core9=nonempty,
                  sample_certified_non8=certified, sample_sat8=sum(r['sat8'] == 'SAT' for r in rows),
                  sample_sat8_unknown=sum(r['sat8'] == 'TIMEOUT' or (r['sat8'] == 'UNSAT' and r['non8_certificate'] != 'VERIFIED_NON_K_COLOURABLE') for r in rows),
                  best_colours_by_stratum=by(lambda r: r['best_colours']),
                  omega_by_stratum=by(lambda r: r['omega']),
                  degeneracy_by_stratum=by(lambda r: r['degeneracy']),
                  isomorphism=dict(classes=len(classes), largest=len(classes[0]), in_nonsingleton=in_multi,
                                   method='WL3 screen + VF2 checked mappings'),
                  oracle_seconds=summary(np.round(np.asarray(oracle) * 1000).astype(int)) | {'unit': 'ms'},
                  verdicts=verdicts, budget=row, verification=dict(archive_hash_seconds=round(verify_seconds, 3),
                                                                     drat_seconds=round(drat_seconds, 3)),
                  sample=rows)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'E1.json').write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('sample',)}, indent=1)[:6000])


if __name__ == '__main__':
    main()
