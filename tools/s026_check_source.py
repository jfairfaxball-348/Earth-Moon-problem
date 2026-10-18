#!/usr/bin/env python3
"""Independent finite graph/certificate checks for the S026 generated source.

Graph construction below does not import the blow-up generator or map finder.
This checks explicit positive containment maps, not completeness of sampling.
"""
import gzip
import itertools as it
import json
from pathlib import Path
import sys
import networkx as nx


def graph(g6,w):
    B=nx.from_graph6_bytes(g6.encode())
    assert len(B)==len(w) and all(isinstance(x,int) and x>0 for x in w)
    bags=[i for i,x in enumerate(w) for _ in range(x)]
    return {e for e in it.combinations(range(len(bags)),2)
            if bags[e[0]]==bags[e[1]] or B.has_edge(bags[e[0]],bags[e[1]])}


def main(root,out):
    root=Path(root)
    records=json.load(gzip.open(root/'FILTER_TRANSFERS.json.gz','rt'))
    for r in records:
        G=graph(r['g6'],r['w'])
        H=graph('Dhc',list(map(int,r['obstruction_tag'])))
        vm={int(a):b for a,b in r['vertex_map'].items()}
        assert set(vm)==set(range(17)) and len(set(vm.values()))==17
        assert all(0<=b<sum(r['w']) for b in vm.values())
        assert all(tuple(sorted((vm[a],vm[b]))) in G for a,b in H),r['name']
    candidates=[]
    for path in sorted((root/'candidates').glob('*/CANDIDATE.json')):
        r=json.loads(path.read_text())
        w=r['w']; B=nx.from_graph6_bytes(r['g6'].encode()); E=graph(r['g6'],w)
        assert sum(w)==28 and {tuple(e) for e in r['edges']}==E
        assert all(any(B.has_edge(a,b) for a,b in it.combinations(S,2))
                   for S in it.combinations(B.nodes,4)),r['name']
        independent3=next(S for S in it.combinations(B.nodes,3)
                          if all(not B.has_edge(a,b) for a,b in it.combinations(S,2)))
        for size in range(1,len(w)+1):
            for S in it.combinations(B.nodes,size):
                if sum(w[v] for v in S)>=9:
                    assert any(not B.has_edge(a,b) for a,b in it.combinations(S,2)),r['name']
        filt=json.loads(path.with_name('FILTER.json').read_text())
        assert filt['avoids_all'] and len(filt['tests'])==18 and all(not x['contains'] for x in filt['tests'])
        # Independently inspect the full independent-set list used in the counting
        # certificate; a proper colour class contains at most one vertex per bag.
        listed={tuple(S) for S in r['independent_sets']}
        actual={S for k in range(len(w)+1) for S in it.combinations(range(len(w)),k)
                if all(not B.has_edge(a,b) for a,b in it.combinations(S,2))}
        assert listed==actual and max(map(len,actual))==3
        assert len(E)<=156
        candidates.append({'name':r['name'],'vertices':28,'edges':len(E),'alpha':3,
                           'clique_number_at_most':8,'chromatic_lower':10,
                           'example_independent_base_triple':independent3})
    result={'verdict':'PASS','explicit_obstruction_maps_checked':len(records),
            'candidate_counting_certificates':candidates,
            'negative_containment_scope':'18 frozen S025 C5 bag-search outcomes; completeness rests on the audited finite bag-assignment algorithm, not this map checker',
            'no_new_biplanar_witness':True}
    Path(out).write_text(json.dumps(result,indent=1))
    print(json.dumps({'verdict':'PASS','maps':len(records),'candidates':len(candidates)}))


if __name__=='__main__':main(*sys.argv[1:3])
