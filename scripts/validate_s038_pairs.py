"""Independent explicit pair checking and rotation certificate authoring."""
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_check_pair import check


if __name__ == '__main__':
    start = time.process_time()
    rows = []
    paths = sorted((ROOT/'validation/S038/arms').glob('*-single.json'))
    paths += sorted((ROOT/'validation/S038/arms').glob('*-patch.json'))
    paths += sorted((ROOT/'validation/S038/coupled').glob('arm-*.json'))
    for path in paths:
        source = json.loads(path.read_text())
        result = check(source['best'], source['density'])
        result.update(path=str(path.relative_to(ROOT)).replace('\\', '/'), pointer=['best'],
                      sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        rows.append(result)
    for density in (156, 155):
        specs = [(f'validation/S038/coupled/neighborhood-{density}.json', ['best', 'pair'])]
        specs += [(f'validation/S038/radius4/{density}.json', [key, 'best', 'pair']) for key in ('one_layer_r4', 'joint_2_2')]
        for name, pointer in specs:
            path = ROOT/name
            source = json.loads(path.read_text())
            data = source
            for key in pointer:
                data = data[key]
            result = check(data, density)
            result.update(path=name, pointer=pointer, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            rows.append(result)
    out = dict(status='PASS', records=len(rows), rows=rows,
               cpu_seconds=time.process_time()-start, witness_found=any(r['alpha_at_most_3'] for r in rows))
    (ROOT/'validation/S038/PAIR_CHECKS.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')
    print([(r['path'], r['independent_four_sets'], r['proper_coloring_upper_bound']) for r in rows])
