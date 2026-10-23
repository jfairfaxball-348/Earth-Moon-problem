"""Read-only pilot evaluation and independent audit of new geometric deltas.

Only new files under validation/S035/resume/live are written. No original worker,
source journal, old ledger, claim or mathematical certificate is changed.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tools')]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read(path):
    return json.loads(Path(path).read_text())


def sha(path, limit=None):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        while limit is None or limit:
            block = source.read(1024 * 1024 if limit is None else min(limit, 1024 * 1024))
            if not block:
                require(limit in (None, 0), 'Truncated prefix while hashing')
                break
            digest.update(block)
            if limit is not None:
                limit -= len(block)
    return digest.hexdigest()


def save(path, value):
    with Path(path).open('w', encoding='utf-8', newline='\n') as destination:
        json.dump(value, destination, indent=1)
        destination.write('\n')
        destination.flush()
        os.fsync(destination.fileno())


def preserve(source, destination, inventory):
    source, destination = Path(source), Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    require(not destination.exists(), 'Refusing to overwrite snapshot')
    shutil.copyfile(source, destination)
    require(sha(source) == sha(destination), 'Snapshot copy hash mismatch')
    inventory.append(dict(source=str(source), copy=str(destination), sha256=sha(destination),
                          bytes=destination.stat().st_size))


def key(record):
    return record['pid'], record['start_ticks']


def telemetry(before, after, adoption, events):
    expected = {0, 7, 127, 255}
    old = {row['cell']: row for row in before['native']}
    new = {row['cell']: row for row in after['native']}
    contexts = {row['cell']: row for row in adoption['contexts']}
    require(set(old) == set(new) == set(contexts) == expected, 'Resident membership differs')
    require(before['all_native_paused'] and after['all_native_paused'], 'Native pause sampling failed')
    require(before['all_legacy_preserved'] and after['all_legacy_preserved'], 'Legacy preservation failed')
    old_legacy = {row['pid']: row for row in before['legacy']}
    new_legacy = {row['pid']: row for row in after['legacy']}
    require(len(old_legacy) == len(new_legacy) == 8 and set(old_legacy) == set(new_legacy), 'Eight legacy identities differ')
    require(all(row['same_identity'] and row['status'] == 'stopped' for row in new_legacy.values()), 'A legacy process resumed or changed')
    require(adoption['status'] == 'PAUSED' and adoption['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED', 'Pilot did not complete normally')
    require(not adoption.get('pause_errors'), 'Pilot pause reported errors')
    active, peak, counts = set(), 0, Counter()
    for event in events:
        if event['kind'] == 'same_identity_resumed':
            cell = event['cell']
            require(cell in expected and cell not in active, 'Duplicate or unknown executing identity')
            require(key(event['worker']) == key(old[cell]['worker']), 'Journal worker identity differs')
            active.add(cell)
            counts[cell] += 1
            peak = max(peak, len(active))
            require(len(active) <= 2, 'More than two executing native slots')
        elif event['kind'] == 'fair_turn_paused':
            require(event['cell'] in active, 'Paused an unclaimed executing identity')
            active.remove(event['cell'])
        elif event['kind'] == 'preservation_pause':
            require(not event.get('errors'), 'Final preservation journal reported errors')
            active.clear()
    require(events and events[-1]['kind'] == 'preservation_pause' and not active, 'Missing final pause journal')
    require(peak == 2, 'Pilot did not demonstrate the two-slot bound')
    rows = []
    for cell in sorted(expected):
        a, b, context = old[cell], new[cell], contexts[cell]
        require(key(a['worker']) == key(b['worker']) == key(context['worker']), 'Native identity was replaced')
        require(a['status'] == b['status'] == 'stopped' and a['sample_cpu_delta'] == b['sample_cpu_delta'] == 0,
                'Native is not fully paused with zero sampled CPU')
        require(counts[cell] >= 2 and context['turns'] >= 2, 'Not every resident resumed twice')
        require(context['state'] == 'PAUSED', 'Adopted native state is not paused')
        cpu = b['cpu_seconds'] - a['cpu_seconds']
        require(cpu > 0, 'No positive active CPU delta for region ' + str(cell))
        require(a['counters'] is not None and b['counters'] is not None, 'Missing native counters')
        deltas = {name: b['counters'][name] - a['counters'][name] for name in ('conflicts', 'decisions', 'propagations')}
        require(all(value >= 0 for value in deltas.values()), 'Native counters decreased')
        require(b['log_bytes'] >= a['log_bytes'] and b['geometric_journal_bytes'] >= a['geometric_journal_bytes'], 'An append-only journal shrank')
        rows.append(dict(cell=cell, worker=b['worker'], turns=counts[cell], active_cpu_seconds=cpu,
                         before_counters=a['counters'], after_counters=b['counters'], deltas=deltas,
                         conflicts_per_active_cpu_second=deltas['conflicts'] / cpu,
                         paused_cpu_delta=b['sample_cpu_delta'], private_bytes=b['private_bytes']))
    return rows, peak


def extract_delta(context, old, new, audit_rows, cfg, target):
    from audit_s033_fast import subdivision
    source = Path(context['directory']) / 'new-cuts.lem'
    registered = next(row for row in audit_rows if (ROOT / row['path']).resolve() == source.resolve())
    offset = registered['complete_bytes']
    require(offset <= old['geometric_journal_bytes'], 'Old complete prefix exceeds baseline length')
    require(old['geometric_journal_bytes'] - offset == registered['omitted_incomplete_tail_bytes'], 'Unexpected baseline partial tail')
    require(sha(source, offset) == registered['prefix_sha256'], 'Original geometric prefix changed')
    limit = new['geometric_journal_bytes']
    require(source.stat().st_size == limit, 'Geometric source changed after the paused snapshot')
    count = complete = 0
    kinds = Counter()
    digest = hashlib.sha256()
    pairs = cfg['pairs']
    with source.open('rb') as stream, target.open('xb') as destination:
        stream.seek(offset)
        while stream.tell() < limit:
            line = stream.readline(limit - stream.tell())
            if not line.endswith(b'\n'):
                break
            literals = list(map(int, line.split()))
            require(literals and literals[-1] == 0 and 0 not in literals[:-1], 'Malformed geometric clause')
            literals = literals[:-1]
            require(literals and len(literals) == len(set(literals)), 'Empty or duplicated geometric literals')
            require(all(-2 * len(pairs) <= literal < 0 for literal in literals), 'Geometric literal out of range')
            require(len({(-literal - 1) % 2 for literal in literals}) == 1, 'Geometric clause spans layers')
            kind = subdivision([tuple(pairs[(-literal - 1) // 2]) for literal in literals])
            destination.write(line)
            digest.update(line)
            complete += len(line)
            count += 1
            kinds[kind] += 1
        destination.flush()
        os.fsync(destination.fileno())
    require(sha(target) == digest.hexdigest(), 'Delta copy hash mismatch')
    return dict(cell=context['cell'], source=str(source), baseline_bytes=old['geometric_journal_bytes'],
                baseline_complete_bytes=offset, baseline_partial_bytes=old['geometric_journal_bytes'] - offset,
                end_complete_bytes=offset + complete, observed_source_bytes=limit,
                omitted_incomplete_tail_bytes=limit - offset - complete,
                preserved_delta=str(target), delta_sha256=digest.hexdigest(), delta_bytes=complete,
                independently_checked_clause_occurrences=count, subdivision_counts=dict(kinds),
                status='INDEPENDENT_SUBDIVISION_PASS', uniqueness_claimed=False)


def evaluate(before_path, after_path, control, output):
    require(sys.flags.optimize == 0, 'Independent subdivision checks require Python assertions')
    output.mkdir(parents=True, exist_ok=True)
    event = output / ('evaluation-' + str(time.time_ns()))
    event.mkdir()
    report = dict(status='FAIL', created_epoch=time.time(), originals_modified=False,
                  scientific_verdict='UNKNOWN', whole_stratum_certified=False,
                  warning='Counters and clause occurrences are not graph coverage or an ETA.',
                  preserved=[], source_sha256=sha(__file__), evaluation_directory=str(event))
    try:
        for source, name in ((before_path, 'BEFORE_PILOT.json'), (after_path, 'AFTER_PILOT.json'),
                             (control / 'ADOPTION.json', 'ADOPTION.json'),
                             (control / 'JOURNAL.jsonl', 'JOURNAL.jsonl'),
                             (control / 'CONTROLLER.json', 'CONTROLLER.json'),
                             (control / 'WATCHER.json', 'WATCHER.json')):
            if Path(source).exists():
                preserve(source, event / name, report['preserved'])
        before, after = read(before_path), read(after_path)
        adoption = read(control / 'ADOPTION.json')
        events = [json.loads(line) for line in (control / 'JOURNAL.jsonl').read_text().splitlines() if line.strip()]
        require((control / 'STOP').exists() and (control.parent / 'STOP').exists(), 'Either preservation STOP is missing')
        require(not (control / 'SAT_ALERT.json').exists() and not (control.parent / 'SAT_ALERT.json').exists(), 'SAT alert requires priority review')
        rows, peak = telemetry(before, after, adoption, events)
        cfg = read(control.parent / 'CONFIG.json')
        mapping_path = ROOT / 'artifacts/tmp/S032/INPUTS.json'
        require(sha(mapping_path) == cfg['mapping_sha256'], 'Literal mapping hash changed')
        mapping = read(mapping_path)
        require(mapping['n'] == cfg['n'] == 28 and mapping['pairs'] == cfg['pairs'], 'Literal pair mapping differs')
        frozen_audit = read(ROOT / 'validation/S035/pause/RAW_JOURNAL_AUDIT.json')
        require(frozen_audit['status'] == 'PASS_ALL_SCIENTIFIC_COMPLETE_PREFIXES', 'Missing original complete-prefix audit')
        old = {row['cell']: row for row in before['native']}
        new = {row['cell']: row for row in after['native']}
        deltas = []
        for context in adoption['contexts']:
            cell = context['cell']
            directory = Path(context['directory'])
            for name in ('native.log', 'INPUT.json'):
                preserve(directory / name, event / f'cell-{cell:04d}' / name, report['preserved'])
            deltas.append(extract_delta(context, old[cell], new[cell], frozen_audit['journals'], cfg,
                                        event / f'cell-{cell:04d}' / 'pilot-geometric-delta.lem'))
        for checkpoint in (control / 'checkpoints').glob('*.json'):
            preserve(checkpoint, event / 'checkpoints' / checkpoint.name, report['preserved'])
        report.update(status='PASS', native=rows, peak_executing_slots=peak,
                      all_four_same_identities=True, all_eight_legacy_stopped=True,
                      all_four_native_paused_zero_cpu=True, every_region_resumed_twice=True,
                      geometric_deltas=deltas,
                      independently_checked_new_clause_occurrences=sum(row['independently_checked_clause_occurrences'] for row in deltas),
                      geometric_clauses_added_to_old_ledger=False, new_region_closures=0,
                      mapping_sha256=cfg['mapping_sha256'])
    except Exception as exc:
        report['error'] = repr(exc)
    save(event / 'RESULT.json', report)
    save(output / 'PILOT_EVALUATION.json', report)
    print(json.dumps({k: report[k] for k in ('status', 'evaluation_directory', 'scientific_verdict')}, indent=1))
    if report['status'] != 'PASS':
        print(report['error'])
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, default=ROOT / 'validation/S035/resume/BEFORE_PILOT.json')
    parser.add_argument('--after', type=Path, default=ROOT / 'validation/S035/resume/AFTER_PILOT.json')
    parser.add_argument('--control', type=Path, default=ROOT / 'artifacts/tmp/S035/campaign/RESUME_CONTROL')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    require(args.output.resolve().is_relative_to(Path(__file__).resolve().parent), 'Outputs must stay inside the new live evidence directory')
    evaluate(args.before, args.after, args.control, args.output)
