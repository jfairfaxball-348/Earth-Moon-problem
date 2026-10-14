"""Registered complete bipartite detectors and finite adversarial colour controls."""
import itertools, json, math, sys
from pathlib import Path
import networkx as nx
from check_s009_records import labelled, graph6_edges
from check_rotation import check
from s007_run import save

ROOT=Path('validation/S010')

def allocations(w,total,pos=0):
    if pos==len(w):
        if total==0:yield ()
        return
    for x in range(min(w[pos],total)+1):
        for tail in allocations(w,total-x,pos+1):yield (x,)+tail

def bag_max(base,w,a):
    adj={i:{i} for i in range(len(w))}
    for u,v in base:adj[u].add(v);adj[v].add(u)
    best=-1;arg=None;count=0
    for xs in allocations(w,a):
        support=[i for i,x in enumerate(xs) if x]
        common=set.intersection(*(adj[i] for i in support))
        size=sum(w[j]-xs[j] for j in common)
        count+=1
        if size>best:best=size;arg=xs
    return best,arg,count

def explicit_max(n,es,a):
    adj=[set() for _ in range(n)]
    for u,v in es:adj[u].add(v);adj[v].add(u)
    return max((len(set.intersection(*(adj[u] for u in s))-set(s)) for s in itertools.combinations(range(n),a)),default=-1)

def detector():
    comparisons=thresholds=0
    pairs=list(itertools.combinations(range(4),2))
    for mask in range(64):
        base={e for j,e in enumerate(pairs) if mask>>j&1}
        for w in itertools.product((1,2),repeat=4):
            bag=[i for i,x in enumerate(w) for _ in range(x)]
            es={(u,v) for u,v in itertools.combinations(range(len(bag)),2) if bag[u]==bag[v] or tuple(sorted((bag[u],bag[v]))) in base}
            for a in range(1,5):
                b,_,_=bag_max(base,w,a);direct=explicit_max(len(bag),es,a)
                assert b==direct;comparisons+=1
                for threshold in range(1,5):assert (b>=threshold)==(direct>=threshold);thresholds+=1
    sources=((5,13),(6,9),(7,7));rows=[];maps=[]
    corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    for idx,row in enumerate(corpus):
        k,base=graph6_edges(row[0]);w=row[1];n,es=labelled(row)
        offset=list(itertools.accumulate([0]+w));alllabels=set(range(n))
        adj=[set() for _ in range(n)]
        for u,v in es:adj[u].add(v);adj[v].add(u)
        for a,b in sources:
            maximum,xs,count=bag_max(base,w,a)
            entry=dict(index=idx,source=[a,b],max_common=maximum,allocations_checked=count,verdict='EXHAUSTED_NO_MAP')
            if maximum>=b:
                left=[offset[j]+z for j,x in enumerate(xs) for z in range(x)]
                right=sorted(set.intersection(*(adj[v] for v in left))-set(left))[:b]
                assert len(left)==a and len(right)==b and not set(left)&set(right)
                assert all(tuple(sorted((u,v))) in es for u in left for v in right)
                entry.update(verdict='VERIFIED_LABELLED_MAP',left=left,right=right,cross_edges_checked=a*b)
                maps.append(entry)
            rows.append(entry)
    arithmetic=0
    for a,b in itertools.product(range(1,101),repeat=2):
        if a+b<3:continue
        x,y=sorted((a,b));violates=a*b>4*(a+b)-8
        contains=any(x>=p and y>=q for p,q in sources)
        assert violates==contains;arithmetic+=1
    # K2,9 is planar; split into two stars, check each nonisolated component separately.
    edges=[(u,v) for u in (0,1) for v in range(2,11)]
    rotations=[]
    for u in (0,1):
        layer=[e for e in edges if e[0]==u];g=nx.Graph(layer);ok,emb=nx.check_planarity(g);assert ok
        labels=sorted(g.nodes());relabel={v:i for i,v in enumerate(labels)}
        rot={str(relabel[v]):[relabel[t] for t in emb.neighbors_cw_order(v)] for v in labels}
        audit=check(len(labels),[(relabel[a],relabel[b]) for a,b in layer],rot)
        rotations.append(dict(nonisolated_labels=labels,rotation=rot,sphere=audit,isolated_vertex=1-u))
    heavy=json.loads(Path('validation/S007/heavy_search.json').read_text())[1]
    split=heavy['split'];union=set(map(tuple,split['E1']))|set(map(tuple,split['E2']))
    assert not set(map(tuple,split['E1']))&set(map(tuple,split['E2'])) and len(union)==51
    audits=[]
    for key in ('E1','E2'):
        ok,emb=nx.check_planarity(nx.Graph(split[key]));assert ok
        rot={str(v):list(emb.neighbors_cw_order(v)) for v in range(12)}
        audits.append(dict(rotation=rot,sphere=check(12,split[key],rot)))
    save(ROOT/'positive_controls.json',dict(K2I9=dict(V=list(range(11)),E1=[e for e in edges if e[0]==0],
            E2=[e for e in edges if e[0]==1],rotations=rotations,proper2=[0,0]+[1]*9),
            K6I6=dict(split=split,rotations=audits,proper7=heavy['proper_colouring'],clique_lower=heavy['clique_lower']),verdict='PASS'))
    save(ROOT/'bipartite_detector.json',dict(rows=rows,maps=maps,complete_rows=271,source_pairs=sources,
        comparisons=comparisons,threshold_comparisons=thresholds,arithmetic_cases=arithmetic,
        allocation_cases=sum(r['allocations_checked'] for r in rows),verdict='PASS',
        completeness='all bag allocations; actual-edge maps independently checked; misses concern ONLY three sources'))
    print('PASS detector',len(rows),'source-row pairs;',len(maps),'maps;',comparisons,'independent maxima',flush=True)

