"""One registered radius-four diagnostic; no continuation or autonomous search."""
from collections import Counter
import gzip
import itertools as it
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s038_patch import candidates, explicit, fillings, load_start, move_record, universe
from s038_coupled import coupled_choices, joint_move
from s037_check_pair import check


if __name__ == '__main__':
    assert len(fillings(tuple(range(8)), False)) == 132
    assert len(fillings(tuple(range(8)), True)) == 330
    start = time.process_time()
    summaries = []
    for density in (156, 155):
        planes, initial, source = load_start(density)
        cover, full = universe(28)
        rows, seen = [], {}
        best = None
        for score, k, patch, ds, fs in candidates(planes, cover, full, sizes=(4,)):
            assert time.process_time()-start < 120
            key = k, tuple(sorted(patch['removed']-ds)), tuple(sorted(ds-patch['removed']))
            seen[key] = score
            if best is None or score < best['score']:
                trial = list(planes); trial[k] = planes[k].replace(patch, fs)
                best = dict(score=score, move=move_record(k, patch, ds, fs, score), pair=explicit(trial, score))
        rows = [dict(layer=k, removed=removed, added=added, score=score) for (k, removed, added), score in sorted(seen.items())]
        one = dict(neighbors=len(seen), minimum_score=best['score'], best=best,
                   strict_improvements=sum(s < initial['independent_four_sets'] for s in seen.values()),
                   independent_best_check=check(best['pair'], density))
        out = ROOT/f'validation/S038/radius4/{density}-one.json.gz'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(gzip.compress(json.dumps(rows, separators=(',', ':')).encode(), mtime=0))
        rows = []
        best = None
        for split, key0, key1, score, m0, m1 in coupled_choices(planes, ((2, 2),), cover, full):
            assert time.process_time()-start < 120
            rows.append(dict(moves=[key0, key1], score=score))
            if best is None or score < best['score']:
                trial = [planes[k].replace(m['patch'], m['filling']) for k, m in enumerate((m0, m1))]
                best = dict(score=score, move=joint_move(split, score, m0, m1), pair=explicit(trial, score))
        two = dict(neighbors=len(rows), minimum_score=best['score'], best=best,
                   strict_improvements=sum(r['score'] < initial['independent_four_sets'] for r in rows),
                   independent_best_check=check(best['pair'], density))
        (out.parent/f'{density}-two.json.gz').write_bytes(gzip.compress(json.dumps(rows, separators=(',', ':')).encode(), mtime=0))
        summary = dict(density=density, source=source, one_layer_r4=one, joint_2_2=two)
        (out.parent/f'{density}.json').write_text(json.dumps(summary, indent=2)+'\n', newline='\n')
        summaries.append(dict(density=density, one_neighbors=one['neighbors'], one_minimum=one['minimum_score'],
                              joint_neighbors=two['neighbors'], joint_minimum=two['minimum_score']))
        print(summaries[-1], flush=True)
    (ROOT/'validation/S038/radius4/SUMMARY.json').write_text(json.dumps(dict(
        cpu_seconds=time.process_time()-start, rows=summaries), indent=2)+'\n', newline='\n')
