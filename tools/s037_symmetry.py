"""Independent stdlib checker of the sorted-prefix theorem, not an S11 solver."""
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def audit():
    config = json.loads((ROOT/'validation/S034/REGISTERED_CONFIG.json').read_text())
    raw_mapping = (ROOT/'validation/S032/start/INPUTS.json').read_bytes()
    mapping = json.loads(raw_mapping)
    assert sha(raw_mapping) == config['mapping_sha256']
    pairs = list(it.combinations(range(28), 2))
    assert mapping['pairs'] == config['pairs'] == [list(e) for e in pairs]
    m = len(pairs)
    rename = {int(k): v for k, v in mapping['original_to_native'].items()}
    assert sorted(rename) == sorted(rename.values()) == list(range(1, 17977))
    assert all(rename[i+1] == 2*m+i+1 for i in range(m))
    original = gzip.decompress((ROOT/'validation/S031/search/final.cnf.gz').read_bytes())
    assert sha(original) == mapping['sha256']['original.cnf']
    lines = original.decode().splitlines()
    assert lines[0] == 'p cnf 17976 336030'
    clauses = [tuple(map(int, line.split()[:-1])) for line in lines[1:]]
    assert len(clauses) == 336030
    clause_set = set(clauses)
    graph = {e: i+1 for i, e in enumerate(pairs)}
    native = {e: rename[v] for e, v in graph.items()}
    native_lines = ['p cnf 17976 336030\n']
    native_units = {}
    for clause in clauses:
        xs = [rename[abs(v)]*(1 if v > 0 else -1) for v in clause]
        native_lines.append(' '.join(map(str, xs))+' 0\n')
        if len(xs) == 1 and 2*m < abs(xs[0]) <= 3*m:
            native_units[str(abs(xs[0]))] = xs[0] > 0
    native_bytes = ''.join(native_lines).encode()
    assert sha(native_bytes) == config['base_sha256'] == mapping['sha256']['base.cnf']
    assert native_units == config['graph_units']
    free = [v for v in config['graph_variables'] if str(v) not in native_units]
    assert free[:8] == [native[1, v] for v in range(3, 11)] == list(range(785, 793))
    assert config['bits'] == 8

    # Audit all sorting clauses in both blocks against the actual frozen bytes.
    sorting = []
    for block in (range(3, 14), range(14, 28)):
        for u, v in zip(block, list(block)[1:]):
            vs = [graph[1, u], graph[2, u], graph[1, v], graph[2, v]]
            local = []
            for a in range(4):
                for b in range(a):
                    bits = [a//2, a%2, b//2, b%2]
                    c = tuple(-x if bit else x for x, bit in zip(vs, bits))
                    assert c in clause_set
                    local.append(c)
                    sorting.append(c)
            for bits in it.product((0, 1), repeat=4):
                assignment = dict(zip(vs, bits))
                satisfied = all(any(assignment[abs(x)] == (x > 0) for x in c) for c in local)
                assert satisfied == (2*bits[0]+bits[1] <= 2*bits[2]+bits[3])
    assert len(sorting) == 138

    cases = []
    for cell, xs in enumerate(it.product((0, 1), repeat=8)):
        # Independent exhaustive second-coordinate enumeration (65536 total).
        good_y = [list(ys) for ys in it.product((0, 1), repeat=8)
                  if all(2*xs[i]+ys[i] <= 2*xs[i+1]+ys[i+1] for i in range(7))]
        # Independent DP extends the full 11-vertex block, quantifying all bits.
        counts = {t: 1 for t in range(4) if t//2 == xs[0]}
        for i in range(1, 11):
            counts = {t: sum(count for prev, count in counts.items() if prev <= t)
                      for t in range(4) if i >= 8 or t//2 == xs[i]}
        count = sum(counts.values())
        monotone = all(a <= b for a, b in zip(xs, xs[1:]))
        assert bool(good_y) == (count > 0) == monotone
        assumptions = [v if b else -v for v, b in zip(free[:8], xs)]
        cases.append(dict(id=cell, prefix=''.join(map(str, xs)), permitted=monotone,
                          first8_y_extensions=len(good_y), full11_extensions=count,
                          assumptions=assumptions))
    allowed = [c['id'] for c in cases if c['permitted']]
    assert allowed == [0, 1, 3, 7, 15, 31, 63, 127, 255]
    old = json.loads((ROOT/'validation/S035/closeout/AUDIT.json').read_text())
    forbidden = sorted(c['id'] for c in cases if not c['permitted'])
    receipts = sorted(c['cell'] for c in old['certificates'])
    assert forbidden == receipts and len(set(receipts)) == 247
    final = json.loads((ROOT/'validation/S036/closeout/REGIONS_FINAL.json').read_text())
    assert allowed == sorted(r['region'] for r in final['regions'])
    # Check historical bit order/assumptions on all cells independently.
    historical = json.loads(gzip.decompress((ROOT/'validation/S035/REGIONS.json.gz').read_bytes()))
    assert all(c['assumptions'] == cases[c['id']]['assumptions'] for c in historical['cells'])
    return dict(status='PASS', graph_variables=378, fixed_graph_variables=28,
                split_variables=free[:8], split_edges=[[1, v] for v in range(3, 11)],
                original_formula_sha256=sha(original), native_formula_sha256=sha(native_bytes),
                sorting_clauses_in_frozen_formula=138, pair_truth_table_cases=16,
                permitted=allowed, forbidden=forbidden, historical_certificates_match=True,
                fresh_historical_DRAT_replay=False, full_S11_satisfiability='UNKNOWN', cases=cases)


if __name__ == '__main__':
    result = audit()
    out = ROOT/'validation/S037/SYMMETRY.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('PASS: all 247 forbidden prefixes follow from sorting alone; allowed:', result['permitted'])
