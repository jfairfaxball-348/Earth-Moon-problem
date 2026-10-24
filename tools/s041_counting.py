"""S041 probe P2: exact necessary-count tables for non-alpha constructions (R3).

Conditional on the Kostochka-Yancey bound (SRC-0011) for k>=4 critical graphs;
odd cycles are the 3-critical graphs; K2/K1 the 2/1-critical ones. A k-critical
graph has k or at least k+2 vertices. Biplanar: e<=6n-12; K_{m,n} biplanar needs
mn<=4(m+n)-8. Integer arithmetic only.
"""
from fractions import Fraction


def ky(k, n):
    """Minimum edges of a k-critical graph on n vertices (lower bound)."""
    if k == 1:
        return 0 if n == 1 else None
    if k == 2:
        return 1 if n == 2 else None
    if k == 3:
        return n if n % 2 and n >= 3 else None
    if n < k or n == k+1:
        return None
    num = (k+1)*(k-2)*n-k*(k-3)
    den = 2*(k-1)
    return -(-num//den)


def budget(n):
    return 6*n-12


def mycielski(limit=4000, levels=20):
    bad = []
    for h in range(9, limit+1):
        e = ky(9, h)
        if e is None:
            continue
        for r in range(1, levels+1):
            n, m = h*(r+1)+1, e*(2*r+1)+h
            if m <= budget(n):
                bad.append((h, r))
    # Algebra for all h: 3*(70h-54)/16+h > 12h-6 iff 34h > 66.
    assert Fraction(3*(70*9-54), 16)+9 > 12*9-6
    return dict(checked_orders=[9, limit], levels=[1, levels], counting_feasible=bad,
                algebra='for r=1: 3e+h >= (226h-162)/16 > 12h-6 = 6(2h+1)-12 iff 34h > 66; r>1 only denser')


def joins(total, limit=60):
    rows = []
    for k1 in range(1, total//2+1):
        k2 = total-k1
        for h1 in range(1, limit+1):
            e1 = ky(k1, h1)
            if e1 is None:
                continue
            for h2 in range(1, limit+1):
                e2 = ky(k2, h2)
                if e2 is None:
                    continue
                n, m = h1+h2, e1+e2+h1*h2
                if m > budget(n):
                    continue
                if min(h1, h2) >= 3 and h1*h2 > 4*(h1+h2)-8:
                    continue
                rows.append(dict(k1=k1, h1=h1, k2=k2, h2=h2, n=n, min_edges=m, slack=budget(n)-m,
                                 first_factor_complete=(h1 == k1)))
    return rows


def apex_budgets(limit=60):
    out = {}
    for a, k in ((1, 9), (2, 8), (3, 7)):
        bound = [(h, budget(h+a)-a*(a-1)//2-a*h) for h in range(k, limit+1)]
        out[f'K{a}_join_{k}critical'] = dict(max_edges_of_H=[[h, b] for h, b in bound[:12]],
                                             omega_H_at_most=8-a,
                                             ky_feasible_orders=[h for h, b in bound if ky(k, h) is not None and ky(k, h) <= b][:40])
    return out


def run():
    j10, j9 = joins(10), joins(9)
    families10 = sorted({(r['k1'], r['k2'], r['first_factor_complete'] and r['h1'] or 0) for r in j10})
    return dict(mycielski=mycielski(), joins_chi10=j10, joins_chi9=j9,
                chi10_join_types=[dict(k1=a, k2=b, complete_first_order=c) for a, b, c in families10],
                chi10_unbounded_types=sorted({(r['k1'], r['h1']) for r in j10 if r['h2'] >= 50}),
                apex=apex_budgets())
