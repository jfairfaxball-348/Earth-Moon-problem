"""Small SAT provenance/domain validator controls; no workers or live runtime I/O."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s035_sat_validation import CandidateValidationError, validate_candidate, sha


def write(path, text):
    with path.open('w', newline='\n') as out:
        out.write(text)


def fixture(area, assumptions=None, metadata=False):
    area.mkdir(parents=True)
    pairs = list(map(list, itertools.combinations(range(3), 2)))
    values = [1, -2, 3, -4, 5, -6, 7, 8, 9]
    base = area / 'base.cnf'
    clauses = ''.join(f'{v} 0\n' for v in values)
    base.write_text('p cnf 9 9\n' + clauses)
    seed = area / 'seed.lem'
    seed.write_text('')
    cfg = dict(n=3, pairs=pairs, variables=9, graph_variables=[7, 8, 9],
               graph_units={'7': True}, scientific=False, edge_low=3, edge_high=3,
               base=str(base), base_clauses=9, base_sha256=sha(base),
               mapping_sha256='CONTROL')
    recipe = {k: cfg[k] for k in ('n', 'pairs', 'variables', 'base', 'base_clauses', 'base_sha256', 'mapping_sha256')}
    recipe.update(sources=[dict(path=str(seed), count=0, sha256=sha(seed))],
                  assumptions=[8] if assumptions is None else assumptions)
    source = area / 'input.inst'
    write(source, f'p bipsat2 3 3 3 {9+len(recipe["assumptions"])}\n' +
                      ''.join(f'e {a} {b}\n' for a, b in pairs) + clauses +
                      ''.join(f'{v} 0\n' for v in recipe['assumptions']))
    log = area / 'native.log'
    log.write_text('s SATISFIABLE\nv ' + ' '.join(map(str, values)) + ' 0\n')
    if metadata:
        (area / 'INPUT.json').write_text(json.dumps(dict(recipe=recipe, input_sha256=sha(source))))
    return cfg, recipe, source, log, area / 'CANDIDATE.json'


def main():
    result = []
    with tempfile.TemporaryDirectory(prefix='s035-sat-validation-') as temporary:
        temp = Path(temporary)
        for name in ('valid_recipe', 'valid_control', 'bad_header', 'bad_pair_order', 'bad_clause_count',
                     'incomplete_assignment', 'contradictory_assignment', 'violated_assumption',
                     'violated_graph_unit', 'bad_recipe_hash', 'edge_domain', 'nonplanar_layer', 'missing_input'):
            cfg, recipe, source, log, target = fixture(temp / name, metadata=name == 'valid_recipe')
            supplied_recipe = recipe if name in ('bad_recipe_hash', 'violated_assumption') else None
            if name == 'bad_header':
                write(source, source.read_text().replace('p bipsat2 3 3 3', 'p bipsat2 4 3 3'))
            elif name == 'bad_pair_order':
                write(source, source.read_text().replace('e 0 1', 'e 1 2'))
            elif name == 'bad_clause_count':
                write(source, source.read_text().replace('3 3 3 10', '3 3 3 11'))
            elif name == 'incomplete_assignment':
                log.write_text('s SATISFIABLE\nv 1 -2 3 -4 5 -6 7 8 0\n')
            elif name == 'contradictory_assignment':
                log.write_text(log.read_text() + 'v -1 0\n')
            elif name == 'violated_assumption':
                recipe['assumptions'] = [-8]
                lines = source.read_text().splitlines()
                lines[-1] = '-8 0'
                write(source, '\n'.join(lines) + '\n')
            elif name == 'violated_graph_unit':
                cfg['graph_units']['7'] = False
            elif name == 'bad_recipe_hash':
                recipe['sources'][0]['sha256'] = '0' * 64
            elif name == 'edge_domain':
                cfg['edge_high'] = 2
            elif name == 'missing_input':
                source.unlink()
            elif name == 'nonplanar_layer':
                # Complete K5 in one layer, with consistent graph and CNF units.
                pairs = list(map(list, itertools.combinations(range(5), 2)))
                cfg.update(n=5, pairs=pairs, variables=30, graph_variables=list(range(21, 31)),
                           graph_units={}, edge_low=10, edge_high=10)
                values = [v if v % 2 else -v for v in range(1, 21)] + list(range(21, 31))
                write(source, 'p bipsat2 5 10 10 30\n' + ''.join(f'e {a} {b}\n' for a, b in pairs) +
                                  ''.join(f'{v} 0\n' for v in values))
                log.write_text('s SATISFIABLE\nv ' + ' '.join(map(str, values)) + ' 0\n')
            expected_pass = name.startswith('valid_')
            try:
                candidate = validate_candidate(cfg, source, log, target, recipe=supplied_recipe)
                assert expected_pass, name + ' unexpectedly passed'
                assert candidate['mathematical_headline_promoted'] is False
                assert Path(candidate['full_assignment']).exists()
                status = 'PASS_ACCEPTED'
            except CandidateValidationError:
                assert not expected_pass, name + ' unexpectedly rejected'
                assert not target.exists(), name + ' left a candidate after failed validation'
                diagnostic = json.loads(next(source.parent.glob('*.validation.json')).read_text())
                assert diagnostic['status'] == 'SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED'
                assert diagnostic['ordinary_UNKNOWN_forbidden'] is True
                assert next(source.parent.glob('*.assignment.json')).exists()
                status = 'PASS_REJECTED_WITH_SAT_ALERT_EVIDENCE'
            result.append(dict(control=name, status=status))
    out = ROOT / 'validation/S035/resume/audit/VALIDATOR_CONTROLS.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(status='PASS', controls=result, native_workers_launched=0,
                                  source_sha256=sha(ROOT / 'tools/s035_sat_validation.py')), indent=1) + '\n')
    print(json.dumps(dict(status='PASS', controls=len(result), report=str(out))))


if __name__ == '__main__':
    main()
