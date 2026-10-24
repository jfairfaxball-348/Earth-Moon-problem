"""Fresh native/protocol/oracle acceptance; controls are not headline results."""
import gzip
import itertools as it
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import networkx as nx
from s045_search import EXE,atomic,colour_cnf,colouring,env,instance,run_slice,sha
from s045_verify import check_pair,check_colouring,geometric_journal,partition_clause

def main():
    assert json.loads((ROOT/'validation/S045/watchdog_repair/SMOKE.json').read_text())['verdict']=='PASS'
    out=ROOT/'artifacts/tmp/S045'/(sys.argv[1] if len(sys.argv)>1 else 'controls');out.mkdir(parents=True,exist_ok=False)
    assert not (ROOT/'validation/S045/watchdog_repair/CONTROLS.json').exists()
    started=time.monotonic();rows=[]
    def fixed(n,layers,name,expected):
        dest=out/name;dest.mkdir(exist_ok=False)
        pairs=instance(dest/'BASE.inst',n,fixed=layers)
        p=subprocess.run([str(EXE),str(dest/'BASE.inst'),str(dest/'RULES.lem'),'5',str(dest/'STOP'),'0','partition'],
                         input='STOP\n',text=True,capture_output=True,env=env(),timeout=15)
        (dest/'NATIVE.log').write_text(p.stdout+p.stderr,encoding='utf-8')
        assert p.returncode==(0 if expected else 20),(name,p.returncode,p.stdout,p.stderr)
        cuts=geometric_journal(dest/'RULES.lem',n)
        if expected:
            line=next(x for x in p.stdout.splitlines() if x.startswith('CAND '));bits=line.split()[2]
            actual=[[list(e) for i,e in enumerate(pairs) if bits[2*i+j]=='1'] for j in (0,1)]
            assert actual==[list(map(list,ls)) for ls in layers]
            rotations=[]
            for ls in layers:
                g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(ls)
                ok,emb=nx.check_planarity(g);assert ok;rotations.append(emb.get_data())
            check_pair(n,layers,rotations)
        else: assert cuts>0
        return dict(name=name,returncode=p.returncode,cuts=cuts,expected_planar=expected)
    pairs=list(it.combinations(range(5),2))
    for mask in range(1024):
        layers=[[e for i,e in enumerate(pairs) if mask>>i&1],[]]
        rows.append(fixed(5,layers,f'n5-{mask:04d}',mask!=1023))
    rows.append(fixed(6,[list(it.product(range(3),range(3,6))),[]],'K33',False))
    pos=json.loads((ROOT/'validation/S030/POSITIVE24.json').read_text())
    layers=[sorted(tuple(sorted(e)) for e in pos[k]) for k in ('E1','E2')]
    rows.append(fixed(50,layers,'positive24-padded50',True))
    answer,cols=colouring(50,layers,9);assert answer is True;check_colouring(50,layers,cols,9)
    # Reject malformed feedback even though a valid model was returned first.
    d=out/'bad-feedback';d.mkdir();instance(d/'BASE.inst',4)
    p=subprocess.run([str(EXE),str(d/'BASE.inst'),str(d/'RULES.lem'),'5',str(d/'STOP'),'0','partition'],
                     input='COLOR 3 0 0 0 99\n',text=True,capture_output=True,env=env(),timeout=15)
    assert p.returncode==3 and 'bad colour vector' in p.stderr
    # Reject a truncated checkpoint before search.
    (d/'bad.lem').write_text('-1 -3',encoding='ascii')
    p=subprocess.run([str(EXE),str(d/'BASE.inst'),str(d/'bad.lem'),'5',str(d/'STOP'),'0','partition'],
                     input='STOP\n',text=True,capture_output=True,env=env(),timeout=15)
    assert p.returncode==3 and 'invalid geometric checkpoint' in p.stderr
    # Exhaustively check the target implication of every 3-colouring partition
    # on every labelled four-vertex graph, using brute force, independently of SAT.
    ps=list(it.combinations(range(4),2));tested=0
    partitions=list(it.product(range(3),repeat=4))
    for mask in range(64):
        edges=[e for i,e in enumerate(ps) if mask>>i&1]
        colourable=any(all(cs[a]!=cs[b] for a,b in edges) for cs in partitions)
        for cs in partitions:
            clause=partition_clause(4,cs)
            holds=any(mask>>((v-1)//2)&1 for v in clause)
            if not colourable:assert holds
            if all(cs[a]!=cs[b] for a,b in edges):assert not holds
            tested+=1
    # Actual chromatic SAT/UNSAT and standalone native DRAT round trip.
    k4=[list(it.combinations(range(4),2)),[]]
    assert colouring(4,k4,4)[0] is True and colouring(4,k4,3)[0] is False
    cnf=out/'K4-non3.cnf';clauses=colour_cnf(4,k4,3)
    cnf.write_text(f'p cnf 12 {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses),encoding='ascii')
    proof=out/'K4-non3.drat'
    p=subprocess.run([str(ROOT/'artifacts/tmp/S004/cadical.exe'),'-q','--no-binary',str(cnf),str(proof)],
                     text=True,capture_output=True,env=env(),timeout=30)
    assert p.returncode==20
    checked=subprocess.run([str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'),str(cnf),str(proof)],
                           text=True,capture_output=True,timeout=30)
    assert checked.returncode==0 and 's VERIFIED' in checked.stdout
    for p in (cnf,proof):
        with gzip.open(ROOT/'validation/S045/watchdog_repair'/(p.name+'.gz'),'wb') as f:f.write(p.read_bytes())
    # End-to-end feedback finds a tiny non-three-colourable candidate; independent
    # brute-force verifies its alert. This is NOT an Earth-Moon witness.
    result=run_slice(out/'incremental',4,3,10)
    alert=json.loads((out/'incremental/ALERT.json').read_text())
    assert result['reason']=='NONCOLOUR_ALERT_UNVERIFIED' and alert['colouring_result'] is False
    es=alert['layers'][0]+alert['layers'][1]
    assert all(any(cs[a]==cs[b] for a,b in es) for cs in it.product(range(3),repeat=4))
    # Explicit cooperative STOP on a genuine active 50-vertex feedback run.
    d=out/'stop-test';d.mkdir()
    timer=threading.Timer(2,lambda:(d/'STOP').touch());timer.start()
    try: stopped=run_slice(d,50,9,30)
    finally: timer.cancel()
    assert stopped['state']=='STOPPED' and stopped['reason']=='STOP_FILE' and stopped['native_returncode']==0
    extra_cuts=geometric_journal(d/'PLANARITY.lem',50)
    summary=dict(stop_test_geometric_cuts=extra_cuts,status='PASS',fixed_layer_cases=len(rows),exhaustive_n5=1024,rows=rows,
                 partition_truth_table_cases=tested,padded50_positive=True,malformed_feedback_rejected=True,
                 truncated_checkpoint_rejected=True,standalone_drat_verified=True,incremental_feedback=True,
                 cooperative_stop=True,wall_seconds=time.monotonic()-started,
                 proof_sha256=sha(proof),cnf_sha256=sha(cnf),stop_test=stopped)
    atomic(ROOT/'validation/S045/watchdog_repair/CONTROLS.json',summary)
    print('S045 watchdog native acceptance controls PASS',flush=True)

if __name__=='__main__':main()
