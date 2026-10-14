"""One fresh process per counter representation; prevent TreeCardEnc import leakage."""
import json, sys
from pathlib import Path
from biplanar_cnf import read_edges

kind,ef,prefix,out=sys.argv[1:]
if kind=='Cover':
    from triangulation_cover import Cover as Klass
elif kind=='TreeFullCover':
    from s008_tree import TreeFullCover as Klass
elif kind=='HeavyCover':
    from s009_heavy_cover import HeavyCover as Klass
else:raise ValueError(kind)
d=json.loads(Path(prefix+'.cuts.json').read_text())
c=Klass(read_edges(ef),d['lex'],d.get('short_links',False))
if 'static' in d:assert c.static==d['static']
c.cuts=d['cuts'];c.write_cnf(Path(out))
print('PASS regenerated',kind,len(c.cuts),'cuts',flush=True)
