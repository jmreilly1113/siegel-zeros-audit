"""Executable version of the proof of Lemma 3 (lem:interpolation) in
"Uniform exclusion of Landau-Siegel zeros", refs/siegel-paper.tex lines 269-407.

For a nonzero dual vector v on E_N = {0..N-1}^4 the proof builds a polynomial
B in P_t with sum_n v_n B(An) != 0. We carry out that construction literally,
in exact arithmetic (Fractions; K = Q(sqrt d, sqrt 2) via lemma7_check), with A
from (eq:A), and check every intermediate claim. Step numbers refer to
docs/lemma3-audit.md.

Two ways to choose the auxiliary polynomial R of (eq:zeros):
  'product': R = prod_{m in K cap Z^4} (z1 - theta_m), so deg_{z1} R = #(K cap Z^4),
             deg_{z2} R = deg_{z3} R = 0. This satisfies (eq:budget) with
             b = (#L, 0, 0), and R(Ax) = 0 exactly on K cap Z^4.
  'generic': a random element of the space of R with deg_{z_j} R <= b_j vanishing
             on K cap Z^4, for the smallest balanced b with prod(b_j + 1) > #L.
             R may vanish at further lattice points, which makes the
             nearest-point search in step 5 non-trivial.

Usage: python src/lemma3_construct.py --N 2 --d -7 5 --count 40 --seed 1 [--json out.jsonl]
"""
from fractions import Fraction
from itertools import product
import argparse
from functools import reduce
import json
from math import gcd
import random
import sys
import time

import lemma7_check as KA

F0, F1 = Fraction(0), Fraction(1)


# ---------- rational vector helpers ----------

def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def vsub(x, y):
    return tuple(a - b for a, b in zip(x, y))


def vadd(x, y):
    return tuple(a + b for a, b in zip(x, y))


def vscale(c, x):
    return tuple(c * a for a in x)


def solve(mat, rhs):
    """Solve a square nonsingular rational system by Gaussian elimination."""
    n = len(mat)
    m = [list(r) + [b] for r, b in zip(mat, rhs)]
    for i in range(n):
        p = next(k for k in range(i, n) if m[k][i] != 0)
        m[i], m[p] = m[p], m[i]
        piv = m[i][i]
        m[i] = [t / piv for t in m[i]]
        for k in range(n):
            if k != i and m[k][i] != 0:
                f = m[k][i]
                m[k] = [a - f * b for a, b in zip(m[k], m[i])]
    return [m[i][n] for i in range(n)]