def upper():
    # Every F of order <=4, and every one/two-set family with a nonadjacent pair in EACH set.
    count=feasible=infeasible=0;first=None;budget_counter=None
    for n in range(1,5):
        pairs=list(itertools.combinations(range(n),2))
        for mask in range(1<<len(pairs)):
            edges={e for i,e in enumerate(pairs) if mask>>i&1}
            sets=[set(i for i in range(n) if bits>>i&1) for bits in range(1,1<<n)]
            sets=[s for s in sets if len(s)>=2 and any(e not in edges for e in itertools.combinations(sorted(s),2))]
            colours=[c for c in itertools.product(range(3),repeat=n) if all(c[a]!=c[b] for a,b in edges)]
            for k in (1,2):
                for ss in itertools.combinations_with_replacement(sets,k):
                    good=[c for c in colours if all(len({c[v] for v in s})<len(s) for s in ss)]
                    count+=1
                    if good:
                        feasible+=1;t=min(len(set(c)) for c in good)
                        if t*(t-1)//2>len(edges)+k and budget_counter is None:budget_counter=dict(n=n,edges=sorted(edges),sets=list(map(sorted,ss)),t=t)
                    else:
                        infeasible+=1
                        if first is None and colours:first=dict(n=n,edges=sorted(edges),sets=list(map(sorted,ss)),
                                                               proper3_colourings=len(colours),grade='ABSTRACT_GRAPH_NOT_CRITICAL_EMP_WITNESS')
    assert first==dict(n=3,edges=[(0,1)],sets=[[0,2],[1,2]],proper3_colourings=18,grade='ABSTRACT_GRAPH_NOT_CRITICAL_EMP_WITNESS'),first
    # A single rainbow-forbidden set can forbid TWO colours at the last vertex.
    partial=[0,1];forbidden=[c for c in range(3) if len(set(partial+[c]))==3]
    # Better: impose SAME-colour pair, rather than nonrainbow three-set.
    assert forbidden==[2]
    # With |S|-1 distinct old colours, EVERY absent old colour is forbidden: 11-colour universe ->9 choices.
    forbidden11=[c for c in range(11) if len({0,1,c})==3];assert len(forbidden11)==9
    save(ROOT/'upper_controls.json',dict(verdict='PASS',instances=count,feasible_proper3=feasible,infeasible_proper3=infeasible,
        first_incompatible_repetition=first,finite_budget_counterexample=budget_counter,
        rainbow_constraint_forbidden_colours=forbidden11,
        domain='all labelled edge graphs n1..4, all one/two eligible set multisets, all proper3 assignments; finite only'))
    print('PASS upper adversarial controls',count,'instances;',infeasible,'infeasible',flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
