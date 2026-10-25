"""S046 E2 matched pilots and E3 candidate analysis / registered targeting criterion."""
import argparse
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import s046_analyse as A

REG = json.loads((ROOT / 'validation/S046/REGISTRATION.json').read_text())
BASE = ROOT / 'artifacts/tmp/S046/pilots'
OUT = ROOT / 'validation/S046/pilots'


def arms():
    return [(n, arm) for n in REG['e2']['orders'] for arm in REG['e2']['arms']]


def e2():
    from s046_driver import run_slice
    cap = REG['budget']['blocks']['E2']
    rows, used_cpu, used_wall = [], 0.0, 0.0
    for idx, (n, arm) in enumerate(arms()):
        if time.time() >= REG['experimental_deadline_epoch']:
            rows.append(dict(index=idx, n=n, arm=arm, status='NOT_RUN_DEADLINE'))
            continue
        # Do not start an arm that could not finish inside the block allocation.
        if used_cpu + 75 > cap['cpu'] or used_wall + 75 > cap['wall']:
            rows.append(dict(index=idx, n=n, arm=arm, status='NOT_RUN_BUDGET'))
            continue
        out = BASE / f'n{n}-{arm}'
        assert not out.exists(), 'fresh runtime directory required'
        ledger = A.Ledger(f'E2:n{n}-{arm}')
        r = run_slice(out, n, REG['e2']['k'], REG['e2']['solve_seconds'], arm,
                      positive=REG['e2']['positive_phases'], absolute_deadline=REG['experimental_deadline_epoch'],
                      startup_ceiling=REG['e2']['startup_ceiling'])
        ledger.child_cpu = r.get('native_cpu_seconds') or 0.0
        b = ledger.close(reason=r['reason'], candidates=r['candidates'])
        used_cpu += b['cpu_seconds']
        used_wall += b['wall_seconds']
        row = dict(index=idx, n=n, arm=arm, status=r['state'], reason=r['reason'], candidates=r['candidates'],
                   solve_seconds=r['solve_seconds'], native_startup_seconds=r.get('native_startup_seconds'),
                   instance=r.get('instance'), native_cpu_seconds=r['native_cpu_seconds'],
                   controller_cpu_seconds=r['controller_cpu_seconds'], oracle_seconds=r['oracle_seconds'],
                   peak_private_bytes=r['peak_private_bytes'], geometric_cuts=r['verified_geometric_cuts_new'],
                   audit_seconds=r['audit_seconds'], native_returncode=r['native_returncode'], error=r['error'],
                   native_progress=r.get('native_progress'), budget=b)
        rows.append(row)
        print(json.dumps({k: row[k] for k in ('n', 'arm', 'status', 'reason', 'candidates', 'solve_seconds',
                                              'native_cpu_seconds', 'peak_private_bytes')}), flush=True)
        if r['reason'] in ('NONCOLOUR_ALERT_UNVERIFIED', 'COLOUR_TIMEOUT'):
            rows.append(dict(status='PILOTS_HALTED', cause=r['reason'], at=f'n{n}-{arm}'))
            break
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'E2.json').write_text(json.dumps(dict(status='COMPLETE', arms=rows, used_cpu=used_cpu, used_wall=used_wall),
                                            indent=1) + '\n', encoding='utf-8', newline='\n')


