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


def certify(edge, prefix, d, two=False):
    rec = {}
    for name, args in [
        ('justification', py('s026_check_two_branch.py' if two else 's025_check_minor_cert.py', edge, prefix)),
        ('regeneration', py('s026_check_two_branch.py', 'regen', edge, prefix, d / 'rebuilt.cnf') if two else
         py('s025_regen_cnf.py', edge, str(prefix) + '.lemmas.json', d / 'rebuilt.cnf')),
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


def exact(edge, d, seconds, two=False):
    prefix = d / 'minor'
    rec = {'edges_sha256': sha(edge)}
    args = py('s026_two_branch.py', edge, prefix, seconds) if two else py(
        's025_minor_cegar.py', edge, prefix, seconds, '--lemmaC', 5)
    rec['search'] = child(args,
                          seconds + 90, d / 'search.log')
    rp = Path(str(prefix) + '.result.json')
    rec['result'] = json.loads(rp.read_text()) if rp.exists() else {'verdict': 'UNKNOWN'}
    if rec['result']['verdict'] == 'UNSAT':
        rec['proof'] = certify(edge, prefix, d, two)
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
    recovered = ROOT / 'validation/S026/recovered' / (tag+'.lemmas.json.gz')
    if recovered.exists():
        prefix = d / 'minor'
        with gzip.open(recovered, 'rb') as f, open(str(prefix)+'.lemmas.json', 'wb') as g:
            shutil.copyfileobj(f, g)
        manifest = next(r for r in json.loads((recovered.parent/'MANIFEST.json').read_text()) if r['tag']==tag)
        regeneration = child(py('s025_regen_cnf.py', edge, str(prefix)+'.lemmas.json', str(prefix)+'.cnf'),
                             600, d/'recovery.log')
        assert regeneration['returncode'] == 0
        assert sha(str(prefix)+'.cnf') == manifest['original_cnf_sha256']
        proof = certify(edge, prefix, d)
        rec = {'recovered_S025': True, 'original_manifest': manifest, 'recovery': regeneration,
               'proof': proof, 'verdict': 'NONBIPLANAR_CERTIFIED' if proof.get('certified') else 'UNKNOWN'}
        save(d/'SUMMARY.json', rec)
    else:
        controls()
        rec = exact(edge, d, 600, two=True)
    print(tag, rec['verdict'], flush=True)


def controls():
    from s026_two_branch import TwoBranch
    from s025_check import check_split
    from blowup_graph import blowup
    from biplanar_cnf import read_edges
    d = OUT/'controls'
    d.mkdir(exist_ok=True)
    cases = []
    p = ROOT/'validation/S003/splits/J1.split.json'
    cases.append(('J1', json.loads(p.read_text()), read_edges(p.with_name('J1.edges'))))
    c5s = json.load(gzip.open(ROOT/'validation/S025/C5_CLASSIFY.json.gz', 'rt'))['results']
    r = next(r for r in c5s if r['w']==[3,3,3,3,4] and r.get('split_checked'))
    es, _ = blowup('Dhc', r['w'])
    cases.append(('C5-33334', {'n':16, 'E1':r['E1'], 'E2':r['E2']}, es))
    results = []
    for name, split, es in cases:
        check_split(split['n'], es, split['E1'], split['E2'])
        c = TwoBranch(es)
        layers = [nx_graph(split[k], split['n']) for k in ('E1','E2')]
        true = {c.idx[tuple(e)] for e in split['E1']}
        import networkx as nx
        for R, cs in c.cvar.items():
            for j, v in enumerate(cs):
                if nx.is_connected(layers[j].subgraph(R)):
                    true.add(v)
        for (q, R, j), v in c.avar.items():
            if any(layers[j-1].has_edge(q,y) for y in R):
                true.add(v)
        for (R, S, j), v in c.pvar.items():
            if any(layers[j-1].has_edge(a,b) for a,b in it.product(R,S)):
                true.add(v)
        assert all(any((x>0)==(abs(x) in true) for x in cl) for cl in c.minor_clauses)
        edge = d/(name+'.edges')
        edge.write_text(''.join(f'{a} {b}\n' for a,b in es))
        prefix = d/name
        c.dump(prefix)
        for mode, args in [('check', py('s026_check_two_branch.py',edge,prefix)),
                           ('regen', py('s026_check_two_branch.py','regen',edge,prefix,d/(name+'.regen.cnf')))]:
            result=child(args,600,d/(name+'.'+mode+'.log'))
            assert result['returncode']==0, result
        results.append({'name':name,'known_split':'PASS','all_minor_clauses_satisfied':True,
                        'two_models':len(c.two_models),'checker_and_byte_regeneration':'PASS'})
    assert sum(r['two_models'] for r in results)>0
    # Fresh checked K9 native proof is a prerequisite in this very job's smoke.
    smoke=json.loads((ROOT/'artifacts/tmp/cloud_smoke/RESULT.json').read_text())
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    save(d/'SUMMARY.json',{'positive_controls':results,'K9_retained_and_fresh':'PASS_IN_SAME_JOB_SMOKE'})


def nx_graph(edges,n):
    import networkx as nx
    g=nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    return g


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
