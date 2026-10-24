"""Independent stdlib re-derivation of the S042 census type table (no import of the census tool).

Written separately from tools/s042_census.py: factor edge minima, Kostochka-Yancey
equality/non-Ore windows and leaf budgets recomputed with integer arithmetic.
"""
from fractions import Fraction
import itertools as it


def ky(k, n):
    return Fraction((k+1)*(k-2)*n-k*(k-3), 2*(k-1))


def non_ore(k, n):
    return Fraction((k+1)*(k-2)*n-max(2*k-6, k*k-5*k+2), 2*(k-1))


def up(x):
    return x.numerator//x.denominator+(x.numerator % x.denominator > 0)


def low(k, n):
    if k == 3:
        return n if n >= 5 and n % 2 else None
    return up(ky(k, n)) if n >= 2*k-1 else None


def leaf_budget(a, n):
    # Lambda = K_a v (L-e) has n+a vertices and e(L)-1+a*n+a(a-1)/2 edges <= 6(n+a)-12.
    return 6*(n+a)-12-a*n-a*(a-1)//2+1


def parts(total, smallest, avail):
    if not total:
        yield ()
    for i, (k, n) in enumerate(avail):
        if (k, n) >= smallest and k <= total:
            for rest in parts(total-k, (k, n), avail):
                yield ((k, n),)+rest


def table(nmax=21):
    avail = sorted((k, n) for k in range(3, 10) for n in range(5, nmax+1) if low(k, n) is not None)
    rows = []
    for a in (1, 2, 3):
        for c in range(0, 10-a):
            for fs in parts(10-a-c, (0, 0), avail):
                if not fs:
                    continue
                n = c+sum(x for _, x in fs)
                if n > nmax:
                    continue
                e = c*(c-1)//2+c*(n-c)+sum(low(k, x) for k, x in fs)+sum(p[1]*q[1] for p, q in it.combinations(fs, 2))
                slack = leaf_budget(a, n)-e
                if slack < 0:
                    continue
                status = []
                for k, x in fs:
                    m = low(k, x)
                    if k == 3:
                        status.append('ODD_CYCLE')
                    elif x <= 7:
                        status.append('ATLAS_COMPLETE')
                    elif m+slack >= up(non_ore(k, x)):
                        status.append(f'UNRESOLVED_NONORE_e_{up(non_ore(k, x))}..{m+slack}')
                    elif ky(k, x).denominator == 1:
                        status.append('ORE_ONLY')
                    else:
                        status.append('EMPTY_NO_ORE_AT_THIS_ORDER')
                rows.append((a, c, tuple(fs), n, slack, tuple(status)))
    return sorted(rows)
