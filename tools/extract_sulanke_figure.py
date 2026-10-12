"""CAM-0001: recover source Figure 3 vectors; independently check output.

Usage: python tools/extract_sulanke_figure.py /path/to/ThicknessTwo.pdf
Requires PyMuPDF and NetworkX. Only this specific 2007 author PDF is supported.
The graph certificate is checked separately by the stdlib rotation checker.
"""
import json
import math
import sys
from pathlib import Path
import fitz
import networkx as nx


def extract(path):
    document = fitz.open(path)
    page = document[5]
    labels = [[], []]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                text = span['text'].strip()
                x0,y0,x1,y1 = span['bbox']
                if text.isdigit() and 475 < y0 < 556:
                    labels[0 if x0 < 310 else 1].append((int(text)-1, ((x0+x1)/2,(y0+y1)/2)))
    layers, positions = [[], []], [{}, {}]
    for drawing in page.get_drawings():
        if (drawing['type']=='s' and len(drawing['items'])==1
                and drawing['items'][0][0]=='l' and 475<drawing['rect'].y0<556):
            _,a,b = drawing['items'][0]
            layer, ends = (0 if a.x<310 else 1), []
            for point in (a,b):
                v,xy = min(labels[layer],key=lambda item:(point.x-item[1][0])**2+(point.y-item[1][1])**2)
                assert math.dist((point.x,point.y),xy)<2
                positions[layer][str(v)]=[point.x,point.y]
                ends.append(v)
            layers[layer].append(tuple(sorted(ends)))
    e1,e2 = map(set,layers)
    assert len(e1)==26 and len(e2)==24 and not e1&e2
    graph=nx.Graph();graph.add_edges_from(e1|e2)
    assert graph.subgraph(range(6)).number_of_edges()==15
    assert all(graph.has_edge(a,b) for a in range(6) for b in range(6,11))
    cycle=graph.subgraph(range(6,11))
    assert nx.is_connected(cycle) and all(d==2 for _,d in cycle.degree)
    rotations=[]
    for i,edges in enumerate((e1,e2)):
        rotations.append({str(v):sorted([w for w in graph.nodes if tuple(sorted((v,w))) in edges],
                          key=lambda w:math.atan2(positions[i][str(w)][1]-positions[i][str(v)][1],
                                                 positions[i][str(w)][0]-positions[i][str(v)][0]))
                          for v in range(11)})
    cycle_order=nx.cycle_basis(cycle)[0]
    colors=list(range(6))+[None]*5
    for i,v in enumerate(cycle_order):
        colors[v]=6+i%2 if i<4 else 8
    result={'num_vertices':11,'edges_part1':sorted(e1),'edges_part2':sorted(e2),
            'coloring':colors,'chromatic_number':9,'rotations':rotations,
            'source':'SRC-0002 author preprint Figure 3, PDF page 6',
            'source_positions':positions,'cycle_order':cycle_order}
    document.close()
    return result


if __name__=='__main__':
    result=extract(sys.argv[1])
    target=Path(__file__).resolve().parents[1]/'validation/sulanke.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(target)