def e2_resume():
    """Run arms skipped only because audit (verification) time was charged to E2.

    The registration treats Kuratowski audits as verification cost; the first
    E2 invocation's per-arm guard counted them. Experimental use is recomputed
    as process-tree CPU/wall minus each arm's audit seconds, and any skipped arm
    is run in registered order if the corrected E2 allocation still covers it.
    """
    from s046_driver import run_slice
    cap = REG['budget']['blocks']['E2']
    data = json.loads((OUT / 'E2.json').read_text())
    done = [r for r in data['arms'] if r.get('budget')]
    used_cpu = sum(r['budget']['cpu_seconds'] - r['audit_seconds'] for r in done)
    used_wall = sum(r['budget']['wall_seconds'] - r['audit_seconds'] for r in done)
    for row in data['arms']:
        if row.get('status') != 'NOT_RUN_BUDGET':
            continue
        n, arm, idx = row['n'], row['arm'], row['index']
        if used_cpu + 75 > cap['cpu'] or used_wall + 75 > cap['wall'] or time.time() >= REG['experimental_deadline_epoch']:
            row['status'] = 'NOT_RUN_BUDGET_AFTER_CORRECTION'
            continue
        out = BASE / f'n{n}-{arm}'
        assert not out.exists(), 'fresh runtime directory required'
        ledger = A.Ledger(f'E2:n{n}-{arm}')
        r = run_slice(out, n, REG['e2']['k'], REG['e2']['solve_seconds'], arm,
                      positive=REG['e2']['positive_phases'], absolute_deadline=REG['experimental_deadline_epoch'],
                      startup_ceiling=REG['e2']['startup_ceiling'])
        ledger.child_cpu = r.get('native_cpu_seconds') or 0.0
        b = ledger.close(reason=r['reason'], candidates=r['candidates'], resumed_after_accounting_correction=True)
        used_cpu += b['cpu_seconds'] - r['audit_seconds']
        used_wall += b['wall_seconds'] - r['audit_seconds']
        row.clear()
        row.update(index=idx, n=n, arm=arm, status=r['state'], reason=r['reason'], candidates=r['candidates'],
                   solve_seconds=r['solve_seconds'], native_startup_seconds=r.get('native_startup_seconds'),
                   instance=r.get('instance'), native_cpu_seconds=r['native_cpu_seconds'],
                   controller_cpu_seconds=r['controller_cpu_seconds'], oracle_seconds=r['oracle_seconds'],
                   peak_private_bytes=r['peak_private_bytes'], geometric_cuts=r['verified_geometric_cuts_new'],
                   audit_seconds=r['audit_seconds'], native_returncode=r['native_returncode'], error=r['error'],
                   native_progress=r.get('native_progress'), budget=b, resumed_after_accounting_correction=True)
        print(json.dumps({k: row[k] for k in ('n', 'arm', 'status', 'reason', 'candidates', 'solve_seconds')}), flush=True)
        if r['reason'] in ('NONCOLOUR_ALERT_UNVERIFIED', 'COLOUR_TIMEOUT'):
            break
    data['experimental_cpu_excluding_audit'] = used_cpu
    data['experimental_wall_excluding_audit'] = used_wall
    (OUT / 'E2.json').write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8', newline='\n')


def load(path):
    with Path(path).open(encoding='utf-8') as f:
        for line in f:
            assert line.endswith('\n')
            yield json.loads(line)


