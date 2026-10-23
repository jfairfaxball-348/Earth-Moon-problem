"""S036 read-only entry audit: live identities, latches, hashes, resources, SAT-first scan.

Never resumes, suspends, launches or terminates a process and never writes into
S035 artifacts. Output: validation/S036/ENTRY.json and SAT_FIRST_AUDIT.json.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
import psutil
from s036_sat_scan import Scanner, ScanUnavailable, sha
from s035_preserved_lifecycle import thread_state, checked

AREA = ROOT / 'artifacts/tmp/S035/campaign'
S035 = ROOT / 'artifacts/tmp/S035'
OUT = ROOT / 'validation/S036'
SCIENTIFIC = ('campaign', 'benchmark-1', 'benchmark-2', 'benchmark-3', 'imported-s034',
              'phase-diagnostic', 'phase-diagnostic-overlap-aborted',
              'phase-diagnostic-input-rebase-failure')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True, timeout=60).strip()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1) + '\n', encoding='utf-8', newline='\n')


def identities():
    policy = json.loads((AREA / 'RESUME_CONTROL/THREAD_POLICY.json').read_text())
    rows = []
    before = {}
    for pid, row in policy['processes'].items():
        record = dict(pid=int(pid), start_ticks=row['start_ticks'])
        p = checked(record)
        clock = p.cpu_times()
        before[pid] = clock.user + clock.system
    time.sleep(2)
    for pid, row in policy['processes'].items():
        record = dict(pid=int(pid), start_ticks=row['start_ticks'])
        p = checked(record)
        state = thread_state(record)
        keys = {(r['tid'], r['created_ticks']) for r in state}
        expected = {(r['tid'], r['created_ticks']) for r in row['threads']}
        clock = p.cpu_times()
        rows.append(dict(pid=int(pid), start_ticks=row['start_ticks'], name=p.name(), kind=row['kind'],
                         exact_thread_set=keys == expected,
                         suspend_counts=[r['suspend_count'] for r in state],
                         all_suspended=all(r['suspend_count'] >= 1 for r in state),
                         private_bytes=p.memory_info().private,
                         cpu_seconds=clock.user + clock.system,
                         cpu_delta_2s=clock.user + clock.system - before[pid]))
    return dict(policy_sha256=sha(AREA / 'RESUME_CONTROL/THREAD_POLICY.json'),
                committed_policy_sha256=sha(ROOT / 'validation/S035/thread-repair/THREAD_POLICY.json'),
                processes=rows,
                all_exact=all(r['exact_thread_set'] for r in rows),
                all_suspended=all(r['all_suspended'] for r in rows),
                zero_cpu=all(r['cpu_delta_2s'] == 0 for r in rows))


def hashes():
    cfg = json.loads((AREA / 'CONFIG.json').read_text())
    sources = {name: sha(ROOT / name) == digest for name, digest in cfg['source_sha256'].items()}
    contexts = json.loads((AREA / 'RESIDENT_CONTEXTS.json').read_text())['contexts']
    inputs = {}
    for key, context in sorted(contexts.items(), key=lambda kv: int(kv[0])):
        directory = Path(context['directory'])
        meta = json.loads((directory / 'INPUT.json').read_text())
        inputs[key] = dict(directory=str(directory), worker=context['worker'],
                           input_sha256=meta['input_sha256'],
                           input_match=sha(directory / 'input.inst') == meta['input_sha256'],
                           native_log_bytes=(directory / 'native.log').stat().st_size,
                           new_cuts_bytes=(directory / 'new-cuts.lem').stat().st_size)
    return dict(scientific_sources_match=sources, all_sources_match=all(sources.values()),
                native=cfg['native'], native_match=sha(cfg['native']) == cfg['native_sha256'],
                base_match=sha(cfg['base']) == cfg['base_sha256'],
                seed_match=sha(cfg['seed']['path']) == cfg['seed']['sha256'],
                resident_inputs=inputs, all_inputs_match=all(v['input_match'] for v in inputs.values()),
                congruence_disabled=cfg.get('disable_congruence'),
                random_walk_disabled=cfg.get('disable_random_walk'))


def resources():
    vm = psutil.virtual_memory()
    return dict(available_bytes=vm.available, total_bytes=vm.total,
                free_disk_bytes=shutil.disk_usage(ROOT).free,
                logical_cpus=psutil.cpu_count(), physical_cpus=psutil.cpu_count(logical=False),
                battery=str(psutil.sensors_battery()), boot_epoch=psutil.boot_time())


def sat_first():
    started = time.time()
    strict = Scanner(attempt_budget=5, exhaustion_seconds=0)
    scientific_hits = []
    for name in SCIENTIFIC:
        root = S035 / name
        if root.exists():
            scientific_hits += strict.inspect(root.rglob('*'), classify_controls=True,
                                              raise_unavailable=False)
    control = AREA / 'RESUME_CONTROL'
    exit_records = [*control.glob('NATIVE_EXIT*.json'), control / 'TERMINAL.json',
                    *control.glob('history/*/TERMINAL.json'), *control.glob('history/*/NATIVE_EXIT*.json')]
    scientific_hits += strict.inspect(exit_records, raise_unavailable=False)
    # Everything else under S035 and the committed S035 evidence is classified,
    # listed for review, never silently excused.
    other = Scanner(attempt_budget=5, exhaustion_seconds=0)
    other_paths = [p for p in S035.rglob('*')
                   if not (len(p.relative_to(S035).parts) and p.relative_to(S035).parts[0] in SCIENTIFIC)]
    other_paths += list((ROOT / 'validation/S035').rglob('*'))
    other_paths += list((ROOT / 'artifacts/tmp/S036').rglob('*'))
    other_hits = other.inspect(other_paths, raise_unavailable=False)
    grouped = {}
    for path in other_hits:
        rel = Path(path).resolve().relative_to(ROOT)
        grouped.setdefault('/'.join(rel.parts[:4]), []).append(str(rel))
    return dict(status='SCIENTIFIC_SAT_SIGNAL_REQUIRES_PROMINENT_REVIEW' if scientific_hits
                else 'NO_SCIENTIFIC_SAT_CANDIDATE_OR_EXIT10_FOUND',
                scientific_roots=[str(S035 / n) for n in SCIENTIFIC],
                scientific_files_scanned=strict.scanned_files,
                scientific_hits=[dict(path=str(p), sha256=sha(p)) for p in scientific_hits],
                imported_s034_control_hits=strict.controls,
                scientific_unreadable=list(strict.pending.values()),
                exit_records_scanned=[str(p) for p in exit_records if p.exists()],
                other_files_scanned=other.scanned_files,
                other_unreadable=list(other.pending.values()),
                other_hit_count=len(other_hits),
                other_hits_by_directory={k: dict(count=len(v), examples=v[:3]) for k, v in sorted(grouped.items())},
                seconds=time.time() - started, epoch=time.time())


def main():
    entry = dict(session='S036', utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                 head=git('rev-parse', 'HEAD'), tree=git('rev-parse', 'HEAD^{tree}'),
                 remote_main=git('ls-remote', 'origin', 'refs/heads/main').split()[0],
                 status_clean=git('status', '--porcelain') == '',
                 stop_latches=dict(campaign=(AREA / 'STOP').exists(),
                                   s035_resume_control=(AREA / 'RESUME_CONTROL/STOP').exists()),
                 sat_alert_present=(AREA / 'SAT_ALERT.json').exists() or (AREA / 'RESUME_CONTROL/SAT_ALERT.json').exists(),
                 s035_controller_watcher=json.loads((AREA / 'RESUME_CONTROL/ADOPTION.json').read_text()).get('controller'),
                 identities=identities(), hashes=hashes(), resources=resources())
    adoption = json.loads((AREA / 'RESUME_CONTROL/ADOPTION.json').read_text())
    lost = []
    for key in ('controller', 'watcher'):
        record = adoption.get(key)
        try:
            checked(record)
            lost.append(dict(role=key, record=record, alive=True))
        except Exception:
            lost.append(dict(role=key, record=record, alive=False))
    entry['s035_controller_watcher'] = lost
    audit = sat_first()
    write(OUT / 'SAT_FIRST_AUDIT.json', audit)
    entry['sat_first_status'] = audit['status']
    write(OUT / 'ENTRY.json', entry)
    print(json.dumps(dict(sat=audit['status'], scientific_files=audit['scientific_files_scanned'],
                          other_hits=audit['other_hit_count'],
                          unreadable=len(audit['scientific_unreadable']) + len(audit['other_unreadable']),
                          identities_exact=entry['identities']['all_exact'],
                          suspended=entry['identities']['all_suspended'], zero_cpu=entry['identities']['zero_cpu'],
                          sources=entry['hashes']['all_sources_match'], native=entry['hashes']['native_match'],
                          inputs=entry['hashes']['all_inputs_match'], stops=entry['stop_latches'],
                          controller_watcher=[(r['role'], r['alive']) for r in lost],
                          head=entry['head'], remote=entry['remote_main']), indent=1))


if __name__ == '__main__':
    main()
