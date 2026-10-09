"""Task 2: how sharp is the box condition (3.1) of Lemma 3 / Corollary 4 for the map A of (4.1)?

For K = Q(sqrt d, sqrt 2), N given, and each (t2, t3) in a range, find the least t1 such that
the rows (theta_n^a1 sigma(theta_n)^a2 sigma-tau(theta_n)^a3)_{n in E_N}, a_j <= t_j, have
rank M = N^4 over K.

Method. Rank modulo a degree-one prime P of K is a lower bound for the rank over K, so a box
that reaches rank M mod P has rank M over K (certified). The least t1 found mod P could be too
large if P is unlucky, so for each minimal box we also compute the exact rank over K of the box
with t1 - 1, via the integer matrix of the regular representation (rank over Q = 4 * rank over K),
and require it to be < M. Both facts together certify that t1 is exactly minimal.

Also checks the claims after (4.1): A (ab, b, -a, -1) = 0 and the minor in the first three
columns equals 4ab.

Usage: python src/interpolation_boxes.py N d1,d2,... TMAX
"""
import json
import sys
from itertools import product
from pathlib import Path

import flint
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lemma7_flint as F  # noqa: E402


def kernel_and_minor(d):
    a, b, ab, one = (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (1, 0, 0, 0)
    neg = lambda z: tuple(-c for c in z)                       # noqa: E731
    add = lambda *zs: tuple(sum(c) for c in zip(*zs))          # noqa: E731
    A = [[one, a, b, ab], [one, neg(a), b, neg(ab)], [one, neg(a), neg(b), ab]]
    c = [ab, b, neg(a), neg(one)]
    kern = [add(*[F.imul(A[i][j], c[j], d) for j in range(4)]) for i in range(3)]
    m = [row[:3] for row in A]
    mul = lambda x, y: F.imul(x, y, d)                         # noqa: E731
    det3 = add(mul(m[0][0], add(mul(m[1][1], m[2][2]), neg(mul(m[1][2], m[2][1])))),
               neg(mul(m[0][1], add(mul(m[1][0], m[2][2]), neg(mul(m[1][2], m[2][0]))))),
               mul(m[0][2], add(mul(m[1][0], m[2][1]), neg(mul(m[1][1], m[2][0])))))
    return all(z == (0, 0, 0, 0) for z in kern), det3 == (0, 0, 0, 4)


def exact_rank_K(d, pts, alphas):
    exact = F.ExactRows(d, pts)
    M = len(pts)
    rows = []
    for al in alphas:
        r = exact.row(al)
        for u in range(4):
            rr = [0] * (4 * M)
            for j in range(M):
                reg = F.regmat(r[j], d)
                for v in range(4):
                    rr[4 * j + v] = reg[u][v]
            rows.append(rr)
    rq = flint.fmpz_mat(rows).rank()
    assert rq % 4 == 0
    return rq // 4


def least_t1(mr, p, M, t2, t3, tmax):
    ech = F.ModEchelon(p)
    for a1 in range(tmax + 1):
        for a2 in range(t2 + 1):
            for a3 in range(t3 + 1):
                r = ech.reduce(mr.row((a1, a2, a3)))
                if r.any():
                    ech.add(r)
        if len(ech.rows) == M:
            return a1
    return None


def main():
    N = int(sys.argv[1])
    ds = [int(x) for x in sys.argv[2].split(",")]
    tmax = int(sys.argv[3])
    pts = list(product(range(N), repeat=4))
    M = len(pts)
    out = []
    for d in ds:
        kern_ok, minor_ok = kernel_and_minor(d)
        p, s, t = next(F.split_primes(d))
        mr = F.ModRows(pts, p, s, t, tmax + 1)
        table = {}
        for t2 in range(tmax + 1):
            for t3 in range(tmax + 1):
                table[(t2, t3)] = least_t1(mr, p, M, t2, t3, M)
        # Pareto-minimal boxes (t1, t2, t3): t1 = least_t1(t2, t3) and it strictly drops
        # compared with (t2-1, t3) and (t2, t3-1)
        minimal = []
        for (t2, t3), t1 in sorted(table.items()):
            if t1 is None:
                continue
            if (t2 > 0 and table[(t2 - 1, t3)] == t1) or (t3 > 0 and table[(t2, t3 - 1)] == t1):
                continue
            minimal.append((t1, t2, t3))
        certs = []
        for (t1, t2, t3) in minimal:
            if t1 == 0:
                certs.append(True)
                continue
            box = [(a1, a2, a3) for a1 in range(t1) for a2 in range(t2 + 1) for a3 in range(t3 + 1)]
            certs.append(exact_rank_K(d, pts, box) < M)
        rec = dict(d=d, N=N, M=M, prime=p, kernel_claim=kern_ok, minor_is_4ab=minor_ok,
                   least_t1={f"{k[0]},{k[1]}": v for k, v in table.items()},
                   minimal_boxes=[list(b) for b in minimal],
                   minimal_box_rows=[(b[0] + 1) * (b[1] + 1) * (b[2] + 1) for b in minimal],
                   exact_minimality_certified=certs)
        out.append(rec)
        print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
