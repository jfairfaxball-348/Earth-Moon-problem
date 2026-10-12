import copy
import json
from pathlib import Path
import unittest
from tools.check_rotation import check, check_file

ROOT = Path(__file__).resolve().parents[1]


class TestConcreteCertificates(unittest.TestCase):
    def test_sulanke_structure_and_rotations(self):
        path = ROOT / 'validation/sulanke.json'
        result = check_file(path)
        self.assertEqual([r['edges'] for r in result['layers']], [26, 24])
        self.assertEqual(result['proper_colouring_uses'], 9)
        d = json.loads(path.read_text())
        es = set(map(tuple, d['edges_part1']+d['edges_part2']))
        self.assertEqual({(a,b) for a in range(6) for b in range(a+1,6)},
                         {e for e in es if e[1]<6})
        self.assertTrue(all((a,b) in es for a in range(6) for b in range(6,11)))
        cycle = d['cycle_order']
        self.assertEqual({tuple(sorted((cycle[i],cycle[(i+1)%5]))) for i in range(5)},
                         {e for e in es if e[0]>=6})

    def test_minimum_degree11_witness(self):
        path = ROOT / 'validation/degree11_witness.json'
        result = check_file(path)
        self.assertEqual([r['faces'] for r in result['layers']], [80,80])
        d = json.loads(path.read_text())
        degree = [0]*42
        for u,v in d['edges_part1']+d['edges_part2']:
            degree[u]+=1; degree[v]+=1
        self.assertEqual(sorted(degree),[11]*24+[12]*18)
        p = d['permutation']
        self.assertEqual(sorted(p),list(range(42)))
        self.assertTrue(all(p[v]>=12 for v in range(12)))
        self.assertEqual(sorted(tuple(sorted((p[u],p[v]))) for u,v in d['edges_part1']),
                         list(map(tuple,d['edges_part2'])))

    def test_corrupt_rotation_rejected(self):
        d = json.loads((ROOT/'validation/degree11_witness.json').read_text())
        rotation = copy.deepcopy(d['rotations'][0])
        rotation['0'][0] = rotation['0'][1]
        with self.assertRaises(AssertionError):
            check(42,d['edges_part1'],rotation)

    def test_genus_corruption_rejected(self):
        d = json.loads((ROOT/'validation/degree11_witness.json').read_text())
        rotation = copy.deepcopy(d['rotations'][0])
        rotation['0'][0],rotation['0'][1] = rotation['0'][1],rotation['0'][0]
        with self.assertRaises(AssertionError):
            check(42,d['edges_part1'],rotation)

    def test_wrong_graph_rejected(self):
        d = json.loads((ROOT/'validation/sulanke.json').read_text())
        with self.assertRaises(AssertionError):
            check(11,d['edges_part1'][:-1],d['rotations'][0])


if __name__=='__main__':
    unittest.main()
