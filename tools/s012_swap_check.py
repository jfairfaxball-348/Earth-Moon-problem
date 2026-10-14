#!/usr/bin/env python3
"""S012 independent verification: NetworkX-based expansion, new colour permutations, all pairs."""
import gzip,json,os
from pathlib import Path
import networkx as nx
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
ROWS=[2,55,59,61,199,200]
def check():
    corpus=json.loads(Path("validation/S003/survivors_alpha_ge3.json").read_text())
    summary=json.loads(Path("artifacts/tmp/S012/swap_audit.json").read_text())
    with gzip.open("validation/S011/edge_critical_witnesses.json.gz","rt") as f: archive=json.load(f)
    assert summary["campaign"]=="CAM-0015" and [r["row"] for r in summary["rows"]]==ROWS
    a={r["index"]:r for r in archive["rows"]}
    verified=0
    for row in summary["rows"]:
        idx=row["row"]
        code,weights=corpus[idx][:2]
        g=nx.from_graph6_bytes(code.encode())
        groups=[[v for v in range(sum(weights[:i]),sum(weights[:i+1]))] for i in range(len(weights))]
        bag={v:i for i,G in enumerate(groups) for v in G}
        E=set()
        for G in groups:
            E.update((u,v) for u in G for v in G if u<v)
        for i,j in g.edges():
            E.update(tuple(sorted((u,v))) for u in groups[i] for v in groups[j])
        n=sum(weights)
        nonedge=[(u,v) for u in range(n) for v in range(u+1,n) if (u,v) not in E]
        assert len(E)==row["m"] and n==row["n"] and len(nonedge)==row["nonedges"]
        stored={tuple(w["edge"]):w["colors"] for w in a[idx]["witnesses"]}
        assert set(stored)==E
        recolour=separate=0
        for e,c in stored.items():
            assert len(c)==n and all(type(v)==int and 0<=v<9 for v in c)
            assert all(c[u]!=c[v] for u,v in E if (u,v)!=e)
            for f in nonedge:
                cc=list(c)
                if cc[f[0]]==cc[f[1]]:
                    eligible=next(z for z in f if bag[z]!=bag[e[0]] and bag[z]!=bag[e[1]])
                    alt=next(y for y in groups[bag[eligible]] if y!=eligible and c[y]!=c[eligible])
                    cc[eligible],cc[alt]=cc[alt],cc[eligible]
                    recolour+=1
                else: separate+=1
                assert cc[f[0]]!=cc[f[1]]
                assert all(cc[u]!=cc[v] for u,v in E if (u,v)!=e)
                verified+=1
        assert recolour==row["recoloured_pairs"] and separate==row["already_separated"]
        assert recolour+separate==row["all_pairs"]
    assert verified==summary["total_swap_pairs"]
    report={"verdict":"PASS","all_swaps_independently_nine_colourable":verified,
      "scope":"six fixed labelled rows, not the complete 271 pool or other constructions"}
    Path("artifacts/tmp/S012/swap_check.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)
if __name__=="__main__": check()
