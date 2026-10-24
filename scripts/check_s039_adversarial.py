"""Falsification controls for malformed S039 certificates; finite and read-only."""
import copy
import json
from pathlib import Path
from check_s039_records import read, rotation, faces_normal, star_replay

ROOT = Path(__file__).resolve().parents[1]


def main():
    r = read('validation/S039/neighborhood-155.json')
    data = read(r['source'])['best']
    cert = next(c for c in read('validation/S038/PAIR_CHECKS.json')['rows'] if c['path'] == r['source'] and c['pointer'] == ['best'])
    move = r['best']['move']
    k = move['layer']
    faces = faces_normal(rotation(28, data[('E1', 'E2')[k]], cert['layers'][k]['rotation']))
    star_replay(faces, move)
    bad = []
    for name in ('repeated_rim', 'interior_on_rim', 'wrong_degree', 'wrong_deficit', 'missing_face', 'nonface_target', 'missing_effect', 'fake_chord'):
        m = copy.deepcopy(move)
        if name == 'repeated_rim': m['boundary'][1] = m['boundary'][0]
        elif name == 'interior_on_rim': m['boundary'][0] = m['vertex']
        elif name == 'wrong_degree': m['old_degree'] = 2
        elif name == 'wrong_deficit': m['quad_incident'] = not m['quad_incident']
        elif name == 'missing_face': m['selected_faces'].pop()
        elif name == 'nonface_target': m['target'] = [0, 1, m['vertex']]
        elif name == 'missing_effect': m['removed'].pop()
        elif name == 'fake_chord': m['hole_diagonals'].append([0, 1])
        try:
            star_replay(faces, m)
        except (AssertionError, ValueError, IndexError):
            bad.append(name)
        else:
            raise AssertionError('Accepted malformed certificate: '+name)
    print('S039 adversarial PASS:', len(bad), 'malformed certificates rejected')
    return dict(status='PASS', rejected=bad, valid_control=True)


if __name__ == '__main__':
    import sys
    result = main()
    if '--record' in sys.argv:
        (ROOT/'validation/S039/ADVERSARIAL_CHECKS.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
