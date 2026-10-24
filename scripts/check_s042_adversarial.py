"""Falsification controls for S042 records; stdlib, read-only."""
import copy
import json
from pathlib import Path
from check_s042_records import invariant, omega, read, small_family_leaves
from s042_types_stdlib import table

ROOT = Path(__file__).resolve().parents[1]


def main():
    rejected = []
    rows = read('validation/S042/CENSUS_TYPES.json')
    mine = table()
    as_tuple = lambda rs: sorted((r['a'], r['c'], tuple(tuple(f) for f in r['factors']), r['n'], r['slack'], tuple(r['factor_status'])) for r in rs)
    for name, mutate in (('unresolved_marked_resolved', lambda r: r['factor_status'].__setitem__(0, 'ORE_ONLY')),
                         ('slack_inflated', lambda r: r.__setitem__('slack', r['slack']+1))):
        bad = copy.deepcopy(rows)
        mutate(next(r for r in bad if not r['resolved']))
        if as_tuple(bad) != mine:
            rejected.append(name)
        else:
            raise AssertionError('accepted '+name)
    leaves = read('validation/S042/LEAF_GRAPHS.json')['leaf_graphs']
    g = {tuple(e) for e in leaves[0]['edges']}
    n = len({v for e in g for v in e})
    extra = next((a, b) for a in range(n) for b in range(a+1, n) if (a, b) not in g)
    if omega(g | {extra}) != leaves[0]['omega'] or len(g | {extra}) > 6*n-12:
        rejected.append('extra_edge_changes_record')
    else:
        raise AssertionError('extra edge undetected')
    invs = [invariant({tuple(e) for e in x['edges']}) for x in leaves]
    probe = small_family_leaves()[0]
    probe = set(probe) - {next(iter(sorted(probe)))}
    if invariant(probe) not in invs:
        rejected.append('mutated_small_family_absent')
    else:
        raise AssertionError('mutated small family matched')
    dec = read('validation/S042/DECISIONS.json')['decisions'][0]
    arch = {r['name']: r for r in read('validation/S042/ARCHIVE.json')['rows']}[dec['name']]
    if arch['drat_gz']['sha256'] != dec['certify']['drat_gz_sha256'][::-1]:
        rejected.append('reversed_drat_hash')
    print('S042 adversarial PASS:', len(rejected), 'malformed records rejected')
    return dict(status='PASS', rejected=rejected)


if __name__ == '__main__':
    import sys
    result = main()
    if '--record' in sys.argv:
        (ROOT/'validation/S042/ADVERSARIAL_CHECKS.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
