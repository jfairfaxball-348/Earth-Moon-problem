#!/usr/bin/env python3
"""Generate CAM-0005 C5 frontier and run hard-capped certificate searches."""
import gzip
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

import networkx as nx
from blowup_graph import blowup
from s004_certify import refute


def images(w):
    return [w[i:]+w[:i] for i in range(5)] + [w[::-1][i:]+w[::-1][:i] for i in range(5)]


def feasible(w):
    if any(w[i]+w[(i+1)%5] > 8 for i in range(5)):
        return False
    for mask in range(1, 32):
        S = [i for i in range(5) if mask >> i & 1]
        n = sum(w[i] for i in S)
        cross = sum(w[i]*w[(i+1)%5] for i in range(5)
                    if i in S and (i+1)%5 in S)
        e = cross+sum(w[i]*(w[i]-1)//2 for i in S)
        if n >= 3 and (e > 6*n-12 or cross > 4*n-8):
            return False
    return True


def setup():
    p = Path('validation/S004/targets')
    p.mkdir(parents=True, exist_ok=True)
    C5 = nx.cycle_graph(5)
    g6 = nx.to_graph6_bytes(C5, header=False).decode().strip()
    weights = sorted({min(images(w)) for w in itertools.product(range(1,9), repeat=5) if feasible(w)})
    maximal = [w for w in weights if not any(
        sum(v) > sum(w) and any(all(a <= b for a,b in zip(w, iv)) for iv in images(v))
        for v in weights)]
    assert len(maximal) == 13, maximal
    children = [(1,6,2,6,2), (2,5,2,6,2), (2,6,1,6,2)]
    ordered = [(2,6,2,6,2), (2,3,5,2,6), (2,5,3,3,5), (2,3,5,3,5)]
    ordered += [w for w in maximal if min(images(w)) not in {min(images(t)) for t in ordered}]
    ordered += children
    names = []
    for w in ordered:
        tag = 'C5-'+''.join(map(str,w))
        edges, _ = blowup(g6,w)
        (p/(tag+'.edges')).write_text(''.join(f'{u} {v}\n' for u,v in edges), newline='\n')
        names.append(tag)
    Path('validation/S004/C5_frontier.json').write_text(json.dumps({
        'canonical_feasible':len(weights), 'maximal':[list(w) for w in maximal],
        'children':[list(w) for w in children], 'run_order':names},indent=2))
    corpus = Path('artifacts/tmp/S004/patil/data/graphs/pool')
    source_names = {'apex-19':'19_12v_57e_w2', 'apex-49':'49_12v_53e_subdivface',
                    'apex-79dh':'79_dh_7_8_31v_148e',
                    'apex-79single':'79_doubleHajos_single_31v_148e'}
    if corpus.exists():
        from biplanar_cnf import read_edges
        rows = []
        for tag, fn in source_names.items():
            source_edges = read_edges(str(corpus/(fn+'.edges')))
            labels = sorted({v for e in source_edges for v in e})
            relabel = dict(zip(labels, range(len(labels))))
            edges = sorted(tuple(sorted((relabel[u], relabel[v]))) for u,v in source_edges)
            n = len(labels)
            apex = sorted(edges+[(v,n) for v in range(n)])
            (p/(tag+'.edges')).write_text(''.join(f'{u} {v}\n' for u,v in apex),newline='\n')
            rows.append({'tag':tag,'source_file':fn+'.edges','labels':labels,
                         'relabel':relabel,'base_n':n,'base_m':len(edges),
                         'apex_deficit':5*n-6-len(edges)})
        edges, _ = blowup(g6, [3]*5)
        (p/'apex-C5K3.edges').write_text(''.join(f'{u} {v}\n' for u,v in sorted(edges+[(v,15) for v in range(15)])),newline='\n')
        Path('validation/S004/apex_targets.json').write_text(json.dumps(rows,indent=2))
    return names


def run_one(tag, route, seconds):
    outdir = Path('validation/S004/search')
    outdir.mkdir(exist_ok=True)
    edgefile = 'validation/S004/targets/'+tag+'.edges'
    prefix = str(outdir/(route+'-'+tag)).replace('\\','/')
    script = 'tools/triangulation_cover.py' if route == 'cover' else 'tools/biplanar_cegar.py'
    flags = ['--lex'] if route == 'cover' else ['--seed-small', '--limit','12']
    start = time.monotonic()
    cmd = [sys.executable,script,edgefile,prefix,str(seconds),*flags]
    row = {'tag':tag,'route':route,'command':cmd,'cap_seconds':seconds}
    try:
        run = subprocess.run(cmd,capture_output=True,text=True,timeout=seconds+10)
        Path(prefix+'.run.log').write_text(run.stdout+run.stderr)
        assert run.returncode == 0, run.stdout+run.stderr
        info = json.loads(run.stdout.strip().splitlines()[-1])
        row.update(info)
    except subprocess.TimeoutExpired as ex:
        row['verdict'] = 'UNKNOWN'
        row['reason'] = 'external wall cap'
        output = (ex.stdout or b'') + (ex.stderr or b'')
        Path(prefix+'.run.log').write_bytes(output)
    row['observed_seconds'] = time.monotonic()-start
    if row['verdict'] in ('SAT','SAT_CHECKED'):
        checked = subprocess.run([sys.executable,'tools/check_layers.py',edgefile,prefix+'.split.json'],
                                 capture_output=True,text=True,timeout=60)
        assert checked.returncode == 0, checked.stdout+checked.stderr
        Path(prefix+'.layercheck.log').write_text(checked.stdout)
        row['layer_checker'] = checked.stdout.strip()
    elif row['verdict'] == 'UNSAT':
        checkscript = 'tools/triangulation_cover.py' if route == 'cover' else 'tools/check_cegar_certificate.py'
        args = ['check',edgefile,prefix] if route == 'cover' else [edgefile,prefix]
        checked = subprocess.run([sys.executable,checkscript,*args],capture_output=True,text=True,timeout=600)
        assert checked.returncode == 0, checked.stdout+checked.stderr
        row['structure_checker'] = checked.stdout.strip()
        row['proof'] = refute(Path(prefix+'.cnf'),Path(prefix+'.drat'),
                             'artifacts/tmp/S004/cadical.exe','artifacts/tmp/S004/drat-trim-mingw.exe')
        for suffix in ('.cnf','.drat','.lemmas.json'):
            file = Path(prefix+suffix)
            if file.exists():
                with gzip.GzipFile(filename=str(file)+'.gz',mode='wb',mtime=0) as f:
                    f.write(file.read_bytes())
                file.unlink()
        Path(prefix+'.regenerated.cnf').unlink(missing_ok=True)
    print(json.dumps(row),flush=True)
    return row


def main():
    if sys.argv[1] == 'setup':
        print(setup())
        return
    lane, route = sys.argv[1:3]
    cap = int(sys.argv[3]) if len(sys.argv)>3 else 600
    if lane == 'C5':
        tags = json.loads(Path('validation/S004/C5_frontier.json').read_text())['run_order']
        totalcap = 3600
    else:
        tags = ['apex-19','apex-49','apex-79dh','apex-79single','apex-C5K3']
        totalcap = 3000
    rows = []
    start = time.monotonic()
    for tag in tags:
        remaining = totalcap-(time.monotonic()-start)
        if remaining < 15:
            break
        rows.append(run_one(tag,route,min(cap,int(remaining))))
        Path(f'validation/S004/{lane}_{route}_results.json').write_text(json.dumps(rows,indent=1))


if __name__ == '__main__':
    main()
