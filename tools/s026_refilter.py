#!/usr/bin/env python3
"""Re-test one frozen S026 candidate against newly certified local C5s.

Called externally with a registered wall/memory cap. A found map is independently
expanded/edge checked; no output or a cap is UNKNOWN, never containment absence.
"""
import json
from pathlib import Path
import sys
import networkx as nx
from s025_transfer import find_map,explicit_check


def main(candidate,local,out):
    r=json.loads(Path(candidate).read_text())
    B=nx.from_graph6_bytes(r['g6'].encode()); H=nx.from_graph6_bytes(b'Dhc')
    tests=[]
    for p in sorted(Path(local).glob('C5-*/SUMMARY.json')):
        cert=json.loads(p.read_text())
        if cert.get('verdict')!='NONBIPLANAR_CERTIFIED' or not cert.get('proof',{}).get('certified'):
            continue
        tag=p.parent.name[3:]; u=list(map(int,tag))
        assignment=find_map(H,u,B,r['w'])
        test={'tag':tag,'contains':assignment is not None}
        tests.append(test)
        if assignment is not None:
            vm=explicit_check('Dhc',u,r['g6'],r['w'],assignment)
            result={'candidate':r['name'],'verdict':'NONBIPLANAR_BY_NEW_CERTIFIED_SUBGRAPH',
                    'tag':tag,'vertex_map':vm,'tests':tests}
            Path(out).write_text(json.dumps(result,indent=1));print(json.dumps(result));return
    result={'candidate':r['name'],'verdict':'NO_NEW_C5_MAP_IN_COMPLETED_TESTS','tests':tests}
    Path(out).write_text(json.dumps(result,indent=1));print(json.dumps(result))


if __name__=='__main__':main(*sys.argv[1:4])
