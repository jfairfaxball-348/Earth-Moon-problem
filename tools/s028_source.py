#!/usr/bin/env python3
"""S028 rerun of the S027 learned-obstruction source (CAM-0035), same seed/profiles.

Differences from tools/s027_source.py (copied, then edited; S027 bytes untouched):
  * all certified obstructions (S025/S026 + S027 + S028 descent, via
    EMP_S027_EXTRA_OBSTRUCTIONS) are filters and preload sources;
  * every S027 PRELOAD/CONTAIN record of the same profile is re-applied as PRELOAD
    (its map is re-validated on its support with the same capacities);
  * known S027/S028 survivor graphs (EMP_S028_KNOWN, base edge sets) are blocked as
    KNOWN_SURVIVOR blocks before generation, so admission seeks NEW graphs.
Original S027 docstring follows.
S027 learned-obstruction source (CAM-0032). Heuristic generator, exact filters.

Domain per fixed profile w (28 vertices): base graphs B on len(w) labelled
vertices with no independent 4-set (alpha(B[w])<=3, hence chi>=ceil(28/3)=10), no
clique of weight>=9 (K9-free), and at most 156=2(3*28-6) blow-up edges.
Learned clauses (all sound for this profile, see tools/s027_contain.py):
  PRELOAD   S026 checked obstruction maps whose bag usage fits w;
  CONTAIN   in-loop certified-obstruction maps found on generated models;
  EULER     a set T of whole bags whose selected base edges already give the
            blow-up on T more than 6|T|-12 edges (Euler for each planar layer);
  *_PERM    images of any of the above under weight-preserving relabellings.
Only admitted / unknown models receive a plain blocking clause. A generator
UNSAT is a finite profile-domain statement only after native DRAT and after
every blocking clause is itself justified. Caps are UNKNOWN, not exhaustion.
"""
import gzip
import itertools as it
import json
import os
from pathlib import Path
import random
import sys
import time

import networkx as nx
import numpy as np
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from blowup_graph import blowup                       # noqa: E402
from s027_contain import (encode, decode, explicit_map, support, usage,   # noqa: E402
                          weight_perms, load_obstructions)
from s026_supervision import atomic_json              # noqa: E402

SEED = 270018  # unchanged from S027 (registered)
MODELS, PROFILE_SECONDS, SOURCE_SECONDS, MAX_ADMITTED = 100, 180, 7200, 6
PERMS_PER_CLAUSE = 32
CONTAIN_BUDGET = 20000
GEN_BUDGET = 200000
EULER = 156


