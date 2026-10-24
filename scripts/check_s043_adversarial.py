"""S043 checker falsification controls; does not search for graphs."""
import copy
import itertools as it

from check_s043_records import read, expected_base, check_subdivision, check_rotation


def rejected(function):
    try:
        function()
    except (AssertionError, KeyError, ValueError, StopIteration):
        return
    raise AssertionError('invalid certificate accepted')


def main():
    enc = read('ENCODING.json')
    expected_base(enc)
    for field in ('orbits', 'fours', 'generators', 'triangles'):
        bad = copy.deepcopy(enc)
        if field == 'orbits':
            bad[field][0][0][1] = 27
        elif field == 'fours':
            bad[field].pop()
        elif field == 'generators':
            bad[field][0]['image'][0] = 252
        else:
            bad[field].reverse()
        rejected(lambda: expected_base(bad))
    k5 = [list(e) for e in it.combinations(range(5), 2)]
    k33 = [[a, b] for a in range(3) for b in range(3, 6)]
    assert check_subdivision(k5) == 'K5' and check_subdivision(k33) == 'K33'
    for es in (k5, k33):
        rejected(lambda: check_subdivision(es[:-1]))
        rejected(lambda: check_subdivision(es+[es[0]]))
        # A disjoint cycle cannot hide in a subdivision certificate.
        rejected(lambda: check_subdivision(es+[[20, 21], [21, 22], [20, 22]]))
    layer = read('CONTROLS.json')['planar_layer']
    check_rotation(layer['edges'], layer['rotation'])
    bad = copy.deepcopy(layer['rotation'])
    bad['0'][0] = bad['0'][1]
    rejected(lambda: check_rotation(layer['edges'], bad))
    print('S043 adversarial PASS: orbit/four-set/generator/pin corruption; deleted/duplicate/disconnected subdivision edges; invalid rotation rejected')


if __name__ == '__main__':
    main()
