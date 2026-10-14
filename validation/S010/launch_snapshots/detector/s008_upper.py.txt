"""CAM-0009 finite support and availability controls, not a universal theorem."""
import itertools
import json
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
import sys


def main():
    rows=[]
    # One canonical representative for each overlap cardinality, not graph census.
    for overlap in range(5):
        a=set(range(4));b=set(range(overlap))|set(range(4,8-overlap))
        assert len(a)==len(b)==4 and len(a&b)==overlap
        union=sorted(a|b);offset=len(union)
        t1=list(range(offset,offset+7));t2=list(range(offset+7,offset+14))
        es=set(itertools.combinations(t1,2))|set(itertools.combinations(t2,2))
        es|={tuple(sorted((u,v))) for core,boundary in ((t1,a),(t2,b)) for u in core for v in boundary}
        n=offset+14;m=len(es)
        assert m==98 and n==22-overlap
        rows.append(dict(overlap=overlap,n=n,m=m,euler_bound=6*n-12,
            verdict='NON_BIPLANAR_EULER' if m>6*n-12 else 'UNKNOWN',
            edges=sorted(es),cores=[t1,t2],boundaries=[sorted(a),sorted(b)]))
    sets=[{i for i in range(3) if mask>>i&1} for mask in range(8)]
    count=0;sat=0;bad=None
    for availability in itertools.product(sets,repeat=3):
        count+=1
        direct=any(all(p[i] in availability[i] for i in range(3)) for p in itertools.permutations(range(3)))
        hall=all(len(set.union(*(availability[i] for i in subset)))>=len(subset)
            for size in range(1,4) for subset in itertools.combinations(range(3),size))
        assert direct==hall
        sat+=int(direct)
        if availability==({0,1},{0,1},{0,1}):
            assert not direct
            bad=dict(availability=[sorted(s) for s in availability],
                pairwise_distinct_assignments=True,simultaneous_distinct_assignment=False)
    assert count==512 and bad
    Path('validation/S008/upper_controls.json').write_text(json.dumps(dict(
        support_pairs=rows,availability_domain=512,distinct_assignment_cases=sat,
        failed_pairwise_inference=bad),indent=1)+'\n',newline='\n')
    print('PASS5 support-overlap controls;512 availability triples;',sat,'matchings')


if __name__=='__main__':
    Path('validation/S008/upper_launch_hashes.json').write_text(json.dumps({
        p:sha(p) for p in ('tools/s008_upper.py','tools/s005_search.py')},indent=1)+'\n',newline='\n')
    main()
