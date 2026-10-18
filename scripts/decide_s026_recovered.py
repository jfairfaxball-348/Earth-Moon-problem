"""Registered fifth candidate stage for recovered P29; one heavy local tree."""
import ctypes,hashlib,itertools as it,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'artifacts/tmp/S026-filter-recovery'
os.environ.update(EMP_S026_OUTPUT=str(OUT),EMP_S026_MEMORY_KIB=str(11*1024*1024),EMP_CADICAL=str(ROOT/'artifacts/tmp/S004/cadical.exe'),EMP_DRAT_TRIM=str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'))
from s026_supervision import atomic_json,run_step
from s026_check_source import graph
from s026_campaign import exact
from s025_check import check_split
import networkx as nx
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert read(OUT/'SUMMARY.json')['verdict']=='AVOIDS_ALL_CERTIFIED_REQUIRES_CANDIDATE_STAGE'
 import msvcrt
 lock=(ROOT/'artifacts/tmp/S026-local/RUN.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
 d=OUT/'candidate';d.mkdir(exist_ok=True)
 try:
  paths=[p for pattern in ['s025_*.py','s026_*.py','biplanar_cegar.py','biplanar_cnf.py','blowup_graph.py'] for p in (ROOT/'tools').glob(pattern)]+[Path(__file__)]
  atomic_json(d/'SOURCE.json',dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256={str(p.relative_to(ROOT)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}))
  def run(args,cap,name):return run_step(args,cap,d/name,OUT/'RUN_JOURNAL.jsonl',memory_kib=11*1024*1024)
  smoke=run([sys.executable,str(ROOT/'scripts/cloud_smoke.py')],2400,'smoke.log');assert smoke['returncode']==0
  shutil.copyfile(ROOT/'artifacts/tmp/cloud_smoke/RESULT.json',d/'SMOKE.json');assert read(d/'SMOKE.json')['verdict']=='PASS'
  r=read(OUT/'SUMMARY.json')['candidate'];E=graph(r['g6'],r['w']);n=sum(r['w'])
  assert n==28 and max(max(e) for e in E)==27
  assert not any(all(tuple(sorted(e)) not in E for e in it.combinations(S,2)) for S in it.combinations(range(n),4))
  triples=[list(S) for S in it.combinations(range(n),3) if all(tuple(sorted(e)) not in E for e in it.combinations(S,2))]
  assert triples
  G=nx.Graph();G.add_nodes_from(range(n));G.add_edges_from(E);omega=max(map(len,nx.find_cliques(G)));assert omega<=8
  B=nx.from_graph6_bytes(r['g6'].encode());assert sum(r['w'][v] for v in B if B.degree(v)==len(B)-1)<6
  r.update(n=n,m=len(E),alpha=3,all_independent_triples=triples,no_independent_quadruple_checked=True,clique_number=omega,chromatic_lower=10)
  atomic_json(d/'CANDIDATE.json',r)
  edge=d/'graph.edges';edge.write_text(''.join(f'{u} {v}\n' for u,v in sorted(E)),newline='\n')
  report={'candidate':r['name'],'chromatic_lower':10,'alpha_certificate_checked':True,'anneals':[]}
  for seed in [1,2]:
   step=run([sys.executable,str(ROOT/'tools/s025_cover_anneal.py'),str(edge),str(seed),'60',str(d/f'anneal{seed}.json')],75,f'anneal{seed}.log')
   ar=read(d/f'anneal{seed}.json') if (d/f'anneal{seed}.json').exists() else {}
   report['anneals'].append(dict(seed=seed,process=step,best_uncovered=ar.get('best_uncovered')))
   if ar.get('best_uncovered')==0:
    check_split(n,sorted(E),ar['E1'],ar['E2']);report['biplanar_split_checked']=True
  report['exact']=exact(edge,d,300)
  report['verdict']='BIPLANAR_CHI_GE10_CHECKED' if report.get('biplanar_split_checked') or report['exact']['verdict']=='BIPLANAR_CHECKED' else report['exact']['verdict']
  atomic_json(OUT/'CANDIDATE_STAGE.json',report);print(json.dumps(report),flush=True)
 finally:
  ctypes.windll.kernel32.SetThreadExecutionState(0x80000000);lock.close()
if __name__=='__main__':main()
