"""Portable S036 record integrity and scanner-repair logic checks (hosted CI).

Not a mathematical proof replay and not a Windows lifecycle replay: the real
Windows controls are recorded in validation/S036/SUPERVISOR_CONTROLS.json and
NATIVE_CONTROLS.json. Here the scanner repair logic is re-exercised with
simulated sharing violations so a regression fails on any platform.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import s036_sat_scan as scan  # noqa: E402

V = ROOT / 'validation/S036'


def read(name):
    return json.loads((V / name).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


state = json.loads((ROOT / 'authoritative/STATE.json').read_text(encoding='utf-8'))
active = state.get('active_session')
if state['last_completed_session'] == 'S035':
    assert active and active['id'] == 'S036' and state['next_session_is_future_unexecuted'] is False
    assert active['no_automatic_S037'] and not active['witness_established'] and not active['whole_stratum_certified']
assert state['confirmed_classical_range'] == dict(state['confirmed_classical_range'], lower=9, upper=12)

entry = read('ENTRY.json')
assert entry['head'] == entry['remote_main'] == '45a2f328471ccad39b49160b12560c0fe1b27f91'
ids = entry['identities']
assert ids['all_exact'] and ids['all_suspended'] and ids['zero_cpu'] and len(ids['processes']) == 12
assert entry['hashes']['all_sources_match'] and entry['hashes']['native_match'] and entry['hashes']['all_inputs_match']
assert all(entry['stop_latches'].values()) and not entry['sat_alert_present']
assert not any(row['alive'] for row in entry['s035_controller_watcher'])
audit = read('SAT_FIRST_AUDIT.json')
assert audit['status'] == 'NO_SCIENTIFIC_SAT_CANDIDATE_OR_EXIT10_FOUND' and audit['scientific_hits'] == []
assert not audit['scientific_unreadable'] and audit['scientific_files_scanned'] > 4000
assert all(key.startswith('validation/S035/') or key.split('/')[3].startswith(
    ('controls-v2', 'resident-acceptance', 'scheduler-controls', 'NATIVE_CONTROLS'))
    for key in audit['other_hits_by_directory'])
smoke = read('SMOKE.json')
assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
policy = V / 'THREAD_POLICY.json'
assert sha(policy) == sha(ROOT / 'validation/S035/thread-repair/THREAD_POLICY.json') == ids['policy_sha256']
native = read('NATIVE_CONTROLS.json')
assert native['status'] == 'PASS' and native['exhaustive_n5_fixed_graphs'] == 1024 and native['random_n6_partitions'] == 64
assert native['cooperative_stop']['returncode'] == 0 and native['cooperative_stop']['marker']
assert len(native['option_rejections']) == 6 and all(r['returncode'] == 3 for r in native['option_rejections'])
arms = read('DIAGNOSTIC_ARMS.json')
assert arms['status'] == 'REGISTERED_BEFORE_ANY_S036_COLD_RUN' and arms['arms'][0]['name'] == 'baseline'
assert native['arms'] == [a['name'] for a in arms['arms']]
plan = read('COLD_CAPACITY_PLAN.json')
assert plan['status'] == 'REGISTERED_BEFORE_ANY_S036_COLD_ADMISSION'
controls = read('SUPERVISOR_CONTROLS.json')
assert controls['status'] == 'PASS' and controls['forced_terminations'] == 0 and not controls['scientific_processes_touched']
assert len(controls['scanner']) == 4 and len(controls['supervisor']) == 6 and len(controls['controller']) == 3
for name, digest in controls['source_sha256'].items():
    assert sha(ROOT / name) == digest, 'Accepted source changed after controls: ' + name
exit1 = read('EXIT1_ATTRIBUTION.json')
assert exit1['status'] == 'ATTRIBUTED' and exit1['taskkill_force_control_exit_code'] == 1
assert len(exit1['rows']) == 21 and not any(r['fatal_marker'] or r['sat_marker'] or r['unsat_marker'] for r in exit1['rows'])

# Portable re-exercise of the repair logic with simulated sharing violations.
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    log = root / 'native.log'; log.write_bytes(b'c active\n')
    real_open = Path.open
    failures = dict(left=0)

    def flaky(self, *args, **kwargs):
        if self == log and failures['left'] > 0:
            failures['left'] -= 1
            raise PermissionError(13, 'simulated sharing violation')
        return real_open(self, *args, **kwargs)
    s = scan.Scanner(attempt_budget=2.0, exhaustion_seconds=60, sleep=lambda _: None)
    assert s.inspect([log]) == []
    log.write_bytes(b'c active\ns SATISFIABLE\n')
    failures['left'] = 3
    with patch.object(Path, 'open', flaky):
        assert s.inspect([log]) == [log] and s.retried_reads == 1
    # Exhaustion: cache is not advanced and the scan fails closed.
    log.write_bytes(b'c active\nc more\n')
    s2 = scan.Scanner(attempt_budget=0.0, exhaustion_seconds=0.0, sleep=lambda _: None)
    failures['left'] = 10 ** 6
    with patch.object(Path, 'open', flaky):
        try:
            s2.inspect([log]); raise AssertionError('no fail-closed exhaustion')
        except scan.ScanUnavailable as exc:
            assert exc.failures[0]['path'] == str(log)
        assert str(log) not in s2.seen and str(log) in s2.pending
        other = root / 'other-RESULT.json'; other.write_text('{"returncode": 10}')
        assert s2.inspect([log, other]) == [other]  # SAT outranks unavailability
    failures['left'] = 0
    log.write_bytes(b's SATISFIABLE\n')
    assert s2.inspect([log]) == [log]
    big = root / 'cross.log'; big.write_bytes(b'c ' + b'x' * (scan.BLOCK - 8) + b'\ns SATI' + b'SFIABLE\n')
    assert scan.Scanner().inspect([big]) == [big]
print('PASS S036 entry/SAT-first/acceptance records and portable scanner-repair logic; '
      'not proof replay, Windows lifecycle replay or a mathematical result')
