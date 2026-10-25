"""S046 amendment A1: k=8 positive-control calibration of the colouring-feedback generator."""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import s046_analyse as A
from s046_driver import run_slice
from s045_verify import check_pair

REG = json.loads((ROOT / 'validation/S046/REGISTRATION.json').read_text())
AM = json.loads((ROOT / 'validation/S046/AMENDMENT_A1.json').read_text())
BASE = ROOT / 'artifacts/tmp/S046/calibration'
OUT = ROOT / 'validation/S046/calibration'


def main():
    assert A.pinned_ok() and time.time() < REG['experimental_deadline_epoch']
    k, rows, used_cpu, used_wall = AM['k'], [], 0.0, 0.0
    OUT.mkdir(parents=True, exist_ok=True)
    for arm, n in AM['runs']:
        if used_cpu + 50 > AM['budget']['cpu'] or used_wall + 50 > AM['budget']['wall']:
            rows.append(dict(arm=arm, n=n, status='NOT_RUN_BUDGET'))
            continue
        out = BASE / f'k8-n{n}-{arm}'
        assert not out.exists()
        ledger = A.Ledger(f'A1:k8-n{n}-{arm}')
        r = run_slice(out, n, k, AM['solve_seconds'], arm, absolute_deadline=REG['experimental_deadline_epoch'],
                      startup_ceiling=60)
        ledger.child_cpu = r.get('native_cpu_seconds') or 0.0
        b = ledger.close(reason=r['reason'], candidates=r['candidates'], audit_seconds=r['audit_seconds'])
        used_cpu += b['cpu_seconds'] - (r['audit_seconds'] or 0)
        used_wall += b['wall_seconds'] - (r['audit_seconds'] or 0)
        row = dict(arm=arm, n=n, reason=r['reason'], candidates_before_hit=r['candidates'],
                   solve_seconds=r['solve_seconds'], hit=r['reason'] in ('NONCOLOUR_ALERT_UNVERIFIED', 'COLOUR_TIMEOUT'),
                   peak_private_bytes=r['peak_private_bytes'], budget=b)
        if row['hit']:
            alert = json.loads((out / 'ALERT.json').read_text())
            check_pair(n, alert['layers'], alert['rotations'])
            edges = sorted({tuple(e) for ls in alert['layers'] for e in ls})
            s = A.structure(n, edges, clique_seconds=5)
            verdict, sec = A.drat_certify(n, edges, k, s['clique'], out / 'drat', 120, 300)
            res9, cols9 = A.sat_colour(n, edges, 9, 30, s['clique'])
            row.update(found=dict(layers=alert['layers'], m=s['m'], min_degree=s['min_degree'],
                                  omega=s['omega'], clique=s['clique'], core9_order=s['core9_order'],
                                  non8=verdict, drat_seconds=sec, nine_colouring=cols9 if res9 == 'SAT' else None,
                                  chi=9 if verdict == 'VERIFIED_NON_K_COLOURABLE' and res9 == 'SAT' else None))
        rows.append(row)
        print(json.dumps({x: row.get(x) for x in ('arm', 'n', 'reason', 'candidates_before_hit', 'solve_seconds')} |
                         ({'chi': row['found']['chi'], 'omega': row['found']['omega'], 'm': row['found']['m']} if row['hit'] else {})),
              flush=True)
    data = dict(status='COMPLETE', amendment='A1', k=k, runs=rows, used_cpu=used_cpu, used_wall=used_wall,
                scope='calibration on known-feasible k=8 analogue; not Earth-Moon evidence; no novelty claim')
    (OUT / 'A1.json').write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
