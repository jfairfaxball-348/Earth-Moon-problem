"""Portable S034 running-record integrity; never native/proof replay or CI science."""
import hashlib
import gzip
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s034_regions import validate_partition

def read(name):
    return json.loads((ROOT/name).read_text())

manifest = read('sessions/S034/RUNNING_MANIFEST.json')
for name, row in manifest['files'].items():
    p = ROOT/name
    assert p.stat().st_size == row['bytes'], name
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], name
smoke = read('validation/S034/SMOKE.json')
native = read('validation/S034/NATIVE_CONTROLS.json')
audit = read('validation/S034/INPUT_AUDIT.json')
controls = read('validation/S034/SCHEDULER_CONTROLS.json')
config = read('validation/S034/REGISTERED_CONFIG.json')
assert smoke['verdict'] == 'PASS'
assert smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
assert native['exhaustive_n5_fixed_graphs'] == 1024 and native['K33'] == native['positive24'] == 'PASS'
assert native['free_K9'] == 'UNKNOWN_AT_2S'
assert native['native_sha256'] == controls['native_sha256'] == config['native_sha256']
assert controls['status'] == 'PASS' and controls['exact_small_graph_assignments'] == 512
assert controls['controller_kill_restart'] == 'PASS' and controls['damaged_proof_rejected']
assert controls['native_absolute_deadline'] == controls['guardian_deadline'] == 'PASS_UNKNOWN'
assert audit['status'] == 'PASS' and audit['bijective_renaming_checked']
assert audit['independently_checked_native_clauses'] == 2579937
assert audit['lemma_sha256'] == config['seed']['sha256'] == '6e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177'
assert config['variables'] == 17976 and config['base_clauses'] == 336030
assert config['deadline'] == read('docs/D073_S034_OVERNIGHT_AUTHORIZATION.json')['deadline_epoch'] == 1792648800
assert config['workers'] == 1 and not config['concurrency_increase_validated']
assert config['bits'] == 8
# Independently reconstruct the entire assumption/weight partition from pinned registration.
import itertools
import math
units = {int(k): v for k, v in config['graph_units'].items()}
free = [v for v in config['graph_variables'] if v not in units]
cells = []
for i, values in enumerate(itertools.product((False, True), repeat=8)):
    present = sum(units.values())+sum(values)
    count = sum(math.comb(len(free)-8, m-present) for m in (155, 156)
                if 0 <= m-present <= len(free)-8)
    cells.append(dict(id=i, assumptions=[v if b else -v for v, b in zip(free[:8], values)], weight=str(count)))
assert validate_partition(config, cells)
with tarfile.open(ROOT/'validation/S034/native.tar.gz') as archive:
    assert hashlib.sha256(archive.extractfile('native/bipsat_s034').read()).hexdigest() == config['native_sha256']
    source = archive.extractfile('native/bipsat_s032.cpp').read().decode()
    assert 'EMP_ABSOLUTE_DEADLINE' in source and source.count('S032 independent subdivision guard') == 2
state = read('authoritative/STATE.json')
if state.get('active_session', {}).get('id') == 'S034':
    assert state['last_completed_session'] == 'S033' and state['active_session']['status'] == 'RUNNING'
    assert state['next_session_is_future_unexecuted'] is False
    for name, digest in controls['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest
assert (ROOT/'sessions/S034/EXECUTED_PROMPT.md').read_bytes() == (ROOT/'sessions/S033/S034_FUTURE_PROMPT.md').read_bytes()
final_path = ROOT/'validation/S034/FINAL_MANIFEST.json'
if final_path.exists():
    final = read('validation/S034/FINAL_MANIFEST.json')
    for name, row in final['files'].items():
        p = ROOT/name
        assert p.stat().st_size == row['bytes'], name
        h = hashlib.sha256()
        with p.open('rb') as source:
            for block in iter(lambda: source.read(1024*1024), b''):
                h.update(block)
        assert h.hexdigest() == row['sha256'], name
    summary = read('validation/S034/SUMMARY.json')
    assert summary['status'] == 'COMPLETED_SAFETY_STOP_UNKNOWN'
    assert summary['stop_reason'] == 'SAFETY_DISK_RESERVE'
    assert summary['proof_closed_regions'] == len(summary['certificates']) == 16
    assert summary['total_visits'] == summary['visited_regions'] == 102
    assert summary['unresolved_regions'] == 240
    assert summary['not_visited_regions'] == 154 and summary['unresolved_visited_regions'] == 86
    assert summary['new_geometric_clauses'] == 93047
    assert summary['total_geometric_clause_occurrences'] == 2672984
    assert summary['all_recorded_workers_stopped'] and not summary['native_cdcl_state_saved']
    assert summary['mathematical_verdict'] == 'UNKNOWN' and not summary['whole_stratum_certified']
    assert summary['witness'] is None and not summary['certified_strata']
    assert not summary['new_DRAT_replay']
    with gzip.open(ROOT/'validation/S034/REGIONS.json.gz', 'rt') as f:
        regions = json.load(f)
    assert validate_partition(config, regions['cells'])
    assert all(c['claim'] is None for c in regions['cells'])
    assert sum(c['visits'] for c in regions['cells']) == 102
    assert sum(c['status']=='UNSAT_DRAT_VERIFIED' for c in regions['cells']) == 16
    inventory = read('validation/S034/RUNTIME_INVENTORY.json')
    assert inventory['format'] == 'S034_SOLID_PROOF_CHUNKS_V1'
    assert len(inventory['files']) == 1510
    assert sum(v['bytes'] for k,v in inventory['files'].items() if k.endswith('/proof.drat')) == 11200738114
    prefix = inventory['runtime_prefix']+'/'
    for row in summary['certificates']:
        cell = regions['cells'][row['cell']]
        cert = read(f"validation/S034/certificates/cell-{row['cell']:04d}.json")
        assert cert['cell'] == cell['id'] and cert['assumptions'] == cell['assumptions']
        assert cert['formula_sha256'] == row['formula_sha256']
        assert cert['proof_sha256'] == inventory['files'][cert['proof'].removeprefix(prefix)]['sha256']
        assert cert['checker_log_sha256'] == inventory['files'][cert['checker_log'].removeprefix(prefix)]['sha256']
        assert cert['checker_sha256'] == config['checker_sha256']
        log = (ROOT/f"validation/S034/certificates/cell-{row['cell']:04d}.check.log").read_bytes()
        assert hashlib.sha256(log).hexdigest() == cert['checker_log_sha256']
        assert b's VERIFIED' in log
    with gzip.open(ROOT/'validation/S034/new-geometric.lem.gz','rb') as f:
        assert sum(1 for line in f) == 93047
    prompt = (ROOT/'sessions/S034/S035_FUTURE_PROMPT.md').read_bytes()
    assert b'Windows' in prompt and b'multiple' in prompt and b'FUTURE / UNEXECUTED' in prompt
    if state['last_completed_session'] == 'S034':
        assert state['recommended_next_session'] == 'S035' and not state.get('active_session')
        assert state['next_session_is_future_unexecuted'] is True
        assert prompt == (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()
    print('PASS S034 final archive/receipts/256-region integrity and S035 Windows multiple-worker handover; not proof replay or search exhaustion')
else:
    print('PASS S034 registered256-region partition, fresh phone gates and immutable running evidence; not a closeout or new mathematical claim')
