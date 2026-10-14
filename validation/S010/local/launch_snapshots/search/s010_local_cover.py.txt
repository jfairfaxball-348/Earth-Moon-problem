"""Necessary small-order full sphere model; totalizer/all-completion K5 and K33."""
import itertools, json, sys, time
from pathlib import Path
import s008_tree  # patches counters only within this dedicated process
from triangulation_cover import Cover
from biplanar_cnf import read_edges
from s009_heavy_cover import completion_k33

class LocalCover(Cover):
    def __init__(self,edges,lex=False,short_links=False):
        super().__init__(edges,lex,short_links);assert self.n<=14
        k5=k33=0
        for vs in itertools.combinations(range(self.n),5):
            es=list(itertools.combinations(vs,2))
            for i in range(2):self.base.append([-self.E(i,*e) for e in es])
            k5+=1
        for es in completion_k33(self.n):
            for i in range(2):self.base.append([-self.E(i,*e) for e in es])
            k33+=1
        self.static=dict(version='S010-small-all-completion-v1',counter='totalizer',K5=k5,K33=k33,
                         subset_cuts='NONE',distinct_faces_enabled=False)

if __name__=='__main__':
    if sys.argv[1]=='check':
        _,_,ef,prefix=sys.argv;d=json.loads(Path(prefix+'.cuts.json').read_text())
        c=LocalCover(read_edges(ef),d['lex'],d.get('short_links',False));c.cuts=d['cuts']
        c.write_cnf(Path(prefix+'.regenerated.cnf'))
        assert Path(prefix+'.cnf').read_bytes()==Path(prefix+'.regenerated.cnf').read_bytes()
        print('PASS LocalCover cold LF CNF/cuts')
    else:
        _,ef,prefix,seconds,*flags=sys.argv;c=LocalCover(read_edges(ef),'--lex' in flags)
        c.write_cnf(Path(prefix+'.initial.cnf'));print(c.static,flush=True)
        print(json.dumps(c.run(prefix,float(seconds))),flush=True)