def nullspace_Q(rows, ncols):
    """Basis of {x in Q^ncols : row . x = 0 for all rows}."""
    m = [list(map(Fraction, r)) for r in rows]
    piv_cols, r = [], 0
    for c in range(ncols):
        p = next((k for k in range(r, len(m)) if m[k][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        pv = m[r][c]
        m[r] = [t / pv for t in m[r]]
        for k in range(len(m)):
            if k != r and m[k][c] != 0:
                f = m[k][c]
                m[k] = [a - f * b for a, b in zip(m[k], m[r])]
        piv_cols.append(c)
        r += 1
    free = [c for c in range(ncols) if c not in piv_cols]
    basis = []
    for fc in free:
        x = [F0] * ncols
        x[fc] = F1
        for i, pc in enumerate(piv_cols):
            x[pc] = -m[i][fc]
        basis.append(x)
    return basis


def affine_rank(points):
    if not points:
        return -1
    p0 = points[0]
    diffs = [vsub(p, p0) for p in points[1:]]
    return len(diffs[0]) - len(nullspace_Q(diffs, len(p0))) if diffs else 0


# ---------- exact nearest point (Wolfe's min-norm-point algorithm) ----------

def min_norm_point(Q):
    """Exact min-norm point of conv(Q). Returns (x, {index: weight}).

    Wolfe (1976); finite in exact arithmetic. The result is certified by the
    caller: weights >= 0 summing to 1 and x.x <= x.q for every q.
    """
    j = min(range(len(Q)), key=lambda k: dot(Q[k], Q[k]))
    corral, lam, x = [j], {j: F1}, Q[j]
    while True:
        xx = dot(x, x)
        best = min(range(len(Q)), key=lambda k: dot(x, Q[k]))
        if xx <= dot(x, Q[best]):
            return x, lam
        assert best not in corral
        corral.append(best)
        lam[best] = F0
        while True:
            n = len(corral)
            G = [[dot(Q[a], Q[b]) for b in corral] + [F1] for a in corral] + [[F1] * n + [F0]]
            alpha = solve(G, [F0] * n + [F1])[:n]
            if all(a > 0 for a in alpha):
                lam = dict(zip(corral, alpha))
                break
            theta = min((lam[i] / (lam[i] - a) if lam[i] != a else F0)
                        for i, a in zip(corral, alpha) if a <= 0)
            lam = {i: theta * a + (1 - theta) * lam[i] for i, a in zip(corral, alpha)}
            corral = [i for i in corral if lam[i] != 0]
            lam = {i: lam[i] for i in corral}
        x = tuple(sum(lam[i] * Q[i][t] for i in corral) for t in range(len(Q[0])))


def nearest(target, pts):
    """Certified nearest point of conv(pts) to target. Returns (y, dist2, weights)."""
    Q = [vsub(p, target) for p in pts]
    x, lam = min_norm_point(Q)
    xx = dot(x, x)
    assert all(w >= 0 for w in lam.values()) and sum(lam.values()) == 1
    assert all(xx <= dot(x, q) for q in Q), "nearest-point certificate failed"
    return vadd(target, x), xx, lam


# ---------- K-valued objects ----------

def Kc(q):
    return (Fraction(q), F0, F0, F0)


def A_of(n):
    """An = (theta_n, sigma theta_n, sigma tau theta_n), (eq:A)."""
    th = tuple(Fraction(t) for t in n)
    return (th, KA.sigma(th), KA.sigmatau(th))


def kpow(z, e, d):
    r = KA.ONE
    for _ in range(e):
        r = KA.mul(r, z, d)
    return r


class Poly:
    """R as an explicit sum of coefficient * z^beta, or as a product of (z1 - theta)."""

    def __init__(self, d, terms=None, roots=None, degs=None):
        self.d, self.terms, self.roots, self.degs = d, terms, roots, degs

    def at(self, z):
        d = self.d
        if self.roots is not None:
            # every root theta_m and every z[0] used here is integral: multiply in int
            # arithmetic (exact), and stop at a zero factor
            if any(t.denominator != 1 for t in z[0]):
                r = KA.ONE
                for th in self.roots:
                    r = KA.mul(r, KA.sub(z[0], th), d)
                return r
            z0 = tuple(int(t) for t in z[0])
            r = (1, 0, 0, 0)
            for th in self.roots:
                f = tuple(x - int(y) for x, y in zip(z0, th))
                if not any(f):
                    return KA.ZERO
                r = KA.mul(r, f, d)
            return tuple(Fraction(t) for t in r)
        r = KA.ZERO
        for beta, c in self.terms:
            t = c
            for j in range(3):
                t = KA.mul(t, kpow(z[j], beta[j], d), d)
            r = KA.add(r, t)
        return r


def generic_R(L, d, rng):
    """Random nonzero R with deg_{z_j} R <= b_j, vanishing at A m for m in L."""
    b = [0, 0, 0]
    while (b[0] + 1) * (b[1] + 1) * (b[2] + 1) <= len(L):
        j = min(range(3), key=lambda k: b[k])
        b[j] += 1
    mons = list(product(*(range(bj + 1) for bj in b)))
    # Equations over K, expanded to rational equations through the basis 1, a, b, ab.
    # Unknown coefficients c_beta in K, also expanded: c_beta = sum_s x_{beta,s} e_s.
    basis = [tuple(Fraction(int(i == s)) for i in range(4)) for s in range(4)]
    rows = []
    for m in L:
        Am = A_of(m)
        vals = []
        for beta in mons:
            t = KA.ONE
            for j in range(3):
                t = KA.mul(t, kpow(Am[j], beta[j], d), d)
            vals.append(t)
        for comp in range(4):
            rows.append([KA.mul(v, e, d)[comp] for v in vals for e in basis])
    ns = nullspace_Q(rows, 4 * len(mons))
    assert ns, "dimension count failed"
    x = [F0] * (4 * len(mons))
    for vec in ns:
        c = rng.randint(-3, 3) or 1
        x = [a + c * t for a, t in zip(x, vec)]
    terms = []
    for i, beta in enumerate(mons):
        coef = tuple(x[4 * i + s] for s in range(4))
        if not KA.is_zero(coef):
            terms.append((beta, coef))
    assert terms
    return Poly(d, terms=terms, degs=tuple(b)), b, len(ns)


def kmat_inv(M, d):
    """Inverse of a square matrix over K (Gauss-Jordan)."""
    n = len(M)
    m = [list(r) + [KA.ONE if i == j else KA.ZERO for j in range(n)] for i, r in enumerate(M)]
    for i in range(n):
        p = next((k for k in range(i, n) if not KA.is_zero(m[k][i])), None)
        if p is None:
            return None
        m[i], m[p] = m[p], m[i]
        pinv = KA.inv(m[i][i], d)
        m[i] = [KA.mul(pinv, t, d) for t in m[i]]
        for k in range(n):
            if k != i and not KA.is_zero(m[k][i]):
                f = m[k][i]
                m[k] = [KA.sub(a, KA.mul(f, b, d)) for a, b in zip(m[k], m[i])]
    return [r[n:] for r in m]


# ---------- one instance of the proof ----------

def lattice_points(S):
    """K cap Z^4 for K = 4 conv(S). K lies inside 4 * bbox(S)."""
    V4 = [tuple(Fraction(4 * t) for t in s) for s in S]
    lo = [4 * min(s[i] for s in S) for i in range(4)]
    hi = [4 * max(s[i] for s in S) for i in range(4)]
    L = [m for m in product(*(range(lo[i], hi[i] + 1) for i in range(4)))
         if nearest(tuple(map(Fraction, m)), V4)[1] == 0]
    return V4, lo, hi, L


def run_instance(d, N, S, v, mode, rng, geom, override=None):
    """Follow the proof for support S (list of 4-tuples) and weights v (dict).

    override: tests only. {'m': ...} or {'u': ...} replaces the proof's choice, to show
    that the checks catch a wrong construction.
    """
    override = override or {}
    out = {"d": d, "N": N, "S_size": len(S), "mode": mode}
    chk = {}
    # Step 2: K = 4P and its lattice points.
    V4, lo, hi, L = geom
    out["dim_P"] = affine_rank([tuple(map(Fraction, s)) for s in S])
    out["lattice_pts_in_K"] = len(L)
    chk["2_count_le_(4N-3)^4"] = len(L) <= (4 * N - 3) ** 4
    # Step 3: R.
    if mode == "product":
        R = Poly(d, roots=[A_of(m)[0] for m in L])
        b = (len(L), 0, 0)
        out["null_dim"] = None
    else:
        R, b, out["null_dim"] = generic_R(L, d, rng)
    out["b"] = list(b)
    chk["3_dim_exceeds_conditions"] = (b[0] + 1) * (b[1] + 1) * (b[2] + 1) > len(L)
    chk["3_R_vanishes_on_K_lattice"] = all(KA.is_zero(R.at(A_of(m))) for m in L)
    # Step 5: lattice m with R(Am) != 0 nearest to K. Points outside the box
    # widened by r have distance >= r + 1, so the search is complete once best <= (r+1)^2.
    Lset = set(L)
    r, best, best_m = 1, None, None
    zeros_seen = []     # dist2 of points outside K where R vanished (generic mode)
    while True:
        cands = []
        for m in product(*(range(lo[i] - r, hi[i] + r + 1) for i in range(4))):
            if m in Lset:
                continue
            bd2 = sum(max(lo[i] - m[i], 0, m[i] - hi[i]) ** 2 for i in range(4))
            cands.append((bd2, m))
        cands.sort()
        for bd2, m in cands:
            if best is not None and bd2 >= best:
                break
            dist2 = nearest(tuple(map(Fraction, m)), V4)[1]
            if best is not None and dist2 >= best:
                continue
            if mode == "product" or not KA.is_zero(R.at(A_of(m))):
                best, best_m = dist2, m
            else:
                zeros_seen.append(dist2)
        if best is not None and best <= (r + 1) ** 2:
            break
        r += 1
    best_m = tuple(override.get("m", best_m))
    m = tuple(map(Fraction, best_m))
    out["m"], out["dist2_m"] = list(best_m), str(best)
    # Every lattice point closer than m was examined, so this counts all of them.
    out["closer_zeros_outside_K"] = sum(1 for z in zeros_seen if z < best)
    Rm = R.at(A_of(best_m))
    chk["5_R(Am)_nonzero"] = not KA.is_zero(Rm)
    y, dist2, _ = nearest(m, V4)
    h = vsub(m, y)
    chk["5_h_nonzero"] = any(t != 0 for t in h)
    # Step 6: y/4 in G, the face of P maximizing h.
    hmax = max(dot(h, s) for s in S)
    SG = [s for s in S if dot(h, s) == hmax]
    chk["6_y/4_in_G"] = dot(h, vscale(Fraction(1, 4), y)) == hmax
    # Step 7.
    out["dim_G"] = affine_rank([tuple(map(Fraction, s)) for s in SG])
    chk["7_dim_G_le_3"] = out["dim_G"] <= 3
    # Step 8, as in the paper: vertices of G, Caratheodory, a coefficient >= 1/4.
    verts = [s for s in SG
             if len(SG) == 1 or nearest(tuple(map(Fraction, s)), [t for t in SG if t != s])[1] > 0]
    V4G = [tuple(Fraction(4 * t) for t in s) for s in verts]
    yy, dd, lam = nearest(y, V4G)
    chk["8_y_in_4conv(vertices of G)"] = dd == 0
    chk["8_at_most_4_vertices"] = len(lam) <= 4
    iu = max(lam, key=lambda i: lam[i])
    u = tuple(override.get("u", verts[iu]))
    chk["8_coefficient_ge_1/4"] = lam[iu] >= Fraction(1, 4)
    chk["8_u_in_S_and_G"] = u in S and dot(h, u) == hmax
    coeffs = {i: (4 * w - (1 if i == iu else 0)) / 3 for i, w in lam.items()}
    chk["8_y-u_in_3P_explicit"] = all(c >= 0 for c in coeffs.values()) and sum(coeffs.values()) == 1
    S3 = [tuple(Fraction(3 * t) for t in s) for s in S]
    chk["8_y-u_in_3P_independent"] = nearest(vsub(y, u), S3)[1] == 0
    out["u"] = list(u)
    # Steps 9-11 for every n in S \ G.
    ok9 = ok10 = okd = ok11 = True
    for n in S:
        if dot(h, n) == hmax:
            continue
        yp = vadd(y, vsub(n, u))
        mp = vadd(m, vsub(n, u))
        ok9 &= nearest(yp, V4)[1] == 0 and vsub(mp, yp) == h
        ok10 &= dot(h, vsub(u, n)) > 0
        okd &= nearest(mp, V4)[1] < dist2
        ok11 &= KA.is_zero(R.at(A_of(tuple(int(t) for t in mp))))
    chk["9_y'_in_4P"] = ok9
    chk["10_h.(u-n)>0"] = ok10
    chk["10_m'_closer"] = okd
    chk["11_R_vanishes_off_face"] = ok11
    # Step 12: rational hyperplane r.v = k containing G, with r.c != 0.
    rowsG = [list(map(Fraction, s)) + [Fraction(-1)] for s in SG]
    ns = [x for x in nullspace_Q(rowsG, 5) if any(t != 0 for t in x[:4])]
    rk = [F0] * 5
    for x in ns:
        c = rng.randint(1, 5)
        rk = [a + c * t for a, t in zip(rk, x)]
    if all(t == 0 for t in rk[:4]):
        rk = ns[0]
    den = 1
    for t in rk:
        den = den * t.denominator // gcd(den, t.denominator)
    rk = [int(t * den) for t in rk]
    rvec, k = rk[:4], rk[4]
    chk["12_r_nonzero_integer"] = any(rvec)
    chk["12_G_in_hyperplane"] = all(dot(rvec, s) == k for s in SG)
    # c = (ab, b, -a, -1) in K
    c_dot = KA.add(KA.add((F0, F0, F0, Fraction(rvec[0])), (F0, F0, Fraction(rvec[1]), F0)),
                   KA.add((F0, Fraction(-rvec[2]), F0, F0), Kc(-rvec[3])))
    chk["12_r.c_nonzero"] = not KA.is_zero(c_dot)
    # Step 13: A restricted to H is a bijection: [A; r] invertible over K.
    a_ = (F0, F1, F0, F0)
    b_ = (F0, F0, F1, F0)
    ab_ = (F0, F0, F0, F1)
    Arows = [[KA.ONE, a_, b_, ab_],
             [KA.ONE, tuple(-t for t in a_), b_, tuple(-t for t in ab_)],
             [KA.ONE, tuple(-t for t in a_), tuple(-t for t in b_), ab_]]
    Minv = kmat_inv(Arows + [[Kc(t) for t in rvec]], d)
    chk["13_A_on_H_bijective"] = Minv is not None
    # Step 14: lambda_i and Lagrange polynomial Q.
    i0 = next(i for i in range(4) if rvec[i] != 0)

    def lam_at(z):
        w = list(z) + [Kc(k)]
        return [reduce(KA.add, [KA.mul(Minv[i][j], w[j], d) for j in range(4)]) for i in range(4)]

    def Q_at(z):
        lv = lam_at(z)
        r_ = KA.ONE
        for i in range(4):
            if i == i0:
                continue
            for a in range(N):
                if a != u[i]:
                    r_ = KA.mul(r_, KA.mul(KA.sub(lv[i], Kc(a)), KA.inv(Kc(u[i] - a), d), d), d)
        return r_

    chk["14_lambda_recovers_coords_on_G"] = all(
        lam_at(A_of(n)) == [Kc(t) for t in n] for n in SG)
    chk["14_Q_degree_le_3(N-1)"] = 3 * (N - 1) == sum(1 for i in range(4) if i != i0 for a in range(N) if a != u[i])
    chk["14_Q(Au)=1"] = Q_at(A_of(u)) == KA.ONE
    chk["14_Q_vanishes_on_rest_of_G"] = all(KA.is_zero(Q_at(A_of(n))) for n in SG if n != u)
    # Step 15: B = Q(z) R(z + A(m-u)) has deg_{z_j} B <= b_j + 3(N-1) (deg Q is the number of
    # affine factors, checked above; translation keeps R's separate degrees). R also lies in the
    # space for b' = (max(b_1, (4N-3)^4), b_2, b_3), which satisfies (eq:budget); so this run is
    # an instance of the lemma for t = b' + 3(N-1).
    bp = [max(b[0], (4 * N - 3) ** 4), b[1], b[2]]
    out["t_paper_instance"] = [x + 3 * (N - 1) for x in bp]
    chk["15_t_satisfies_budget"] = (bp[0] + 1) * (bp[1] + 1) * (bp[2] + 1) > (4 * N - 3) ** 4
    # Step 16: the contradiction.
    total = KA.ZERO
    for n in S:
        shifted = tuple(int(t) for t in vadd(tuple(map(Fraction, n)), vsub(m, u)))
        total = KA.add(total, KA.mul(Kc(v[n]), KA.mul(Q_at(A_of(n)), R.at(A_of(shifted)), d), d))
    chk["16_sum_equals_v_u_R(Am)"] = total == KA.mul(Kc(v[u]), Rm, d)
    chk["16_sum_nonzero"] = not KA.is_zero(total)
    out["checks"] = chk
    out["all_ok"] = all(chk.values())
    return out


def supports(N, rng, count):
    """Structured and random supports in E_N."""
    E = list(product(range(N), repeat=4))
    yield [E[0]]
    yield [E[-1]]
    yield [(0, 0, 0, 0), (N - 1, 0, 0, 0)]                    # a segment
    yield [(0, 0, 0, 0), (N - 1, N - 1, 0, 0), (0, N - 1, 0, 0)]  # a triangle
    yield [e for e in E if e[0] == 0 and e[1] == 0]           # a 2-dim face of the cube
    yield [e for e in E if e[0] == N - 1]                     # a facet
    yield [e for e in E if sum(e) == N - 1]                   # a slice of the simplex
    yield [e for e in E if sum(e) <= 1]                       # standard simplex: smallest 4-dim P
    yield E                                                   # everything
    for _ in range(count):
        k = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, len(E) // 2, len(E) - 1])
        yield rng.sample(E, min(k, len(E)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=2)
    ap.add_argument("--d", type=int, nargs="+", default=[-7, 5])
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--modes", nargs="+", default=["product", "generic"])
    ap.add_argument("--max-lattice-generic", type=int, default=60,
                    help="skip 'generic' when #(K cap Z^4) is larger (linear algebra cost)")
    ap.add_argument("--json")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    fh = open(a.json, "w") if a.json else None
    nrun = nfail = 0
    t0 = time.time()
    for d in a.d:
        for S in supports(a.N, rng, a.count):
            S = sorted(set(S))
            v = {s: Fraction(rng.choice([-1, 1]) * rng.randint(1, 9)) for s in S}
            geom = lattice_points(S)
            for mode in a.modes:
                if mode == "generic" and len(geom[3]) > a.max_lattice_generic:
                    continue
                res = run_instance(d, a.N, S, v, mode, rng, geom)
                nrun += 1
                nfail += not res["all_ok"]
                if not res["all_ok"]:
                    print("FAIL", json.dumps(res))
                if fh:
                    res["S"] = [list(s) for s in S]
                    fh.write(json.dumps(res) + "\n")
    print(f"N={a.N} d={a.d} seed={a.seed}: {nrun} instances, {nfail} failures, {time.time() - t0:.1f}s")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
