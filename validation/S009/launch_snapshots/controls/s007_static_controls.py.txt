import json
from pathlib import Path
from s007_run import ROOT,TMP,save
from s007_cover import StrongCover
from biplanar_cnf import read_edges


def static_control(edgefile, splitfile):
    """Complete an actual split, then pin its primary variables in the new CNF."""
    import itertools
    import networkx as nx
    from pysat.solvers import Cadical153
    from check_layers import certify_layer
    edges=read_edges(edgefile); c=StrongCover(edges,lex=False)
    split=json.loads(Path(splitfile).read_text())
    layers=[];faces=[];rotations=[]
    for key in ('E1','E2'):
        g=nx.Graph();g.add_nodes_from(range(c.n));g.add_edges_from(split[key])
        for a,b in itertools.combinations(range(c.n),2):
            if g.has_edge(a,b):continue
            g.add_edge(a,b)
            if not nx.check_planarity(g)[0]:g.remove_edge(a,b)
        assert g.number_of_edges()==3*c.n-6
        good,emb=nx.check_planarity(g);assert good
        seen=set();fs=set()
        for a,b in emb.edges():
            if (a,b) not in seen:
                f=emb.traverse_face(a,b,seen);assert len(f)==3
                fs.add(tuple(sorted(f)))
        es={tuple(sorted(e)) for e in g.edges()}
        layers.append(es);faces.append(fs);rotations.append(certify_layer(c.n,sorted(es)))
    # Cover always includes layer-swap lex even with lex=False: order the two completions.
    vector=lambda i:[int(e in layers[i]) for e in c.pairs]
    if vector(0)>vector(1):
        layers.reverse();faces.reverse();rotations.reverse()
    assumptions=[]
    for i in range(2):
        assumptions.extend(c.E(i,*e) if e in layers[i] else -c.E(i,*e) for e in c.pairs)
        assumptions.extend(c.F(i,*f) if f in faces[i] else -c.F(i,*f) for f in c.triples)
    with Cadical153(bootstrap_with=c.base) as solver:
        assert solver.solve(assumptions=assumptions), 'Actual completion rejected by stronger clauses'
    return dict(n=c.n,completion_edges=[sorted(es) for es in layers],faces=[sorted(fs) for fs in faces],
        independent_rotation_checks=rotations,static=c.static,primary_pin_check='SAT')


def main():
    assert (ROOT/'BASELINE_PASS.json').exists()
    rows=[]
    for row in json.loads((ROOT/'controls.json').read_text())['results']:
        tag=f"control-{row['index']:02d}" if 'index' in row else 'control-'+row['tag']
        ef=TMP/'replay'/f'{tag}.edges' if 'index' in row else Path(f"validation/S003/splits/{row['tag']}.edges")
        split=TMP/'replay'/f'{tag}.split.json'
        rows.append(dict(tag=tag,**static_control(str(ef),str(split))))
        save(ROOT/'static_truth_controls.json',rows)
    print('PASS23 actual-completion static truth controls')

if __name__=='__main__':main()
