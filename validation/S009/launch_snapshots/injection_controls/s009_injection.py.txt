"""Arbitrary edge-preserving labelled injection search; bounded misses stay UNKNOWN."""
import itertools,time

def adjacency(n,edges):
    a=[set() for _ in range(n)]
    for u,v in edges:a[u].add(v);a[v].add(u)
    return a

def injection(ns,es,nt,et,deadline):
    a=adjacency(ns,es);b=adjacency(nt,et)
    if ns>nt or len(es)>len(et):return dict(verdict='FILTERED_ORDER_EDGE',nodes=0)
    domains=[{v for v in range(nt) if len(b[v])>=len(a[u])} for u in range(ns)]
    if any(not d for d in domains):return dict(verdict='FILTERED_DEGREE',nodes=0)
    nodes=0
    def visit(mapping,ds):
        nonlocal nodes
        nodes+=1
        if time.monotonic()>deadline:raise TimeoutError
        if len(mapping)==ns:return dict(mapping)
        u=min((u for u in range(ns) if u not in mapping),key=lambda u:(len(ds[u]),-len(a[u]),u))
        for v in sorted(ds[u]):
            nd=[set(d) for d in ds];ok=True
            for w in range(ns):
                if w in mapping or w==u:continue
                nd[w].discard(v)
                if w in a[u]:nd[w]&=b[v]
                if not nd[w]:ok=False;break
            if not ok:continue
            mapping[u]=v
            result=visit(mapping,nd)
            if result is not None:return result
            del mapping[u]
        return None
    try:
        m=visit({},domains)
        return dict(verdict='VERIFIED_MAP' if m is not None else 'EXHAUSTED_NO_MAP',mapping=m,nodes=nodes)
    except TimeoutError:return dict(verdict='PAIR_CAP_UNKNOWN',nodes=nodes)

def controls():
    graphs=[]
    for n in range(1,4):
        pairs=list(itertools.combinations(range(n),2))
        for mask in range(1<<len(pairs)):graphs.append((n,[e for j,e in enumerate(pairs) if mask>>j&1]))
    count=0
    for ns,es in graphs:
        for nt,et in graphs:
            target=set(et);expected=False
            for perm in itertools.permutations(range(nt),ns):
                if all(tuple(sorted((perm[u],perm[v]))) in target for u,v in es):expected=True;break
            got=injection(ns,es,nt,et,time.monotonic()+10)
            assert (got['verdict']=='VERIFIED_MAP')==expected,(ns,es,nt,et,got)
            assert got['verdict']!='PAIR_CAP_UNKNOWN';count+=1
    es=list(itertools.combinations(range(3),2));et=es+[(0,3)]
    split=injection(3,es,4,et,time.monotonic()+10)
    assert split['verdict']=='VERIFIED_MAP'
    # Closed twins 1,2 of target and vertex0 form two bags; a source K3 bag crosses them.
    assert set(split['mapping'].values())=={0,1,2}
    return dict(exhaustive_graph_orders=[1,3],graph_pairs=count,brute_permutation_agreement=True,
                cross_twin_bag_control=split,symmetry='NONE',verdict='PASS')
