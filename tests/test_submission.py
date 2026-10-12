import unittest
from tools.check_submission import validate


class TestPreliminaryCertificateValidation(unittest.TestCase):
    def setUp(self):
        self.sample = {
            "num_vertices": 3,
            "edges_part1": [[0, 1], [1, 2]],
            "edges_part2": [[0, 2]],
            "coloring": [0, 1, 2],
            "chromatic_number": 3,
        }

    def test_well_formed(self):
        result = validate(self.sample)
        self.assertEqual(result["edges"], 3)
        self.assertFalse(result["chromatic_lower_bound_certified"])

    def test_overlap_rejected(self):
        sample = dict(self.sample, edges_part2=[[1, 0]])
        with self.assertRaises(ValueError):
            validate(sample)

    def test_improper_colour_rejected(self):
        sample = dict(self.sample, coloring=[0, 1, 0])
        with self.assertRaises(ValueError):
            validate(sample)

    def test_loops_rejected(self):
        sample = dict(self.sample, edges_part2=[[0, 0]])
        with self.assertRaises(ValueError):
            validate(sample)

    def test_bool_vertex_rejected(self):
        sample = dict(self.sample, edges_part2=[[True, 2]])
        with self.assertRaises(ValueError):
            validate(sample)


if __name__ == "__main__":
    unittest.main()