def profiles(seed=SEED):
    """Same scheme as S026 (balanced per order; random for n<=11), new seed."""
    out, rng = [], random.Random(seed)
    for n in range(9, 15):
        ws = {tuple(sorted([28 // n + 1] * (28 % n) + [28 // n] * (n - 28 % n), reverse=True))}
        if n <= 11:
            while len(ws) < 9:
                cuts = sorted(rng.sample(range(1, 28), n - 1))
                w = [b - a for a, b in zip([0] + cuts, cuts + [28])]
                if max(w) <= 7:
                    ws.add(tuple(sorted(w, reverse=True)))
        out.extend((n, list(w)) for w in sorted(ws))
    return out


def base_clauses(n, w, pairs, idx):
    var = lambda a, b: idx[(min(a, b), max(a, b))]
    cls = [[var(a, b) for a, b in it.combinations(S, 2)] for S in it.combinations(range(n), 4)]
    for k in range(2, n + 1):
        for S in it.combinations(range(n), k):
            t = sum(w[v] for v in S)
            if t >= 9 and all(t - w[v] < 9 for v in S):
                cls.append([-var(a, b) for a, b in it.combinations(S, 2)])
    top, units = len(pairs), []
    for (a, b), x in idx.items():
        for _ in range(w[a] * w[b]):
            top += 1
            cls += [[-x, top], [x, -top]]
            units.append(top)
    card = CardEnc.atmost(units, EULER - sum(x * (x - 1) // 2 for x in w), top_id=top,
                          encoding=EncType.seqcounter)
    return cls + card.clauses, card.nv


def euler_violation(n, w, E):
    """Smallest-index whole-bag set T with blow-up edges on T > 6|T|_w - 12."""
    W = np.zeros(1 << n, dtype=np.int64)
    e = np.zeros(1 << n, dtype=np.int64)
    nb = [0] * n
    for a, b in E:
        nb[a] |= 1 << b
        nb[b] |= 1 << a
    for v in range(n):
        lo, hi = 1 << v, 1 << (v + 1)
        rest = np.arange(0, lo, dtype=np.int64)
        W[lo:hi] = W[rest] + w[v]
        # weight of N(v) within rest
        sel = rest & nb[v]
        e[lo:hi] = e[rest] + w[v] * (w[v] - 1) // 2 + w[v] * W[sel]
    bad = np.nonzero((W >= 3) & (e > 6 * W - 12))[0]
    if len(bad) == 0:
        return None
    m = int(bad[np.argmin(W[bad])])
    T = [v for v in range(n) if m >> v & 1]
    WT = int(W[m])
    inside = sum(w[v] * (w[v] - 1) // 2 for v in T)
    chosen, total = [], inside
    for a, b in sorted((e for e in E if m >> e[0] & 1 and m >> e[1] & 1),
                       key=lambda e: (-w[e[0]] * w[e[1]], e)):
        chosen.append((a, b))
        total += w[a] * w[b]
        if total > 6 * WT - 12:
            return {'T': T, 'weight': WT, 'edges': chosen, 'count': total, 'bound': 6 * WT - 12}
    raise AssertionError('inconsistent Euler violation')


def preload(n, w):
    """S026 checked transfer maps plus S027 learned maps of the same profile."""
    out = preload_s026(n, w)
    for p in sorted((ROOT / 'validation/S027/local/source').glob('profile*/LEARNED.json.gz')):
        d = json.load(gzip.open(p, 'rt'))
        if d['n'] == n and d['w'] == w:
            for L in d['learned']:
                if L['kind'] in ('PRELOAD', 'CONTAIN'):
                    out.append(('S027:' + p.parent.name, L['obstruction'], L['f']))
    return out


def preload_s026(n, w):
    """S026 checked transfer maps (original profiles) that fit capacity w."""
    out = []
    rows = json.load(gzip.open(ROOT / 'validation/S026/source/FILTER_TRANSFERS.json.gz', 'rt'))
    summ = json.loads((ROOT / 'validation/S026/SUMMARY.json').read_text())
    cand = {r['name']: r for r in json.loads((ROOT / 'validation/S026/source/SUMMARY.json').read_text())['candidates']
            if r.get('name')}
    for t in summ['candidate_transfers']:
        c = cand[t['candidate']]
        rows.append({'name': t['candidate'], 'g6': c['g6'], 'w': c['w'],
                     'obstruction_tag': t['obstruction'], 'vertex_map': t['vertex_map']})
    for r in rows:
        if len(r['w']) != n:
            continue
        start = [sum(r['w'][:b]) for b in range(n)]
        bag_of = lambda x: max(b for b in range(n) if start[b] <= x)
        f = [bag_of(int(r['vertex_map'][str(v)])) for v in range(17)]
        if all(c <= w[b] for b, c in enumerate(usage(None, f, n))):
            out.append((r['name'], 'C5-' + r['obstruction_tag'], f))
    return out


def known_survivors(n, w):
    import os
    p = os.environ.get('EMP_S028_KNOWN')
    if not p or not Path(p).is_file():
        return []
    return [r for r in json.loads(Path(p).read_text()) if r['w'] == w and len(w) == n]


class Profile:
    def __init__(self, no, n, w, obstructions, log):
        self.no, self.n, self.w = no, n, w
        self.pairs = list(it.combinations(range(n), 2))
        random.Random(SEED + n).shuffle(self.pairs)
        self.idx = {e: i + 1 for i, e in enumerate(self.pairs)}
        self.base, self.top = base_clauses(n, w, self.pairs, self.idx)
        self.learned, self.blocks = [], []
        self.keys = set()
        self.rng = random.Random(SEED * 31 + no)
        self.obs = obstructions
        self.log = log

    def clause(self, edges):
        return [-self.idx[(min(a, b), max(a, b))] for a, b in edges]

    def learn(self, kind, edges, record, solver):
        """Add a learned clause and its weight-preserving images; return count."""
        added = 0
        for p in [None] + weight_perms(self.w, PERMS_PER_CLAUSE, self.rng):
            img = sorted((min(p[a], p[b]), max(p[a], p[b])) if p else (a, b) for a, b in edges)
            key = frozenset(img)
            if key in self.keys:
                continue
            self.keys.add(key)
            self.learned.append({'kind': kind + ('_PERM' if p else ''), 'edges': img,
                                 'perm': p, 'source_edges': edges, **record})
            solver.add_clause(self.clause(img))
            added += 1
        return added


def contain_solvers(P):
    out = []
    for H in P.obs:
        cls, top, x, kinds = encode(H, P.w, pairs=P.pairs)
        s = Solver(name='cadical195', bootstrap_with=cls)
        out.append((H, s, x))
    return out


def run(out, seconds=SOURCE_SECONDS):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    obs = load_obstructions()
    summary = {'seed': SEED, 'universe': 'labelled SAT models; no completeness claim',
               'caps': {'models_per_profile': MODELS, 'profile_seconds': PROFILE_SECONDS,
                        'source_seconds': seconds, 'max_admitted': MAX_ADMITTED,
                        'perms_per_clause': PERMS_PER_CLAUSE, 'generator_conflicts': GEN_BUDGET,
                        'admission': 'first filter-clean model per profile while fewer than 6 admitted; others SURPLUS_FILTER_CLEAN', 'contain_conflicts': CONTAIN_BUDGET},
               'obstructions': [[H['name'], H['n'], len(H['edges']), H['certificate']] for H in obs],
               'profiles': [], 'admitted': [], 'filter_unknown': [], 'surplus_filter_clean': []}
    global_start = time.monotonic()
    admitted = 0
    for no, (n, w) in enumerate(profiles()):
        d = out / f'profile{no:02d}'
        d.mkdir(exist_ok=True)
        P = Profile(no, n, w, obs, None)
        st = {'profile': no, 'nbase': n, 'weights': w, 'models': 0, 'contain': 0, 'euler': 0,
              'cut': 0, 'unknown': 0, 'admitted': 0, 'closed_k6': 0, 'preload_maps': 0,
              'learned_clauses': 0, 'models_by_obstruction': {}}
        summary['profiles'].append(st)
        start = time.monotonic()
        if time.monotonic() - global_start >= seconds:
            st['stop'] = 'NOT_RUN_SOURCE_CAP'
            atomic_json(out / 'SUMMARY.json', summary)
            continue
        cs = contain_solvers(P)
        with Solver(name='cadical195', bootstrap_with=P.base) as gen:
            for name, hname, f in preload(n, w):
                H = next(h for h in obs if h['name'] == hname)
                S = support(H, f)
                explicit_map(H, w, f, S)       # map valid using ONLY its support
                st['preload_maps'] += 1
                P.learn('PRELOAD', S, {'obstruction': hname, 'f': f, 'from': name}, gen)
            for H in obs:                       # whole-profile obstructions, identity bags
                if len(H['u']) == n and all(a <= b for a, b in zip(H['u'], w)):
                    f = list(H['hbag'])
                    S = support(H, f)
                    explicit_map(H, w, f, S)
                    st['preload_maps'] += 1
                    P.learn('PRELOAD', S, {'obstruction': H['name'], 'f': f, 'from': 'identity'}, gen)
            for k in known_survivors(n, w):
                P.blocks.append({'name': k['name'], 'edges': k['edges'], 'kind': 'KNOWN_SURVIVOR'})
                Ek = set(map(tuple, k['edges']))
                gen.add_clause([-P.idx[e] if e in Ek else P.idx[e] for e in P.pairs])
                st['known_blocked'] = st.get('known_blocked', 0) + 1
            for model_no in range(MODELS):
                if (time.monotonic() - start > PROFILE_SECONDS or
                        time.monotonic() - global_start > seconds):
                    st['stop'] = 'REGISTERED_CAP'
                    break
                gen.conf_budget(GEN_BUDGET)
                ans = gen.solve_limited()
                if ans is None:
                    st['stop'] = 'CONFLICT_CAP_UNKNOWN'
                    break
                if ans is False:
                    st['stop'] = 'GENERATOR_UNSAT'
                    break
                m = set(x for x in gen.get_model() if x > 0)
                E = sorted(e for e in P.pairs if P.idx[e] in m)
                st['models'] += 1
                ev = euler_violation(n, w, E)
                if ev:
                    st['euler'] += 1
                    P.learn('EULER', ev['edges'], {'T': ev['T'], 'count': ev['count'], 'bound': ev['bound']}, gen)
                    continue
                found, unknown = None, False
                Eset = set(E)
                assume = [P.idx[e] if e in Eset else -P.idx[e] for e in P.pairs]
                for H, s, x in cs:
                    s.conf_budget(CONTAIN_BUDGET)
                    r = s.solve_limited(assumptions=assume)
                    if r is True:
                        f = decode(H, w, set(v for v in s.get_model() if v > 0), x)
                        explicit_map(H, w, f, E)
                        S = support(H, f)
                        explicit_map(H, w, f, S)
                        found = (H, f, S)
                        break
                    if r is None:
                        unknown = True
                if found:
                    H, f, S = found
                    st['contain'] += 1
                    st['models_by_obstruction'][H['name']] = st['models_by_obstruction'].get(H['name'], 0) + 1
                    P.learn('CONTAIN', S, {'obstruction': H['name'], 'f': f, 'model': model_no}, gen)
                    continue
                B = nx.Graph()
                B.add_nodes_from(range(n))
                B.add_edges_from(E)
                g6 = nx.to_graph6_bytes(B, header=False).decode().strip()
                es, _ = blowup(g6, w)
                assert len(es) <= EULER
                maxcut = max(sum(w[a] * w[b] for a, b in E if ((bits >> a) ^ (bits >> b)) & 1)
                             for bits in range(1 << (n - 1)))
                name = f'P{no:02d}-B{n}-{model_no:04d}'
                rec = {'name': name, 'g6': g6, 'w': w, 'maxcut': maxcut, 'edges': len(es),
                       'profile': no, 'base_edges': E}
                P.blocks.append({'name': name, 'edges': E})
                gen.add_clause([-P.idx[e] if e in Eset else P.idx[e] for e in P.pairs])
                if maxcut > 4 * 28 - 8:
                    st['cut'] += 1
                    rec['status'] = 'CUT_DENSITY'
                    continue
                if unknown:
                    st['unknown'] += 1
                    rec['status'] = 'FILTER_UNKNOWN'
                    summary['filter_unknown'].append(rec)
                    atomic_json(d / f'{name}.json', rec)
                    continue
                omega = max(sum(w[v] for v in C) for C in nx.find_cliques(B))
                assert omega <= 8
                if sum(w[v] for v in B if B.degree(v) == n - 1) >= 6:
                    st['closed_k6'] += 1
                    rec['status'] = 'CLOSED_UNIVERSAL_K6_SOURCE'
                    continue
                indep = max(len(S) for k in range(1, 5) for S in it.combinations(range(n), k)
                            if all(not B.has_edge(a, b) for a, b in it.combinations(S, 2)))
                assert indep <= 3
                rec.update(omega=omega, alpha=indep, chromatic_lower=10, num_vertices=28)
                if st['admitted'] or admitted >= MAX_ADMITTED:
                    rec['status'] = 'SURPLUS_FILTER_CLEAN'
                    st['surplus'] = st.get('surplus', 0) + 1
                    summary['surplus_filter_clean'].append(rec)
                    continue
                rec['status'] = 'ADMITTED'
                st['admitted'] += 1
                admitted += 1
                summary['admitted'].append(rec)
                cdir = out / 'candidates' / name
                cdir.mkdir(parents=True, exist_ok=True)
                atomic_json(cdir / 'CANDIDATE.json', rec)
                (cdir / 'graph.edges').write_text(''.join(f'{a} {b}\n' for a, b in es), newline='\n')
            else:
                st['stop'] = 'MODEL_CAP'
        for _, s, _ in cs:
            s.delete()
        st['learned_clauses'] = len(P.learned)
        st['seconds'] = round(time.monotonic() - start, 2)
        with gzip.open(d / 'LEARNED.json.gz', 'wt', compresslevel=9) as g:
            json.dump({'profile': no, 'n': n, 'w': w, 'pairs': P.pairs, 'learned': P.learned,
                       'blocks': P.blocks}, g)
        if st.get('stop') == 'GENERATOR_UNSAT':
            cls = P.base + [P.clause(L['edges']) for L in P.learned] + \
                [[-P.idx[e] if e in set(map(tuple, b['edges'])) else P.idx[e] for e in P.pairs]
                 for b in P.blocks]
            nv = max([P.top] + [abs(l) for c in cls for l in c])
            (d / 'domain.cnf').write_text(f'p cnf {nv} {len(cls)}\n' + ''.join(
                ' '.join(map(str, c)) + ' 0\n' for c in cls), newline='\n')
            st['domain_cnf'] = str((d / 'domain.cnf').relative_to(out))
            st['domain_blocking_dependencies'] = [b['name'] for b in P.blocks]
        atomic_json(out / 'SUMMARY.json', summary)
        print(json.dumps({k: v for k, v in st.items() if k != 'models_by_obstruction'}), flush=True)
    summary['seconds'] = round(time.monotonic() - global_start, 2)
    atomic_json(out / 'SUMMARY.json', summary)


if __name__ == '__main__':
    run(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else SOURCE_SECONDS)
