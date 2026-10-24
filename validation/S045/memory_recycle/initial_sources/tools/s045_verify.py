"""Independent stdlib checks for S045 external rules and planar rotations."""
import itertools as it
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from s037_certificates import subdivision

def check_colouring(n,layers,colours,k):
    assert len(colours)==n and all(type(c)==int and 0<=c<k for c in colours)
    assert all(colours[a]!=colours[b] for ls in layers for a,b in ls)

def partition_clause(n,colours):
    assert len(colours)==n and all(type(c)==int and c>=0 for c in colours)
    return [2*i+1+j for i,(a,b) in enumerate(it.combinations(range(n),2)) if colours[a]==colours[b] for j in (0,1)]

def check_pair(n,layers,rotations):
    assert len(layers)==len(rotations)==2
    sets=[]
    for ls,data in zip(layers,rotations):
        es=set(map(tuple,ls));sets.append(es)
        assert len(es)==len(ls) and all(type(a)==type(b)==int and 0<=a<b<n for a,b in es)
        rot={int(v):list(ns) for v,ns in data.items()}
        assert set(rot)==set(range(n))
        adj={v:set() for v in range(n)}
        for a,b in es: adj[a].add(b);adj[b].add(a)
        assert all(len(rot[v])==len(adj[v]) and set(rot[v])==adj[v] for v in range(n))
        unseen=set(range(n))
        while unseen:
            root=min(unseen);vs=set();todo=[root]
            while todo:
                v=todo.pop()
                if v not in vs:vs.add(v);todo.extend(adj[v]-vs)
            unseen-=vs
            if len(vs)==1: assert not adj[root];continue
            darts={(a,b) for a in vs for b in adj[a]};seen=set();faces=0
            for first in darts:
                if first in seen:continue
                faces+=1;dart=first
                while dart not in seen:
                    seen.add(dart);a,b=dart
                    ns=rot[b];dart=(b,ns[(ns.index(a)-1)%len(ns)])
                assert dart==first
            assert seen==darts and len(vs)-len(darts)//2+faces==2
    assert not sets[0]&sets[1]

def geometric_journal(path,n,cancel=None):
    path=Path(path)
    if not path.exists():return 0
    pairs=list(it.combinations(range(n),2));count=0
    with path.open(encoding='ascii') as f:
        for index,line in enumerate(f):
            if cancel and index%1024==0:cancel()
            assert line.endswith('\n'),'incomplete geometric journal'
            xs=list(map(int,line.split()));assert xs and xs[-1]==0
            xs=xs[:-1]
            assert xs and len(xs)==len(set(xs)) and all(-2*len(pairs)<=x<0 for x in xs)
            assert len({(-x-1)%2 for x in xs})==1
            subdivision([pairs[(-x-1)//2] for x in xs]);count+=1
    return count
