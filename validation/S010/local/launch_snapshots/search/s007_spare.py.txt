#!/usr/bin/env python3
"""CAM-0008 B: finite exhaustive challenge to spare-colour recolouring."""
import itertools
from s007_run import ROOT,save
from s005_replay import sha


def proper(es,col):return all(col[a]!=col[b] for a,b in es)


def main():
    save(ROOT/'spare_launch_hashes.json',{'tools/s007_spare.py':sha('tools/s007_spare.py')})
    counts=[]
    for n in range(2,6):
        pairs=list(itertools.combinations(range(n),2));proper_count=0;challenges=0
        for mask in range(1<<len(pairs)):
            es=[e for j,e in enumerate(pairs) if mask>>j&1];adj=[set() for _ in range(n)]
            for a,b in es:adj[a].add(b);adj[b].add(a)
            nonedges=[e for j,e in enumerate(pairs) if not (mask>>j&1)]
            for col in itertools.product(range(3),repeat=n):
                if not proper(es,col):continue
                proper_count+=1
                for a,b in nonedges:
                    new=list(col)
                    if col[a]!=col[b]:
                        for v in adj[a]:
                            if col[v]==col[b]:new[v]=3
                        assert proper(es,new)
                        new[a]=col[b]
                    assert proper(es,new) and new[a]==new[b]
                    challenges+=1
        counts.append(dict(n=n,all_labelled_graphs=1<<len(pairs),proper_three_colouring_assignments=proper_count,
            nonadjacent_pair_challenges=challenges))
    es=[(0,v) for v in range(1,5)]+[(1,2),(2,3),(3,4)]
    all_col=[list(c) for c in itertools.product(range(3),repeat=5) if proper(es,c)]
    assert all_col and all(c[1]!=c[4] for c in all_col)
    spare=[3,0,1,2,0];assert proper(es,spare) and spare[1]==spare[4]
    save(ROOT/'spare_controls.json',dict(domain=counts,triangle_fan=dict(V=list(range(5)),edges=es,
        every_proper_three_colouring=all_col,nonadjacent_pair=[1,4],forced_distinct_without_spare=True,
        proper_four_colouring_with_equal_pair=spare),scope='Finite corroboration; hand proof is all-order; no12-critical witness'))
    print('PASS finite spare-colour challenges and no-spare planar triangle-fan obstruction')


if __name__=='__main__':main()
