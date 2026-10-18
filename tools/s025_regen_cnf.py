#!/usr/bin/env python3
"""S025: regenerate a minor-CEGAR UNSAT CNF byte-for-byte from EDGEFILE + LEMMAS.json(.gz).

Rebuilds the base (tools/biplanar_cegar.Cegar) and the eager minor families with the
recorded flags (tools/s025_minor_cegar.MinorCegar), checks the regenerated branch sets
and Lemma C models equal the recorded ones, appends the recorded Kuratowski lemma pairs
in order, and prints the SHA-256 (compare with the certificate's cnf_sha256).
Usage: s025_regen_cnf.py EDGEFILE LEMMAS.json[.gz] OUT.cnf
"""
import gzip
import hashlib
import json
import sys

sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
from biplanar_cnf import read_edges          # noqa: E402
from s025_minor_cegar import MinorCegar      # noqa: E402


def main(edgefile, lemmas, out):
    op = gzip.open if lemmas.endswith('.gz') else open
    with op(lemmas, 'rt') as f:
        data = json.load(f)
    flags = data.get('flags', [])
    rmax = int(flags[flags.index('--rmax') + 1]) if '--rmax' in flags else 5
    cmax = int(flags[flags.index('--lemmaC') + 1]) if '--lemmaC' in flags else 0
    edges = read_edges(edgefile)
    assert [tuple(e) for e in data['edges']] == edges
    c = MinorCegar(edges, rmax=rmax, k2='--k2' in flags, k3='--k3' in flags, cmax=cmax,
                   kB='--noB' not in flags)
    assert [[sorted(R), list(c.cvar[R]), [[list(e) for e in T] for T in c.trees[R]]] for R in c.cvar] == \
        [[b[0], b[1], b[2]] for b in data['branch_sets']]
    assert [list(m) for m in c.cmodels] == [list(m) for m in
                                            [(m[0], m[1], m[2], m[3]) for m in data['cmodels']]]
    c.lemmas = [[tuple(e) for e in k] for k in data['lemmas']]
    cls = c.clauses()
    text = f'p cnf {c.nv} {len(cls)}\n' + ''.join(' '.join(map(str, cl)) + ' 0\n' for cl in cls)
    with open(out, 'w', newline='\n') as f:
        f.write(text)
    print(hashlib.sha256(text.encode()).hexdigest())


if __name__ == '__main__':
    main(*sys.argv[1:4])
