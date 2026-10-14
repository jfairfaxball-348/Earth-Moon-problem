#!/usr/bin/env python3
"""CAM-0014 independent, standard-library-only G-e proper 9-colouring checker."""
import json
import sys
from pathlib import Path


TARGETS = [2, 55, 59, 61, 199, 200]


def expand(row):
    code, w = row[0], row[1]
    data = [ord(ch)-63 for ch in code]
    assert data[0] == len(w) and len(w) in (7, 8)
    bits = [((b >> shift) & 1) for b in data[1:] for shift in (5,4,3,2,1,0)]
    base = set()
    t = 0
    for j in range(1, len(w)):
        for i in range(j):
            if bits[t]:
                base.add((i, j))
            t += 1
    bag = [i for i, weight in enumerate(w) for _ in range(weight)]
    edges = {(i,j) for i in range(len(bag)) for j in range(i+1,len(bag))
             if bag[i]==bag[j] or (min(bag[i],bag[j]),max(bag[i],bag[j])) in base}
    return len(bag), sorted(edges)


def verify(path):
    obj = json.loads(Path(path).read_text())
    corpus = json.loads(Path("validation/S003/survivors_alpha_ge3.json").read_text())
    archive = json.loads(Path("validation/S004/chi10_results.json").read_text())
    assert obj["campaign"] == "CAM-0014"
    total = 0
    completed = []
    for record in obj["rows"]:
        i = record["index"]
        assert i in TARGETS and i not in completed
        n, edges = expand(corpus[i])
        assert n == record["n"] and len(edges)==record["m"]
        old = archive[i]["ten_colouring"]
        assert len(old)==n and len(set(old))==10
        assert all(old[u]!=old[v] for u,v in edges)
        witness = record.get("witnesses", [])
        seen = set()
        for item in witness:
            edge = tuple(item["edge"])
            colors = item["colors"]
            assert edge in edges and edge not in seen
            seen.add(edge)
            assert len(colors)==n and all(type(c)==int and 0<=c<9 for c in colors)
            assert colors[edge[0]]==colors[edge[1]], "deleted edge must be monochromatic"
            assert all(colors[u]!=colors[v] for u,v in edges if (u,v)!=edge)
        if record["status"]=="COMPLETE":
            assert len(witness)==len(edges) and seen==set(edges)
            completed.append(i)
        total += len(witness)
    assert len(obj["rows"]) == len(TARGETS)
    assert obj.get("independent_checker_expected_complete",[]) == completed
    return {"verdict":"PASS", "complete_edge_critical_indices":completed,
            "proper_9_colouring_witnesses_checked":total,
            "all_six_complete":completed==TARGETS,
            "claim_scope":"only six fixed labelled graphs; original chi10 lower via separate full cold smoke"}


if __name__ == "__main__":
    result = verify(sys.argv[1])
    path = Path(sys.argv[1]).with_name("edge_critical_check.json")
    path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result,indent=2), flush=True)
