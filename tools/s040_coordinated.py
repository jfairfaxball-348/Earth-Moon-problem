"""S040 coordinated one-star-per-layer relocations with provisional conflicts.

A component is an S039 degree3..6 simple-disk star relocation in ONE layer,
generated without the opposite-layer filter. Its conflicts C=A&other must be
removed by the other layer's component. Compatibility of components a (layer0)
and b (layer1), with removed R, added A and conflicts C:
    C_a <= R_b,  C_b <= R_a,  A_a & A_b = empty.
Type0: both conflict-free (pairing two S039 neighbors); type1: exactly one
component has conflicts; type2: both do. No global completeness claim.
"""
import itertools as it
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s038_patch import Plane, boundary, canonical, covered, fillings, universe
from s037_certificates import rotation

N = 28
FOURS = 20475
PAIRS = list(it.combinations(range(N), 2))
INDEX = {e: i for i, e in enumerate(PAIRS)}


def emask(edges):
    m = 0
    for e in edges:
        m |= 1 << INDEX[tuple(e)]
    return m


def words(x, n):
    return np.frombuffer(x.to_bytes(8*n, 'little'), dtype='<u8')


def load_pair(path, pointer=('best',), checks='validation/S039/PAIR_CHECKS.json'):
    data = json.loads((ROOT/path).read_text())
    for key in pointer:
        data = data[key]
    row = next(r for r in json.loads((ROOT/checks).read_text())['rows']
               if r['path'] == path and r['pointer'] == list(pointer))
    planes = [Plane(N, rotation(N, data[key], row['layers'][i]['rotation'])) for i, key in enumerate(('E1', 'E2'))]
    return planes, data


def relaxed_stars(plane, cover, protected=frozenset(), degree_cap=6):
    """Distinct (removed, added) effects of degree3..6 star relocations in one layer."""
    effects = {}
    for v in range(plane.n):
        spokes = {e for e in plane.edges if v in e}
        d = len(spokes)
        if not 3 <= d <= degree_cap or spokes & protected:
            continue
        selected = [i for i, face in enumerate(plane.faces) if v in face]
        old_faces = [plane.faces[i] for i in selected]
        if len(selected) != d:
            continue
        rim = boundary(old_faces)
        q = sum(len(f) == 4 for f in old_faces)
        if rim is None or v in rim or q > 1 or len(rim) != d+q:
            continue
        if {v} | set(rim) != set().union(*map(set, old_faces)):
            continue
        chosen = set(selected)
        outside_faces = [f for i, f in enumerate(plane.faces) if i not in chosen]
        outside_edges = plane.edges-spokes
        base_cov = covered(outside_edges, cover)
        for ds, fs in fillings(rim, bool(q)):
            if len(ds) != d-3 or ds & outside_edges:
                continue
            filled = sorted(outside_faces+list(fs))
            hole_cov = base_cov | covered(ds, cover)
            for target in filled:
                if len(target) != 3:
                    continue
                new_spokes = {tuple(sorted((v, w))) for w in target}
                new_edges = outside_edges | ds | new_spokes
                if new_edges == plane.edges:
                    continue
                removed, added = plane.edges-new_edges, new_edges-plane.edges
                key = frozenset(removed), frozenset(added)
                if key in effects:
                    continue
                effects[key] = dict(
                    move=dict(kind='star', vertex=v, old_degree=d, selected_faces=selected, boundary=rim,
                              quad_incident=bool(q), hole_diagonals=sorted(ds), hole_filling=fs, target=target,
                              target_inside_hole=(target in fs), removed=sorted(removed), added=sorted(added)),
                    target=target, filled=filled, cov=hole_cov | covered(new_spokes, cover))
    return effects


def faces_after(plane, effect):
    move, target = effect['move'], effect['target']
    v = move['vertex']
    return [f for f in effect['filled'] if f != target]+[canonical((v, a, b)) for a, b in zip(target, target[1:]+target[:1])]


class Table:
    """Per-layer component table with numpy edge/four-set masks."""

    def __init__(self, plane, other_edges, cover, protected=frozenset()):
        effects = relaxed_stars(plane, cover, protected)
        self.plane = plane
        self.keys = sorted(effects, key=lambda k: (sorted(k[0]), sorted(k[1])))
        self.index = {k: i for i, k in enumerate(self.keys)}
        self.effects = [effects[k] for k in self.keys]
        other = emask(other_edges)
        rs = [emask(k[0]) for k in self.keys]
        ads = [emask(k[1]) for k in self.keys]
        self.R = np.array([words(x, 6) for x in rs]).reshape(-1, 6)
        self.A = np.array([words(x, 6) for x in ads]).reshape(-1, 6)
        self.C = np.array([words(x & other, 6) for x in ads]).reshape(-1, 6)
        self.P = np.array([words(e['cov'], 320) for e in self.effects]).reshape(-1, 320)
        self.conflicted = self.C.any(1)
        self.size = len(self.keys)


def single_scores(table, other_cov):
    """S039-legal single components (no conflict); score = I4 after the move."""
    q = words(other_cov, 320)
    legal = np.nonzero(~table.conflicted)[0]
    covered_count = np.bitwise_count(table.P[legal] | q).sum(1, dtype=np.int64)
    return legal, FOURS-covered_count


def pair_scores(t0, t1, types=(0, 1, 2)):
    """Every compatible (component0, component1) pair, with type and exact I4 score."""
    out_i, out_j, out_t, out_s = [], [], [], []
    want = np.zeros(3, dtype=bool)
    want[list(types)] = True
    for i in range(t0.size):
        ok = ~((t0.C[i] & ~t1.R).any(1))
        ok &= ~((t1.C & ~t0.R[i]).any(1))
        ok &= ~((t0.A[i] & t1.A).any(1))
        kind = np.where(t1.conflicted, 1, 0)+int(t0.conflicted[i])
        ok &= want[kind]
        J = np.nonzero(ok)[0]
        if not J.size:
            continue
        cov = np.bitwise_count(t0.P[i] | t1.P[J]).sum(1, dtype=np.int64)
        out_i.append(np.full(J.size, i, dtype=np.int32)); out_j.append(J.astype(np.int32))
        out_t.append(kind[J].astype(np.int8)); out_s.append((FOURS-cov).astype(np.int32))
    if not out_i:
        e = np.zeros(0, dtype=np.int32)
        return e, e, e.astype(np.int8), e
    return np.concatenate(out_i), np.concatenate(out_j), np.concatenate(out_t), np.concatenate(out_s)


def score_of(edges0, edges1, cover, full):
    return (full ^ covered(set(edges0) | set(edges1), cover)).bit_count()
