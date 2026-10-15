#!/usr/bin/env python3
"""S017: exact original-edge CEGAR plus Euler-cardinality constraints.

Fresh sequential-counter process ONLY; never import s008_tree (F045).
SAT only after independent layers check; UNSAT console output alone is NOT
a certified nonbiplanarity result. This is not a complete search when capped.
"""
import itertools
import json
import pathlib
import sys
from pysat.card import CardEnc, EncType
from pysat.solvers import Minisat22
from biplanar_cegar import Cegar
from biplanar_cnf import read_edges
import networkx as nx

def bounds(n, m):
    cap = 3*n-6
    return max(0,m-cap), min(m,cap)

def counter_clauses(m, low, high, first_id):
    assert 0 <= low <= high <= m
    top = first_id
    result = []
    for kind, k in [('atleast',low),('atmost',high)]:
        # Do not call PySAT for vacuous constraints: some CardEnc versions
        # return an empty CNF with nv=0 instead of preserving top_id.
        if (kind == 'atleast' and k == 0) or (kind == 'atmost' and k == m):
            continue
        part = getattr(CardEnc,kind)(lits=list(range(1,m+1)), bound=k,
                                  top_id=top, encoding=EncType.seqcounter)
        assert part.nv >= top
        result.extend(part.clauses)
        top = part.nv
    assert all(abs(x) <= top for c in result for x in c)
    return result, top

def projected_truth_table():
    """Independently enumerate all edge-bit assignments for each m<=5 and all
    cardinality intervals. Existential SAT over counter auxiliaries MUST equal
    arithmetic membership; no inference from cardinality clauses alone."""
    tests = 0
    for m in range(1,6):
        for low in range(m+1):
            for high in range(low,m+1):
                clauses, nv = counter_clauses(m,low,high,m)
                assert all(abs(lit)<=nv for c in clauses for lit in c)
                with Minisat22(bootstrap_with=clauses) as sol:
                    for bits in itertools.product([False,True],repeat=m):
                        projected = sol.solve(assumptions=[
                            (i+1 if bit else -(i+1)) for i,bit in enumerate(bits)])
                        assert projected == (low <= sum(bits) <= high), (
                            m,low,high,bits,projected)
                        tests+=1
    return tests

class DenseCegar(Cegar):
    def __init__(self, edges, seed=1):
        super().__init__(edges,seed)
        m=len(edges)
        n=1+max(max(e) for e in edges)
        lo,hi=bounds(n,m)
        assert lo<=hi
        start=self.nv
        assert start>=m
        # Bounds on E1 imply bounds on E2, since E2 is the complement.
        # Re-encode BOTH bounds, but not E2 separately.
        clauses, top=counter_clauses(m,lo,hi,start)
        self.base.extend(clauses)
        self.nv=top
        self.density={"n":n,"m":m,"low":lo,"high":hi,
                      "cardinality_clauses":len(clauses),
                      "auxiliary_vars":top-start,
                      "original_lex_top":start}
        assert all(abs(lit)<=self.nv for c in self.base for lit in c)

def run(edgefile, prefix, timeout, seed, limit):
    assert projected_truth_table()>0
    edges=read_edges(edgefile)
    c=DenseCegar(edges,seed=seed)
    c.limit=limit
    outcome,it=c.run(timeout)
    info={"verdict":outcome,"iterations":it,"lemmas":len(c.lemmas),
          "symmetries":len(c.perms),"density":c.density,
          "encoding_truth_table":"PASS",
          "classification":"UNKNOWN_UNLESS_COMPLETE_CHECKED_SPLIT"}
    if outcome=="SAT":
        n=c.density["n"]
        a,b=c.split
        assert len(a)+len(b)==len(edges)
        assert not set(a).intersection(b)
        assert set(a).union(b)==set(edges)
        assert c.density["low"]<=len(a)<=c.density["high"]
        assert nx.check_planarity(nx.Graph(a))[0] and nx.check_planarity(nx.Graph(b))[0]
        pathlib.Path(prefix+".split.json").write_text(
            json.dumps({"n":n,"E1":a,"E2":b},sort_keys=True))
        info["classification"]="PROVISIONAL_SPLIT_NEEDS_INDEPENDENT_CHECKS"
    if outcome=="UNSAT":
        clauses=list(c.base)
        for k in c.lemmas:
            lits=[c.idx[e] for e in k]
            clauses.extend(([-i for i in lits],lits))
        with open(prefix+".cnf","w") as fh:
            fh.write("p cnf %d %d\n" % (c.nv,len(clauses)))
            for clause in clauses:
                fh.write(" ".join(map(str,clause))+" 0\n")
        pathlib.Path(prefix+".lemmas.json").write_text(json.dumps(
            {"edges":edges,"lemmas":c.lemmas,"perms":c.perms,
             "density":c.density},sort_keys=True))
        info["classification"]="UNSAT_UNCERTIFIED_REQUIRES_FRESH_DRAT_AND_INDEPENDENT_AUDIT"
    print(json.dumps(info),flush=True)

if __name__=="__main__":
    run(sys.argv[1],sys.argv[2],float(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]))
