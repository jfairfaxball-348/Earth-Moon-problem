"""Falsification controls for malformed S040 coordinated-pair certificates; finite and read-only."""
import copy
import json
from pathlib import Path
from check_s038_records import patch_replay
from check_s039_records import read, star_replay
from check_s040_records import pair_replay
from replay_s040_neighborhoods import load

ROOT = Path(__file__).resolve().parents[1]


def main():
    rec = read('validation/S040/neighborhood-155.json')
    edges, faces, _ = load(rec['source'])
    move = rec['bests']['type2']['move']
    pair_replay([list(f) for f in faces], move)
    core = read('validation/sulanke.json')
    other = read('validation/S040/neighborhood-156.json')['bests']['type1']['move']
    bad = []
    for name in ('dropped_conflict', 'extra_conflict', 'wrong_type', 'swapped_layers', 'foreign_component',
                 'duplicate_addition', 'missing_effect', 'fake_target'):
        m = copy.deepcopy(move)
        c0, c1 = m['components']
        if name == 'dropped_conflict': c0['conflicts'] = []
        elif name == 'extra_conflict': c1['conflicts'].append([0, 1])
        elif name == 'wrong_type': m['type'] = 1
        elif name == 'swapped_layers': m['components'] = [c1, c0]
        elif name == 'foreign_component': m['components'][1] = other['components'][1]
        elif name == 'duplicate_addition': c1['added'].append(c0['added'][0])
        elif name == 'missing_effect': c0['removed'].pop()
        elif name == 'fake_target': c1['target'] = [0, 1, c1['vertex']]
        try:
            pair_replay([list(f) for f in faces], m)
        except (AssertionError, ValueError, IndexError, KeyError, StopIteration):
            bad.append(name)
        else:
            raise AssertionError('Accepted malformed pair certificate: '+name)
    protected = [set(map(tuple, core[k])) for k in ('edges_part1', 'edges_part2')]
    arm = read('validation/S040/arms/protected-4010-coord.json')
    pair = next(m for m in arm['trace'] if m['kind'] == 'pair')
    p_edges, p_faces, _ = load(arm['source'])
    fake = [set(protected[0]) | set(map(tuple, pair['components'][0]['removed'])), protected[1]]
    fs = [list(f) for f in p_faces]
    for m in arm['trace'][:pair['step']]:
        if m['kind'] == 'pair':
            fs = pair_replay(fs, m, protected)
        elif m['kind'] == 'star':
            fs[m['layer']] = star_replay(fs[m['layer']], m)
        else:
            fs[m['layer']] = patch_replay(fs[m['layer']], m)
    pair_replay(fs, pair, protected)
    try:
        pair_replay(fs, pair, fake)
    except AssertionError:
        bad.append('protected_core_removal')
    else:
        raise AssertionError('Accepted removal of a protected core edge')
    print('S040 adversarial PASS:', len(bad), 'malformed pair certificates rejected')
    return dict(status='PASS', rejected=bad, valid_control=True)


if __name__ == '__main__':
    import sys
    result = main()
    if '--record' in sys.argv:
        (ROOT/'validation/S040/ADVERSARIAL_CHECKS.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
