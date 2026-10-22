"""Read-only final audit of recorded S034 cuts, exact recipes and proof receipts.

Reconstructs formula hashes and verifies original pinned checker receipts; does
not rerun solvers or claim a second independent DRAT replay.
"""
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
sys.path.insert(0, str(ROOT/'scripts'))
from s034_regions import sha, validate_partition, live_identity
from audit_s033_fast import subdivision

AREA = ROOT/'artifacts/tmp/S034/campaign'
OUT = ROOT/'validation/S034'

def read(p):
    return json.loads(Path(p).read_text())

def stream_hash(h, p, skip_header=False):
    # Match registered materialise(): universal newline input, LF-only output.
    # Retained Windows rule bytes can contain CRLF; their raw SHA stays pinned.
    with Path(p).open('r') as f:
        if skip_header:
            next(f)
        for block in iter(lambda: f.read(1024*1024), ''):
            h.update(block.encode())

def main():
    config, data = read(AREA/'CONFIG.json'), read(AREA/'REGIONS.json')
    stop = read(AREA/'STOPPED.json')
    assert stop['status'] == 'STOPPED' and stop['reason'] == 'SAFETY_DISK_RESERVE'
    assert validate_partition(config, data['cells'])
    assert all(c['claim'] is None for c in data['cells'])
    assert not list(AREA.rglob('CANDIDATE.json'))
    for f in AREA.rglob('WORKER.json'):
        w = read(f)
        assert not live_identity(w['pid'], w['start_ticks']), f
    checked = {}
    count = 0
    with gzip.GzipFile(filename=str(OUT/'new-geometric.lem.gz'), mode='wb', mtime=0) as dest:
        for row in data['accepted_cuts']:
            p = Path(row['path'])
            assert str(p) not in checked
            h, lines = hashlib.sha256(), 0
            with p.open('rb') as source:
                for line in source:
                    xs = list(map(int, line.split()))
                    assert xs.pop() == 0 and xs and len(xs) == len(set(xs))
                    assert all(-2*len(config['pairs']) <= x < 0 for x in xs)
                    assert len({(-x-1) % 2 for x in xs}) == 1
                    subdivision([tuple(config['pairs'][(-x-1)//2]) for x in xs])
                    h.update(line); dest.write(line); lines += 1
            assert h.hexdigest() == row['sha256'] and lines == row['count']
            checked[str(p)] = row
            count += lines
    assert count == 93047
    assert sha(config['base']) == config['base_sha256']
    assert sha(config['seed']['path']) == config['seed']['sha256']
    certificates = []
    for cell in data['cells']:
        if cell['status'] != 'UNSAT_DRAT_VERIFIED':
            assert cell['status'] == 'UNKNOWN'
            continue
        cert = read(cell['certificate'])
        recipe = cert['formula_recipe']
        assert cert['cell'] == cell['id'] and cert['assumptions'] == cell['assumptions'] == recipe['assumptions']
        assert recipe['mapping_sha256'] == config['mapping_sha256'] == cert['mapping_sha256']
        assert recipe['base_sha256'] == config['base_sha256']
        assert recipe['sources'][0] == config['seed']
        for row in recipe['sources'][1:]:
            assert checked[row['path']] == row
        clauses = recipe['base_clauses']+sum(s['count'] for s in recipe['sources'])+len(recipe['assumptions'])
        h = hashlib.sha256(f"p cnf {recipe['variables']} {clauses}\n".encode())
        stream_hash(h, recipe['base'], True)
        for row in recipe['sources']:
            stream_hash(h, row['path'])
        for lit in recipe['assumptions']:
            h.update(f'{lit} 0\n'.encode())
        assert h.hexdigest() == cert['formula_sha256']
        assert sha(cert['proof']) == cert['proof_sha256']
        assert sha(cert['checker_log']) == cert['checker_log_sha256']
        assert cert['checker_sha256'] == config['checker_sha256']
        receipt = read(Path(cell['certificate']).parent/'check-RESULT.json')
        assert receipt['returncode'] == 0 and receipt['reason'] is None
        assert 's VERIFIED' in Path(cert['checker_log']).read_text()
        certificates.append(dict(cell=cell['id'], formula_sha256=cert['formula_sha256'],
            proof_sha256=cert['proof_sha256'], checker_log_sha256=cert['checker_log_sha256']))
    assert len(certificates) == 16
    journal = [json.loads(x) for x in (AREA/'JOURNAL.jsonl').read_text().splitlines()]
    started = next(x['utc'] for x in journal if x['kind'] == 'native_start')
    elapsed = (datetime.fromisoformat(stop['stopped_utc'])-datetime.fromisoformat(started)).total_seconds()
    result = dict(session='S034', status='COMPLETED_SAFETY_STOP_UNKNOWN',
        executor='Codex on Samsung SM-S921B / Android16 Termux Debian13 proot ARM64',
        started_utc=started, stopped_utc=stop['stopped_utc'], elapsed_campaign_seconds=elapsed,
        stop_reason=stop['reason'], total_regions=256, visited_regions=sum(c['visits'] > 0 for c in data['cells']),
        total_visits=sum(c['visits'] for c in data['cells']), proof_closed_regions=16,
        unresolved_regions=240, not_visited_regions=sum(not c['visits'] for c in data['cells']),
        unresolved_visited_regions=sum(c['visits'] > 0 and c['status']=='UNKNOWN' for c in data['cells']),
        new_geometric_clauses=count, clause_count_note='Persisted independently checked occurrences; not a globally unique count.',
        inherited_geometric_clauses=2579937, total_geometric_clause_occurrences=2579937+count,
        cut_reaudit='PASS_ALL_93047', partition_audit='PASS_256_EXHAUSTIVE_DISJOINT',
        certificate_integrity_audit='PASS_RECONSTRUCTED_FORMULA_HASHES_AND_ORIGINAL_PINNED_DRAT_RECEIPTS',
        new_DRAT_replay=False, certificates=certificates,
        outcomes=dict(Counter(c.get('last_outcome','NOT_RUN') for c in data['cells'])),
        peak_observed_aggregate_rss_kib=stop['progress']['controller']['peak_aggregate_rss_kib'],
        memory_cap_note='1GiB sampled aggregate RSS visit cap; observed sampling overshoot checkpointed/requeued.',
        all_recorded_workers_stopped=True, native_cdcl_state_saved=False,
        thermal='UNAVAILABLE', mathematical_verdict='UNKNOWN', whole_stratum_certified=False,
        witness=None, certified_strata=[], exact_new_graph_exclusions='NOT_ESTABLISHED',
        baseline_vs_learned_closure_benefit='NOT_SEPARATELY_MEASURED', range=dict(lower=9,upper=12),
        S11_m155_156='UNKNOWN', S11_m154_regular='SOURCE_STATED_NOT_PROGRAMME_DECIDED',
        S10='NOT_RUN', S9='NOT_RUN', S8='NOT_RUN', next_session='S035_FUTURE_UNEXECUTED_WINDOWS_MULTIPLE_WORKERS')
    (OUT/'SUMMARY.json').write_text(json.dumps(result, indent=2)+'\n')
    for name in ('REGIONS.json','STOPPED.json','GUARDIAN.json','CONTROLLER.json','JOURNAL.jsonl'):
        with gzip.GzipFile(filename=str(OUT/(name+'.gz')), mode='wb', mtime=0) as f:
            f.write((AREA/name).read_bytes())
    print('PASS final S034 audit:', count, 'clauses;', len(certificates), 'checked-proof receipts; UNKNOWN')

if __name__ == '__main__':
    main()
