"""Bind SAT assignments to the exact preserved S035 input before domain review.

This adds independent format/provenance checks without changing the hash-pinned
historical engine. No worker is launched and no process is resumed here.
"""
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]


class CandidateValidationError(RuntimeError):
    """The SAT signal remains a review alert regardless of validation failure."""


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as out:
        json.dump(value, out, indent=1)
        out.write('\n')
        out.flush()
        os.fsync(out.fileno())
    os.replace(temporary, path)


def _fresh(path):
    path = Path(path)
    return path if not path.exists() else path.with_name(path.stem + '-' + uuid.uuid4().hex + path.suffix)


def _require(condition, message):
    if not condition:
        raise CandidateValidationError(message)


def _recipe_hash(config, recipe):
    """Hash the exact materialise(native=True) byte stream without writing it."""
    for key in ('n', 'pairs', 'variables', 'base', 'base_clauses', 'base_sha256', 'mapping_sha256'):
        _require(recipe[key] == config[key], 'Recipe/config mismatch: ' + key)
    _require(sha(recipe['base']) == recipe['base_sha256'], 'Base hash mismatch')
    for row in recipe['sources']:
        _require(sha(row['path']) == row['sha256'], 'Clause-source hash mismatch: ' + row['path'])
    count = recipe['base_clauses'] + sum(row['count'] for row in recipe['sources']) + len(recipe['assumptions'])
    m = len(recipe['pairs'])
    h = hashlib.sha256()
    h.update(f"p bipsat2 {recipe['n']} {m} {recipe['variables'] - 2*m} {count}\n".encode())
    for a, b in recipe['pairs']:
        h.update(f'e {a} {b}\n'.encode())
    with Path(recipe['base']).open() as source:
        next(source)
        for block in iter(lambda: source.read(1024 * 1024), ''):
            h.update(block.encode())
    for row in recipe['sources']:
        with Path(row['path']).open() as source:
            for block in iter(lambda: source.read(1024 * 1024), ''):
                h.update(block.encode())
    for literal in recipe['assumptions']:
        h.update(f'{literal} 0\n'.encode())
    return h.hexdigest(), count


