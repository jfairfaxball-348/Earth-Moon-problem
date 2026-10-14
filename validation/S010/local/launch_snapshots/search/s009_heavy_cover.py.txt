"""Full necessary tree cover with ALL completion K3,3 subgraphs (small n only)."""
import itertools,json,sys,time
from pathlib import Path
from s008_tree import TreeFullCover
from biplanar_cnf import read_edges

def completion_k33(n):
    for six in itertools.combinations(range(n),6):
        for tail in itertools.combinations(six[1:],2):
            a=(six[0],)+tail;b=tuple(v for v in six if v not in a)
            yield tuple(sorted(tuple(sorted((u,v))) for u in a for v in b))

class HeavyCover(TreeFullCover):
    def __init__(self,edges,lex=False,short_links=False):
        super().__init__(edges,lex,short_links)
        assert self.n<=12
        count=0
        for es in completion_k33(self.n):
            for i in range(2):self.base.append([-self.E(i,*e) for e in es])
            count+=1
        self.static.update(s009_version='all-completion-K33-v1',completion_K33_count=count)

if __name__=='__main__':
    if sys.argv[1]=='check':
        _,_,ef,prefix=sys.argv
        d=json.loads(Path(prefix+'.cuts.json').read_text())
        c=HeavyCover(read_edges(ef),d['lex'],d.get('short_links',False))
        assert c.static==d['static'];c.cuts=d['cuts']
        c.write_cnf(Path(prefix+'.regenerated.cnf'))
        assert Path(prefix+'.cnf').read_bytes()==Path(prefix+'.regenerated.cnf').read_bytes()
        print('PASS S009 heavy cold LF CNF/cuts regeneration')
    else:
        _,ef,prefix,seconds,*flags=sys.argv
        c=HeavyCover(read_edges(ef),'--lex' in flags)
        c.save(prefix,'INITIALISED',0,time.monotonic());c.write_cnf(Path(prefix+'.initial.cnf'))
        print(json.dumps(c.static),flush=True)
        print(json.dumps(c.run(prefix,float(seconds))),flush=True)
