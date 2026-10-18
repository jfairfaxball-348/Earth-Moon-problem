#!/usr/bin/env python3
"""S025: settle corpus rows by explicit subgraph maps from DRAT-certified C5 obstructions.

For each of the 271 rows, tries the certified obstructions (given in order) and records
the first explicit injective vertex map under which every obstruction edge is a row
edge (tools/s025_transfer.explicit_check).  A row containing a non-biplanar subgraph is
non-biplanar.  Usage: s025_transfer_all.py CERTDIR OUT.json TAG1 TAG2 ...
(TAG like 25262 meaning C5[2,5,2,6,2]; CERTDIR/C5-TAG.certificate.json must say certified)
"""
import json
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s025_transfer import find_map, explicit_check   # noqa: E402

C5 = 'Dhc'

if __name__ == '__main__':
    certdir, outp, tags = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
    obs = []
    for t in tags:
        rec = json.loads((certdir / f'C5-{t}.certificate.json').read_text())
        assert rec['certified'] is True, t
        obs.append((t, [int(ch) for ch in t]))
    corpus = json.loads((ROOT / 'validation/S003/survivors_alpha_ge3.json').read_text())
    unknown = set(json.loads((ROOT / 'validation/S018/SUMMARY.json').read_text())['canonical_original_unknown'])
    H = nx.cycle_graph(5)
    Hadj = {i: set(H[i]) for i in H}
    rows = []
    for r, row in enumerate(corpus):
        Bg6, w = row[0], row[1]
        B = nx.from_graph6_bytes(Bg6.encode())
        rec = {'row': r, 'prior_status': 'BIPLANARITY_UNKNOWN' if r in unknown else 'NONBIPLANAR_CERTIFIED_BEFORE_S025',
               'graph6': Bg6, 'weights': w}
        for t, u in obs:
            a = find_map(Hadj, u, B, w)
            if a is not None:
                vmap = explicit_check(C5, u, Bg6, w, a)
                rec.update(obstruction=f'C5[{",".join(map(str, u))}]', tag=t,
                           vertex_map=[vmap[i] for i in range(sum(u))])
                break
        rows.append(rec)
    settled = [x for x in rows if 'tag' in x and x['prior_status'] == 'BIPLANARITY_UNKNOWN']
    out = {'rule': 'subgraph of a DRAT-certified non-biplanar C5 clique blow-up',
           'obstructions_used': tags, 'rows': rows,
           'unknown_total': len(unknown), 'unknown_settled': len(settled),
           'unknown_unsettled': sorted(r for r in unknown if not any(x['row'] == r and 'tag' in x for x in rows))}
    Path(outp).write_text(json.dumps(out))
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}))