def e3():
    e2rows = {(r['n'], r['arm']): r for r in json.loads((OUT / 'E2.json').read_text())['arms'] if 'arm' in r}
    cfg = REG['e3']
    ledger = A.Ledger('E3')
    results, drat_total = [], 0.0
    for idx, (n, arm) in enumerate(arms()):
        row = e2rows.get((n, arm))
        if not row or 'candidates' not in row:
            results.append(dict(index=idx, n=n, arm=arm, analysed=0, status='NO_PILOT'))
            continue
        path = BASE / f'n{n}-{arm}' / 'CANDIDATES.jsonl'
        recs = list(load(path)) if path.exists() else []
        assert len(recs) == row['candidates']
        unions = [r['bits'] for r in recs]
        keys = {''.join('1' if b[2 * i] == '1' or b[2 * i + 1] == '1' else '0' for i in range(len(b) // 2)) for b in unions}
        chosen = list(range(len(recs))) if len(recs) <= cfg['per_arm'] else \
            sorted(random.Random(cfg['seed_base'] + idx).sample(range(len(recs)), cfg['per_arm']))
        start, done, graphs, drat_arm = time.monotonic(), [], [], 0.0
        for c in chosen:
            if time.monotonic() - start - drat_arm > cfg['per_arm_wall_cap']:
                break
            r = recs[c]
            edges = sorted({tuple(e) for ls in r['layers'] for e in ls})
            A.check_colouring(edges, r['colours'], 9)
            s = A.structure(n, edges, clique_seconds=0.5)
            if s['best_colours'] <= 8:
                sat8, how = 'SAT', 'explicit_greedy'
            else:
                sat8, _ = A.sat_colour(n, edges, 8, cfg['sat8_seconds'], s['clique'])
                how = 'pysat_cadical195'
            cert = None
            if sat8 == 'UNSAT':
                t = time.monotonic()
                cert, _ = A.drat_certify(n, edges, 8, s['clique'], ROOT / f'artifacts/tmp/S046/e3drat/n{n}-{arm}-{c}',
                                         cfg['drat_solve_seconds'], cfg['drat_check_seconds'])
                drat_arm += time.monotonic() - t
            s.pop('best_colouring')
            done.append(dict(candidate=c, sat8=sat8, sat8_method=how, non8_certificate=cert, **s))
            graphs.append((n, edges))
        drat_total += drat_arm
        classes = A.iso_classes(graphs) if graphs else []
        cert9 = sum(d['non8_certificate'] == 'VERIFIED_NON_K_COLOURABLE' for d in done)
        lo, hi = A.wilson(cert9, len(done))
        results.append(dict(
            index=idx, n=n, arm=arm, validated=len(recs), labelled_distinct_unions=len(keys),
            solve_seconds=row['solve_seconds'], rate=len(recs) / row['solve_seconds'] if row['solve_seconds'] else 0,
            analysed=len(done), not_analysed=len(chosen) - len(done), certified_non8=cert9,
            p9=cert9 / len(done) if done else None, wilson95=[lo, hi],
            sat8=sum(d['sat8'] == 'SAT' for d in done),
            unknown8=sum(d['sat8'] == 'TIMEOUT' or (d['sat8'] == 'UNSAT' and d['non8_certificate'] != 'VERIFIED_NON_K_COLOURABLE') for d in done),
            empty_core9=sum(d['core9_order'] == 0 for d in done),
            min_degree=[min((d['min_degree'] for d in done), default=None), max((d['min_degree'] for d in done), default=None)],
            m=[min((d['m'] for d in done), default=None), max((d['m'] for d in done), default=None)],
            with_cut_vertex=sum(d['cut_vertices'] > 0 or d['nontrivial_components'] > 1 for d in done),
            omega_hist={str(w): sum(d['omega'] == w for d in done) for w in sorted({d['omega'] for d in done})},
            best_colours_hist={str(w): sum(d['best_colours'] == w for d in done) for w in sorted({d['best_colours'] for d in done})},
            iso_classes=len(classes), in_nonsingleton=sum(len(x) for x in classes if len(x) > 1),
            drat_seconds=drat_arm, detail=done))
    by = {(r['n'], r['arm']): r for r in results}
    for r in results:
        if r['arm'] == 'B' or r.get('analysed', 0) == 0:
            r['T'] = False
            continue
        b = by.get((r['n'], 'B'), {})
        bhi = b.get('wilson95', [0, 1])[1] if b.get('analysed') else 1.0
        r['T1'] = r['validated'] >= 20 and r['analysed'] >= 20
        r['T2'] = (r['p9'] or 0) >= 0.25 and r['wilson95'][0] > bhi
        r['T'] = r['T1'] and r['T2']
        r['score'] = r['rate'] * (r['p9'] or 0)
    passing = sorted([r for r in results if r.get('T')], key=lambda r: (-r['score'], r['n']))
    row = ledger.close(note='DRAT subprocess time is verification, excluded from this process meter',
                       drat_seconds=round(drat_total, 3))
    data = dict(status='COMPLETE', criterion=REG['e3']['targeting_criterion'], arms=results,
                passing=[(r['n'], r['arm']) for r in passing], selected=(passing[0]['n'], passing[0]['arm']) if passing else None,
                targeting_passed=bool(passing), budget=row)
    (OUT / 'E3.json').write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8', newline='\n')
    for r in results:
        print(json.dumps({k: r.get(k) for k in ('n', 'arm', 'validated', 'analysed', 'certified_non8', 'p9', 'wilson95',
                                                'sat8', 'unknown8', 'empty_core9', 'min_degree', 'best_colours_hist',
                                                'omega_hist', 'iso_classes', 'T')}))
    print('passing', data['passing'], 'selected', data['selected'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stage', choices=['e2', 'e2-resume', 'e3'])
    a = ap.parse_args()
    assert A.pinned_ok()
    {'e2': e2, 'e2-resume': e2_resume, 'e3': e3}[a.stage]()


if __name__ == '__main__':
    main()
