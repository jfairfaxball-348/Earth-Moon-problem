# S002 certificate reproduction

The baseline witness is in sulanke.json; the degeneracy obstruction is in
degree11_witness.json. Both use labels 0..n-1 and explicit edge-disjoint
layers. Every rotation is a cyclic neighbour order; the independent
stdlib checker follows all directed edge/face orbits and requires a
connected orientable embedding with Euler characteristic2. It does not
call NetworkX or a SAT solver.

Run from repository root with Python3.12:

```bash
python scripts/check_scaffold.py
python -m unittest discover -s tests -v
python tools/check_rotation.py validation/sulanke.json
python tools/check_rotation.py validation/degree11_witness.json
```

Optional LR recheck/generation requires NetworkX3.5. Reconstruct the source
Figure3 with PyMuPDF1.26.6,
using the source URL/checksum in S002_MANIFEST.json:

```bash
python tools/extract_sulanke_figure.py /path/to/ThicknessTwo.pdf
python tools/find_degree11_witness.py
python tools/check_submission.py validation/sulanke.json --check-planarity
python tools/check_submission.py validation/degree11_witness.json --check-planarity
```

The source extractor recognizes only the specific2007 author PDF and
derives rotations directly from source coordinates. The other generator
uses the registered fixed-seed/capped CAM-0002 heuristic; only its verified
successful graph supports a claim. A timeout would prove no exclusion.

The42v file's chromatic_number field is retained for compatibility with
the preliminary schema but is explicitly a colouring UPPER bound7.
The exact chromatic number is not asserted. Sulanke's exact chi9 is
proved in research/S002_AMPLIFICATION.md by the join/odd-cycle argument,
independent of the automated checks. No unverified UNSAT assertion.

The formal proof of the rotation checker relies on the standard
rotation-system/surface classification theorem, not a Lean development.
Tests include genuine genus-changing mutation and malformed-rotation
controls. Source PDFs are referenced and hashed, not republished here.
