#!/usr/bin/env python3
"""Serial S026 campaigns. All science runs only after job-local D043 smoke.

Each child is externally wall-capped; the workflow limits the whole process tree
to 12 GiB. Cap/error is recorded as UNKNOWN, never a negative graph decision.
"""
import gzip
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
OUT = ROOT / 'artifacts/tmp/S026'
OUT.mkdir(parents=True, exist_ok=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def save(p, obj):
    Path(p).write_text(json.dumps(obj, indent=1))


def child(args, cap, log):
    t = time.monotonic()
    with open(log, 'w') as f:
        p = subprocess.Popen(args, stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            rc = p.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            import signal
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            rc = 'WALL_CAPPED'
    return dict(command=list(map(str, args)), returncode=rc,
                seconds=round(time.monotonic() - t, 3),
                cumulative_children_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                log=str(log.relative_to(OUT)))


def py(tool, *args):
    return [sys.executable, str(ROOT / 'tools' / tool), *map(str, args)]


def certify(edge, prefix, d):
    rec = {}
    for name, args in [
        ('justification', py('s025_check_minor_cert.py', edge, prefix)),
        ('regeneration', py('s025_regen_cnf.py', edge, str(prefix) + '.lemmas.json', d / 'rebuilt.cnf')),
    ]:
        rec[name] = child(args, 600, d / (name + '.log'))
        if rec[name]['returncode'] != 0:
            return rec
    rec['cnf_byte_match'] = sha(str(prefix) + '.cnf') == sha(d / 'rebuilt.cnf')
    if not rec['cnf_byte_match']:
        return rec
    rec['native'] = child(py('s025_certify.py', str(prefix) + '.cnf', d, 1800, 1800),
                          3900, d / 'native.log')
    cp = d / (prefix.name + '.certificate.json')
    if cp.exists():
        rec['certificate'] = json.loads(cp.read_text())
    rec['certified'] = rec.get('certificate', {}).get('verdict') == 'UNSAT_DRAT_VERIFIED'
    if rec['certified']:
        with open(str(prefix) + '.lemmas.json', 'rb') as f, gzip.open(d / 'lemmas.json.gz', 'wb', 9) as g:
            shutil.copyfileobj(f, g)
        # Compact permanent source of CNF plus complete DRAT; raw scratch is disposable.
        for p in [Path(str(prefix) + '.lemmas.json'), Path(str(prefix) + '.cnf'), d / 'rebuilt.cnf']:
            p.unlink()
    return rec


def exact(edge, d, seconds):
    prefix = d / 'minor'
    rec = {'edges_sha256': sha(edge)}
    rec['search'] = child(py('s025_minor_cegar.py', edge, prefix, seconds, '--lemmaC', 5),
                          seconds + 90, d / 'search.log')
    rp = Path(str(prefix) + '.result.json')
    rec['result'] = json.loads(rp.read_text()) if rp.exists() else {'verdict': 'UNKNOWN'}
    if rec['result']['verdict'] == 'UNSAT':
        rec['proof'] = certify(edge, prefix, d)
    elif rec['result']['verdict'] == 'SAT':
        from s025_check import check_split
        from s025_cover_anneal import read_edges
        s = json.loads(Path(str(prefix) + '.split.json').read_text())
        check_split(s['n'], read_edges(edge), s['E1'], s['E2'])
        rec['split_checked'] = True
    rec['verdict'] = ('NONBIPLANAR_CERTIFIED' if rec.get('proof', {}).get('certified') else
                      'BIPLANAR_CHECKED' if rec.get('split_checked') else 'UNKNOWN')
    save(d / 'SUMMARY.json', rec)
    return rec


def c5(tag):
    from blowup_graph import blowup
    d = OUT / ('C5-' + tag)
    d.mkdir(exist_ok=True)
    edges, _ = blowup('Dhc', list(map(int, tag)))
    edge = d / 'graph.edges'
    edge.write_text(''.join(f'{a} {b}\n' for a, b in edges))
    rec = exact(edge, d, 3600)
    print(tag, rec['verdict'], flush=True)


def main():
    mode = sys.argv[1]
    env = {'source_commit': os.environ.get('GITHUB_SHA'), 'run_id': os.environ.get('GITHUB_RUN_ID'),
           'mode': sys.argv[1:], 'source_sha256': {str(p.relative_to(ROOT)): sha(p)
           for pattern in ['s025_*.py', 's026_*.py', 'biplanar_cegar.py', 'blowup_graph.py']
           for p in (ROOT / 'tools').glob(pattern)}}
    save(OUT / 'SOURCE.json', env)
    if mode == 'c5':
        c5(sys.argv[2])
    elif mode == 'source':
        from s026_source import generate
        generate(OUT)
    else:
        raise ValueError(mode)


if __name__ == '__main__':
    main()
