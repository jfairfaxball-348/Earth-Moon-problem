"""Independent controls for the S036 cold-diagnostic native.

Reuses the S035 resident-native control design (exhaustive n=5 fixed layers,
64 random n=6 partitions, K3,3, the S030 positive 24-vertex split and a free K9
split), with every persisted geometric clause independently subdivision-checked.
Additionally: every registered diagnostic option arm on a fixed subset, fail-
closed rejection of malformed/unknown/out-of-range options, and the
cooperative stop file (natural exit 0, UNKNOWN, lemma file intact).
"""
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tools')]
from verify_s035_resident_native import lemmas  # noqa: E402
from prepare_s032 import write_inst  # noqa: E402
from s025_check import check_split  # noqa: E402

EXE = ROOT / 'artifacts/tmp/S036/native/bipsat_s032.exe'
# The llvm-mingw runtime DLLs (libc++/libunwind) live beside the pinned compiler.
os.environ['PATH'] = str(ROOT / 'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64/bin') + os.pathsep + os.environ['PATH']
OUT = ROOT / 'artifacts/tmp/S036/native-acceptance'
ARMS = json.loads((ROOT / 'validation/S036/DIAGNOSTIC_ARMS.json').read_text())['arms']


def env_for(options):
    env = os.environ.copy()
    env.pop('EMP_S035_DISABLE_WALK', None)
    env['EMP_S035_DISABLE_CONGRUENCE'] = '1'
    env.pop('EMP_S036_STOP_FILE', None)
    if options:
        env['EMP_S036_CADICAL_OPTIONS'] = options
    else:
        env.pop('EMP_S036_CADICAL_OPTIONS', None)
    return env


def fixed(out, n, parts, name, options=''):
    pairs = list(it.combinations(range(n), 2)); parts = [set(map(tuple, p)) for p in parts]
    clauses = [[2*i+k+1 if e in parts[k] else -(2*i+k+1)] for i, e in enumerate(pairs) for k in (0, 1)]
    path = out / (name + '.inst'); write_inst(path, n, pairs, clauses, 2*len(pairs))
    lemma = out / (name + '.lem'); assert not lemma.exists()
    p = subprocess.run([str(EXE), str(path), '--timeout', '10', '--lemmas', str(lemma)], capture_output=True,
                       text=True, timeout=30, env=env_for(options))
    (out / (name + '.log')).write_text(p.stdout + p.stderr, encoding='utf-8', newline='\n')
    expected = all(nx.check_planarity(nx.Graph(es))[0] for es in parts)
    assert p.returncode == (10 if expected else 20), (name, options, p.returncode, p.stdout[-500:], p.stderr)
    if options:
        assert 'c S036_OPTIONS ' + options in p.stdout, (name, options)
    count = lemmas(lemma, n, pairs)
    if not expected:
        assert count > 0
    return dict(name=name, options=options, expected_planar_layers=expected, returncode=p.returncode,
                checked_lemmas=count)


