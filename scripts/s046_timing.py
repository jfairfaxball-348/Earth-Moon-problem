"""S046: S045 slice timing decomposition from archived receipts only (no rerun)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'validation/S045/final/stop_snapshot/SLICES.jsonl'


def main():
    rows = [json.loads(x) for x in SRC.read_text().splitlines()]
    out = []
    for r in rows:
        total = r['elapsed_seconds']
        load = r.get('native_startup_seconds')
        solve = r.get('solve_elapsed_seconds')
        out.append(dict(started_utc=r['started_utc'], state=r['state'], reason=r['reason'], total=total,
                        loading=load, solving_including_oracle=solve,
                        preparation_plus_post_audit=None if load is None or solve is None else total - load - solve,
                        new_records=r.get('new_candidates'), loaded_geometric_rules=r.get('loaded_geometric_rules'),
                        peak_private_gib=(r.get('peak_private_bytes') or 0) / 2**30))
    timed = [o for o in out if o['preparation_plus_post_audit'] is not None and o['state'] == 'SLICE_COMPLETE']
    def agg(xs):
        t = sum(o['total'] for o in xs)
        return dict(slices=len(xs), total=t, loading=sum(o['loading'] for o in xs),
                    solving=sum(o['solving_including_oracle'] for o in xs),
                    preparation_plus_audit=sum(o['preparation_plus_post_audit'] for o in xs),
                    new_records=sum(o['new_records'] for o in xs),
                    overhead_fraction=1 - sum(o['solving_including_oracle'] for o in xs) / t)
    recycle = [o for o in timed if o['reason'] == 'MEMORY_RECYCLE']
    data = dict(source=str(SRC.relative_to(ROOT)), slices=len(out), rows=out,
                watchdog_phase=agg([o for o in timed if o['reason'] == 'NATIVE_TIMEOUT']),
                recycle_phase=agg(recycle), last_eight_recycle=agg(recycle[-8:]),
                limits='receipts do not separate preparation from post-slice audit, nor oracle from native solving; '
                       'oracle cost re-measured on the E1 sample (mean 3 ms per record)')
    (ROOT / 'validation/S046/diagnostics/S045_TIMING.json').write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8', newline='\n')
    for k in ('watchdog_phase', 'recycle_phase', 'last_eight_recycle'):
        print(k, {a: round(b, 3) if isinstance(b, float) else b for a, b in data[k].items()})


if __name__ == '__main__':
    main()
