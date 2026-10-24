"""Falsification controls for S041 certificates; finite, stdlib, read-only."""
import copy
import gzip
import json
from pathlib import Path
from check_s041_records import check_certificate, rotation, z13_orbits

ROOT = Path(__file__).resolve().parents[1]


def main():
    orb = z13_orbits()
    layers = json.loads(gzip.decompress((ROOT/'validation/S041/P1_Z13_layers.json.gz').read_bytes()))
    edges_of = lambda r: set().union(*(orb[n] for n in r['orbits']))
    planar = next(r for r in layers if r['planar'])
    pe = edges_of(planar)
    adj = {v: set() for v in range(28)}
    for a, b in pe:
        adj[a].add(b); adj[b].add(a)
    kur = next(r for r in layers if not r['planar'] and r['certificate']['test'] == 'KURATOWSKI')
    ke = edges_of(kur)
    outside = next(e for e in sorted(set().union(*orb.values())) if e not in ke)
    controls = {
        'T1_on_degree_ge3': (pe, dict(test='T1', vertex=0)),
        'T2_on_edge_in_two_triangles': (pe, dict(test='T2', edge=list(sorted(pe)[0]))),
        'T3_degree_on_planar_link': (pe, dict(test='T3_degree', vertex=0, neighbour=min(adj[0]))),
        'T3_connected_full_link': (pe, dict(test='T3_connected', vertex=0, component=sorted(adj[0]))),
        'kuratowski_foreign_edge': (ke, dict(kur['certificate'], edges=kur['certificate']['edges'][1:]+[list(outside)])),
        'kuratowski_wrong_kind': (ke, dict(kur['certificate'], kind='K5' if kur['certificate']['kind'] == 'K33' else 'K33')),
        'kuratowski_on_planar_layer': (pe, kur['certificate']),
        'unknown_test': (pe, dict(test='T9')),
    }
    rejected = []
    for name, (es, cert) in controls.items():
        try:
            check_certificate(es, cert)
        except (AssertionError, KeyError, ValueError, StopIteration):
            rejected.append(name)
        else:
            raise AssertionError('accepted malformed certificate: '+name)
    rot = copy.deepcopy(planar['rotation'])
    v = next(iter(rot))
    rot[v] = rot[v][1:]+rot[v][:1] if len(rot[v]) < 3 else [rot[v][0], rot[v][2], rot[v][1]]+rot[v][3:]
    try:
        faces = rotation(28, sorted(pe), rot)
        assert len(faces) == 52 and all(len(f) == 3 for f in faces)
    except AssertionError:
        rejected.append('corrupted_rotation')
    else:
        raise AssertionError('accepted corrupted rotation')
    print('S041 adversarial PASS:', len(rejected), 'malformed certificates rejected')
    return dict(status='PASS', rejected=rejected)


if __name__ == '__main__':
    import sys
    result = main()
    if '--record' in sys.argv:
        (ROOT/'validation/S041/ADVERSARIAL_CHECKS.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