def k9_instance(out):
    pairs = list(it.combinations(range(9), 2)); cs = []
    for i in range(len(pairs)):
        cs.extend([[2*i+1, 2*i+2], [-(2*i+1), -(2*i+2)]])
    pool = IDPool(start_from=2*len(pairs)+1)
    for k in (0, 1):
        cs += CardEnc.atmost([2*i+k+1 for i in range(len(pairs))], 21, vpool=pool, encoding=EncType.totalizer).clauses
    cs.append([1])
    path = out / 'K9.inst'; write_inst(path, 9, pairs, cs, pool.top)
    return path, pairs


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    smoke = json.loads((ROOT / 'validation/S036/SMOKE.json').read_text()); assert smoke['verdict'] == 'PASS'
    start = time.monotonic(); rows = []
    base = OUT / 'default'; base.mkdir()
    pairs5 = list(it.combinations(range(5), 2))
    for mask in range(1024):
        row = fixed(base, 5, [[e for i, e in enumerate(pairs5) if mask >> i & 1], []], f'n5-{mask:04d}')
        if mask in (0, 1023):
            rows.append(row)
    for seed in range(64):
        rng = random.Random(seed); pairs = list(it.combinations(range(6), 2))
        labels = [rng.randrange(3) for _ in pairs]
        rows.append(fixed(base, 6, [[e for e, k in zip(pairs, labels) if k == 1],
                                     [e for e, k in zip(pairs, labels) if k == 2]], f'n6-{seed:02d}'))
    rows.append(fixed(base, 6, [[e for e in it.product(range(3), range(3, 6))], []], 'K33'))
    pos = json.loads((ROOT / 'validation/S030/POSITIVE24.json').read_text())
    check_split(24, pos['E1'] + pos['E2'], pos['E1'], pos['E2'])
    rows.append(fixed(base, 24, [pos['E1'], pos['E2']], 'positive24'))
    # Every registered arm on a fixed subset: soundness of option plumbing only.
    arm_rows = []
    for arm in ARMS:
        directory = OUT / ('arm-' + arm['name']); directory.mkdir()
        for mask in (0, 1023, 341, 682):
            arm_rows.append(fixed(directory, 5, [[e for i, e in enumerate(pairs5) if mask >> i & 1], []],
                                  f'n5-{mask:04d}', arm['options']))
        for seed in range(8):
            rng = random.Random(seed); pairs = list(it.combinations(range(6), 2))
            labels = [rng.randrange(3) for _ in pairs]
            arm_rows.append(fixed(directory, 6, [[e for e, k in zip(pairs, labels) if k == 1],
                                                 [e for e, k in zip(pairs, labels) if k == 2]],
                                  f'n6-{seed:02d}', arm['options']))
        arm_rows.append(fixed(directory, 6, [[e for e in it.product(range(3), range(3, 6))], []], 'K33', arm['options']))
        arm_rows.append(fixed(directory, 24, [pos['E1'], pos['E2']], 'positive24', arm['options']))
    # Fail-closed option parsing: exit 3 before any search.
    rejects = []
    k9, k9pairs = k9_instance(OUT)
    for bad in ('nosuchoption=1', 'phase=7', 'phase', '=1', 'phase=x', 'phase=1,stable'):
        p = subprocess.run([str(EXE), str(k9), '--timeout', '2'], capture_output=True, text=True, timeout=20,
                           env=env_for(bad))
        assert p.returncode == 3 and 'EMP_S036_CADICAL_OPTIONS' in p.stderr, (bad, p.returncode, p.stderr)
        rejects.append(dict(options=bad, returncode=p.returncode, stderr=p.stderr.strip()))
    # Free K9 (capped) with a cooperative stop after two seconds.
    stop = OUT / 'K9.STOP'; lemma = OUT / 'K9-stop.lem'; log = OUT / 'K9-stop.log'
    env = env_for(''); env['EMP_S036_STOP_FILE'] = str(stop)
    with log.open('w') as f:
        p = subprocess.Popen([str(EXE), str(k9), '--timeout', '120', '--lemmas', str(lemma)], stdout=f,
                             stderr=subprocess.STDOUT, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(2); stop.touch(); requested = time.monotonic()
        code = p.wait(timeout=30); latency = time.monotonic() - requested
    text = log.read_text()
    assert code in (0, 20), (code, text[-800:])
    if code == 0:
        assert 'c S036_COOPERATIVE_STOP' in text and 's UNKNOWN' in text
    assert latency < 10, latency
    stop_count = lemmas(lemma, 9, k9pairs)
    assert stop_count > 0
    # The stop file is ignored when absent: a 2 s capped run ends by timeout.
    lemma2 = OUT / 'K9-timeout.lem'
    p2 = subprocess.run([str(EXE), str(k9), '--timeout', '2', '--lemmas', str(lemma2)], capture_output=True,
                        text=True, timeout=30, env=env_for(''))
    assert p2.returncode in (0, 20) and 'S036_COOPERATIVE_STOP' not in p2.stdout
    data = dict(status='PASS', native=str(EXE), native_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),
                exhaustive_n5_fixed_graphs=1024, random_n6_partitions=64, K33='PASS', positive24='PASS',
                arms=[a['name'] for a in ARMS], arm_fixed_controls=len(arm_rows),
                option_rejections=rejects,
                cooperative_stop=dict(returncode=code, latency_seconds=round(latency, 3), checked_lemmas=stop_count,
                                      marker='c S036_COOPERATIVE_STOP' in text),
                free_K9_timeout=dict(returncode=p2.returncode, checked_lemmas=lemmas(lemma2, 9, k9pairs)),
                rows=rows, arm_rows=arm_rows, seconds=time.monotonic() - start,
                scope='native plumbing/soundness controls only; no scientific verdict')
    (ROOT / 'validation/S036/NATIVE_CONTROLS.json').write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8',
                                                              newline='\n')
    print(json.dumps({k: v for k, v in data.items() if k not in ('rows', 'arm_rows')}, indent=1))


if __name__ == '__main__':
    main()