def validate_candidate(config, native_input, log, target, recipe=None):
    """Validate one complete assignment, preserving diagnostics even on failure.

    `recipe` must be the immutable INPUT.json recipe used to construct this input,
    not the resident context recipe after later deltas have been appended. When
    omitted, the adjacent INPUT.json supplies it. The returned candidate remains
    pending domain review and never promotes a mathematical headline.
    """
    native_input, log, target = map(Path, (native_input, log, target))
    assignment_path = _fresh(target.with_name(target.stem + '.assignment.json'))
    diagnostic_path = _fresh(target.with_name(target.stem + '.validation.json'))
    diagnostic = dict(status='SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED', epoch=time.time(),
                      input=str(native_input), native_log=str(log), candidate=str(target),
                      assignment=str(assignment_path), ordinary_UNKNOWN_forbidden=True,
                      mathematical_headline_promoted=False, stage='PRESERVE')
    _json(diagnostic_path, diagnostic)
    try:
        text = log.read_text(errors='replace')
        raw_lines = [line for line in text.splitlines() if line.startswith('v ')]
        log_sha = sha(log)
        _json(assignment_path, dict(raw_assignment_lines=raw_lines, native_log_sha256=log_sha,
                                   complete=False))
        diagnostic.update(native_log_sha256=log_sha, stage='ASSIGNMENT')
        _require(native_input.is_file(), 'Exact native input is unavailable')
        diagnostic['input_sha256'] = sha(native_input)
        _json(diagnostic_path, diagnostic)
        _require(not target.exists(), 'Refusing to overwrite an existing candidate')
        values = {}
        for line in raw_lines:
            for literal in map(int, line.split()[1:]):
                if not literal:
                    continue
                _require(abs(literal) not in values or values[abs(literal)] == (literal > 0), 'Contradictory assignment')
                values[abs(literal)] = literal > 0
        variables = int(config['variables'])
        _require(set(values) == set(range(1, variables + 1)), 'Assignment is incomplete or has out-of-range variables')
        _json(assignment_path, dict(raw_assignment_lines=raw_lines, native_log_sha256=sha(log),
                                   input_sha256=sha(native_input), complete=True,
                                   assignment=[v if values[v] else -v for v in range(1, variables + 1)]))
        n = int(config['n'])
        pairs = [tuple(pair) for pair in config['pairs']]
        m = len(pairs)
        _require(len(set(pairs)) == m and all(0 <= a < b < n for a, b in pairs), 'Invalid simple-graph pair mapping')
        graph_variables = list(range(2*m + 1, 3*m + 1))
        _require(list(config.get('graph_variables', graph_variables)) == graph_variables, 'Graph-variable mapping mismatch')
        metadata_path = native_input.parent / 'INPUT.json'
        metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else None
        if recipe is None and metadata:
            recipe = metadata['recipe']
        _require(recipe is not None or not config.get('scientific'), 'Scientific candidate requires an exact input recipe')
        diagnostic['stage'] = 'INPUT_BINDING'
        if metadata:
            if native_input.name == 'input.inst':
                _require(diagnostic['input_sha256'] == metadata['input_sha256'], 'Preserved input hash mismatch')
            if 'native_sha256' in metadata:
                _require(metadata['native_sha256'] == config['native_sha256'], 'Input/native provenance mismatch')
        if recipe is not None:
            expected_sha, expected_count = _recipe_hash(config, recipe)
            _require(expected_sha == diagnostic['input_sha256'], 'Input bytes do not match their exact recipe')
            diagnostic.update(recipe_sha256=hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest(),
                              recipe_input_sha256=expected_sha)
            for literal in recipe['assumptions']:
                _require(literal and abs(literal) in values and values[abs(literal)] == (literal > 0), 'Region assumption violated')
        else:
            expected_count = None
        if config.get('scientific'):
            _require(n == 28 and pairs == list(itertools.combinations(range(28), 2)), 'Scientific order/pair domain mismatch')
            mapping_path = Path(config.get('mapping_file', Path(config.get('root', ROOT)) / 'artifacts/tmp/S032/INPUTS.json'))
            _require(sha(mapping_path) == config['mapping_sha256'], 'Scientific mapping source hash mismatch')
            mapping = json.loads(mapping_path.read_text())
            _require(mapping['n'] == n and list(map(tuple, mapping['pairs'])) == pairs and mapping['variables'] == variables,
                     'Scientific mapping contents mismatch')
            _require(sha(config['native']) == config['native_sha256'], 'Native executable hash mismatch')
            for name, digest in config.get('source_sha256', {}).items():
                _require(sha(Path(config.get('root', ROOT)) / name) == digest, 'Historical source hash mismatch: ' + name)
        for variable, bit in config.get('graph_units', {}).items():
            _require(int(variable) in graph_variables and values[int(variable)] == bool(bit), 'Graph unit violated')
        diagnostic['stage'] = 'CNF_AND_HEADER'
        with native_input.open() as source:
            header = next(source).split()
            _require(len(header) == 6 and header[:2] == ['p', 'bipsat2'], 'Malformed native header')
            _require(list(map(int, header[2:5])) == [n, m, variables - 2*m], 'Native header domain mismatch')
            declared = int(header[5])
            _require(declared >= 0 and (expected_count is None or declared == expected_count), 'Declared recipe clause count mismatch')
            for pair in pairs:
                fields = next(source).split()
                _require(len(fields) == 3 and fields[0] == 'e' and tuple(map(int, fields[1:])) == pair, 'Native pair order mismatch')
            count = 0
            for line in source:
                literals = list(map(int, line.split()))
                _require(bool(literals) and literals[-1] == 0 and 0 not in literals[:-1], 'Malformed clause')
                _require(all(1 <= abs(v) <= variables for v in literals[:-1]), 'Clause variable out of range')
                _require(any(values[abs(v)] == (v > 0) for v in literals[:-1]), 'CNF clause unsatisfied')
                count += 1
            _require(count == declared, 'Actual native clause count mismatch')
        diagnostic.update(checked_clauses=count, stage='INDEPENDENT_DOMAIN')
        _json(diagnostic_path, diagnostic)
        edge_count = sum(values[v] for v in graph_variables)
        _require(config.get('edge_low', 0) <= edge_count <= config.get('edge_high', m), 'Configured edge domain violated')
        _require(sys.flags.optimize == 0, 'Historical independent checker requires Python assertions enabled')
        from s035_engine import independent_sat
        candidate = independent_sat(config, native_input, log, target)
        candidate.update(input_sha256=diagnostic['input_sha256'], native_log_sha256=diagnostic['native_log_sha256'],
                         full_assignment=str(assignment_path), validation_report=str(diagnostic_path),
                         exact_recipe_sha256=diagnostic.get('recipe_sha256'), checked_clauses=count)
        _json(target, candidate)
        diagnostic.update(status='INDEPENDENT_CANDIDATE_CHECK_PASS_PENDING_DOMAIN_REVIEW', stage='COMPLETE',
                          edge_count=edge_count, counting_lower_bound=candidate['counting_lower_bound'])
        _json(diagnostic_path, diagnostic)
        return candidate
    except Exception as exc:
        diagnostic.update(status='SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED', error=repr(exc))
        _json(diagnostic_path, diagnostic)
        raise CandidateValidationError('SAT review remains pending; ' + str(exc) + '; diagnostic=' + str(diagnostic_path)) from exc
