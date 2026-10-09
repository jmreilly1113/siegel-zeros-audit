"""Fast exact version of src/lemma7_check.py using python-flint and numpy.

Same construction (Sections 4-5 of the paper), different method:

1. Greedy selection modulo a prime ideal P of degree 1 (p splits completely in K, p < 2^31).
   Rows independent mod P are independent over K, so every retained row is certified.
   Every row rejected mod P is re-checked exactly over K (solve x B_S = r_S over K through
   the regular representation, then test x B = r on all columns). A row that fails the
   exact test is retained, so the selected set is exactly the greedy set over K.
2. Delta = det(R_alpha) is computed exactly: for many split primes, det mod p at all four
   embeddings gives the four coordinates of Delta mod p; these are combined by CRT until
   the modulus exceeds twice a rigorous (Arb) Hadamard bound on the coordinates, and a
   few extra primes are used to confirm the result is stable.
3. Optional second method for N(Delta): det of the 4M x 4M integer matrix of the regular
   representation (flint fmpz_mat.det), which equals N_{K/Q}(Delta).

Output dict has the same keys as lemma7_check.run plus a few extra ones.
Usage: python src/lemma7_flint.py d N H [--json] [--regdet]
"""
import json
import math
import sys
import time
from itertools import product
from pathlib import Path

import flint
import numpy as np

# N(Delta) exceeds Python's default 4300-digit str() limit from N = 4 on
sys.set_int_max_str_digits(0)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lemma7_check as L  # noqa: E402  (reuses vp, legendre, primes_upto, squarefree, print_text)

P_MAX = 2 ** 31


# ---------- exact integer arithmetic in R = Z[a, b] (4-tuples of Python ints) ----------

def imul(x, y, d):
    x1, x2, x3, x4 = x
    y1, y2, y3, y4 = y
    return (x1*y1 + d*x2*y2 + 2*x3*y3 + 2*d*x4*y4,
            x1*y2 + x2*y1 + 2*(x3*y4 + x4*y3),
            x1*y3 + x3*y1 + d*(x2*y4 + x4*y2),
            x1*y4 + x4*y1 + x2*y3 + x3*y2)


def inorm(z, d):
    s = lambda w: (w[0], -w[1], w[2], -w[3])     # noqa: E731
    t = lambda w: (w[0], w[1], -w[2], -w[3])     # noqa: E731
    st = lambda w: (w[0], -w[1], -w[2], w[3])    # noqa: E731
    w = imul(imul(z, s(z), d), imul(t(z), st(z), d), d)
    assert w[1] == w[2] == w[3] == 0
    return w[0]


def regmat(z, d):
    """Matrix of multiplication by z on the basis (1, a, b, ab), acting on coordinate
    row vectors: coords(y * z) = coords(y) @ regmat(z)."""
    rows = []
    for e in ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)):
        rows.append(list(imul(e, z, d)))
    return rows


class ExactRows:
    """Exact rows R_alpha with integer coordinates, cached powers."""

    def __init__(self, d, pts):
        self.d = d
        self.th = [tuple(n) for n in pts]
        self.sth = [(n[0], -n[1], n[2], -n[3]) for n in pts]
        self.stth = [(n[0], -n[1], -n[2], n[3]) for n in pts]
        self.cache = {}

    def pw(self, which, j, e):
        key = (which, j, e)
        if key not in self.cache:
            base = (self.th, self.sth, self.stth)[which][j]
            if e == 0:
                v = (1, 0, 0, 0)
            else:
                v = imul(self.pw(which, j, e - 1), base, self.d)
            self.cache[key] = v
        return self.cache[key]

    def row(self, alpha):
        a1, a2, a3 = alpha
        d = self.d
        return [imul(imul(self.pw(0, j, a1), self.pw(1, j, a2), d), self.pw(2, j, a3), d)
                for j in range(len(self.th))]


# ---------- primes splitting completely in K ----------

def split_primes(d, below=P_MAX):
    """Yield (p, s, t) with p = 1 mod 8, p prime, p not dividing d, (d/p) = 1,
    s^2 = d, t^2 = 2 mod p; descending from `below`."""
    p = below - 1
    p -= (p - 1) % 8           # p = 1 mod 8
    while p > 10 ** 6:
        if flint.fmpz(p).is_prime() and d % p != 0 and L.legendre(d, p) == 1:
            s = int(flint.nmod(d % p, p).sqrt())
            t = int(flint.nmod(2, p).sqrt())
            assert (s * s - d) % p == 0 and (t * t - 2) % p == 0
            yield p, s, t
        p -= 8
    raise RuntimeError("ran out of primes")


class ModRows:
    """Rows R_alpha reduced at the embedding a -> sa, b -> sb mod p, via power tables."""

    def __init__(self, pts, p, sa, sb, maxexp):
        n = np.array(pts, dtype=np.int64)
        ab = sa * sb % p
        x = (n[:, 0] + n[:, 1] * sa + n[:, 2] * sb + n[:, 3] * ab) % p
        y = (n[:, 0] - n[:, 1] * sa + n[:, 2] * sb - n[:, 3] * ab) % p
        z = (n[:, 0] - n[:, 1] * sa - n[:, 2] * sb + n[:, 3] * ab) % p
        self.p = p
        self.tabs = []
        for v in (x, y, z):
            t = [np.ones_like(v)]
            for _ in range(maxexp):
                t.append(t[-1] * v % p)
            self.tabs.append(t)

    def extend(self, maxexp):
        for i, t in enumerate(self.tabs):
            v = t[1]
            while len(t) <= maxexp:
                t.append(t[-1] * v % self.p)

    def row(self, alpha):
        a1, a2, a3 = alpha
        self.extend(max(alpha))
        p = self.p
        return self.tabs[0][a1] * self.tabs[1][a2] % p * self.tabs[2][a3] % p


class ModEchelon:
    def __init__(self, p):
        self.p = p
        self.rows = []      # (pivot, row with pivot entry 1)

    def reduce(self, r):
        p = self.p
        r = r.copy()
        for piv, b in self.rows:
            c = int(r[piv])
            if c:
                r = (r - c * b) % p
        return r

    def add(self, r):
        nz = np.flatnonzero(r)
        piv = int(nz[0])
        inv = pow(int(r[piv]), -1, self.p)
        self.rows.append((piv, r * inv % self.p))


def exact_in_span(exact, retained, pivots, r_alpha, d):
    """True iff the exact row of r_alpha lies in the K-span of the exact retained rows.
    pivots: columns where the retained rows are independent mod P (hence over K)."""
    k = len(retained)
    B = [exact.row(a) for a in retained]
    r = exact.row(r_alpha)
    if k == 0:
        return all(z == (0, 0, 0, 0) for z in r)
    # unknown x in K^k as coordinate vector of length 4k; x B_S = r_S, 4k equations.
    A = [[0] * (4 * k) for _ in range(4 * k)]      # A[(i,u)][(j,v)]
    for i in range(k):
        for jj, j in enumerate(pivots):
            reg = regmat(B[i][j], d)
            for u in range(4):
                for v in range(4):
                    A[4 * i + u][4 * jj + v] = reg[u][v]
    rhs = [c for j in pivots for c in r[j]]
    Aq = flint.fmpq_mat(A).transpose()            # Aq x = rhs
    x = Aq.solve(flint.fmpq_mat([[c] for c in rhs]))
    xs = [x[i, 0] for i in range(4 * k)]
    # check x B = r on every column, exactly
    for j in range(len(r)):
        acc = [flint.fmpq(0)] * 4
        for i in range(k):
            reg = regmat(B[i][j], d)
            for u in range(4):
                xu = xs[4 * i + u]
                if xu != 0:
                    for v in range(4):
                        acc[v] += xu * reg[u][v]
        if any(acc[v] != r[j][v] for v in range(4)):
            return False
    return True


def hadamard_log2_bound(d, N, M, retained):
    """Rigorous upper bound for log2 max_nu |nu(Delta)| (Arb), via the estimate before (5.1):
    |nu(theta_n)| <= (N-1)(1+sqrt|d|)(1+sqrt 2), row norm <= sqrt(M) T^(a1+a2+a3)."""
    T = flint.arb(N - 1) * (1 + flint.arb(abs(d)).sqrt()) * (1 + flint.arb(2).sqrt())
    tot = sum(sum(a) for a in retained)
    lg = flint.arb(M).log() * M / 2 + T.log() * tot
    ub = (lg / flint.arb(2).log()).upper()
    return float(ub) + 1e-6


def run(d, N, H, quiet=False, regdet=False, extra_primes=3):
    assert d not in (0, 1, 2) and L.squarefree(d)
    assert H >= 1
    q = abs(d) if d % 4 == 1 else 4 * abs(d)
    pts = list(product(range(N), repeat=4))
    M = len(pts)
    timing = {}
    exact = ExactRows(d, pts)

    # --- 1. selection ---
    t0 = time.perf_counter()
    primes = split_primes(d)
    p0, s0, t0b = next(primes)
    mr = ModRows(pts, p0, s0, t0b, 8)
    ech = ModEchelon(p0)
    retained, tried, w = [], 0, 0
    rejected_modp, rejected_certified, retained_after_exact = 0, 0, []
    while len(retained) < M:
        for a2 in range(w // H + 1):
            for a3 in range((w - H * a2) // H + 1):
                alpha = (w - H * (a2 + a3), a2, a3)
                tried += 1
                r = ech.reduce(mr.row(alpha))
                if r.any():
                    ech.add(r)
                    retained.append(alpha)
                else:
                    rejected_modp += 1
                    pivots = [pv for pv, _ in ech.rows]
                    if exact_in_span(exact, retained, pivots, alpha, d):
                        rejected_certified += 1
                    else:
                        # independent over K but not mod P: retain; mod-P echelon is no
                        # longer usable, so stop and report (has not happened so far).
                        retained_after_exact.append(alpha)
                        raise RuntimeError(f"row {alpha} independent over K but dependent mod "
                                           f"{p0}; rerun with another prime")
                if len(retained) == M:
                    break
            if len(retained) == M:
                break
        w += 1
    timing["selection_s"] = time.perf_counter() - t0
    maxw = w - 1
    S1 = sum(a[0] for a in retained)
    S2 = sum(a[1] + a[2] for a in retained)

    # --- 2. Delta by CRT over split primes ---
    t0 = time.perf_counter()
    bound_bits = hadamard_log2_bound(d, N, M, retained)
    need_bits = bound_bits + 2          # modulus > 2 * bound
    maxexp = max(max(a) for a in retained)
    modulus = 1
    coords = [0, 0, 0, 0]
    used = 0
    stable_extra = 0
    primes = split_primes(d)            # restart; reuse of p0 is fine
    while True:
        p, s, t = next(primes)
        dets = {}
        for e1 in (1, -1):
            for e2 in (1, -1):
                mrp = ModRows(pts, p, (e1 * s) % p, (e2 * t) % p, maxexp)
                mat = np.stack([mrp.row(a) for a in retained])
                dets[(e1, e2)] = int(flint.nmod_mat(mat.tolist(), p).det())
        inv4 = pow(4, -1, p)
        si, ti = pow(s, -1, p), pow(t, -1, p)
        z = [sum(dets.values()) * inv4 % p,
             sum(e1 * v for (e1, e2), v in dets.items()) * inv4 * si % p,
             sum(e2 * v for (e1, e2), v in dets.items()) * inv4 * ti % p,
             sum(e1 * e2 * v for (e1, e2), v in dets.items()) * inv4 * si * ti % p]
        # CRT
        new = []
        for c, r in zip(coords, z):
            k = ((r - c) * pow(modulus, -1, p)) % p
            new.append(c + modulus * k)
        newmod = modulus * p
        sym = [c if c <= newmod // 2 else c - newmod for c in new]
        oldsym = [c if c <= modulus // 2 else c - modulus for c in coords]
        if modulus.bit_length() > need_bits:
            stable_extra = stable_extra + 1 if sym == oldsym else 0
            if sym != oldsym:
                raise RuntimeError("CRT result changed after exceeding the Hadamard bound")
        coords, modulus = new, newmod
        used += 1
        if modulus.bit_length() > need_bits and stable_extra >= extra_primes:
            break
    Delta = [c if c <= modulus // 2 else c - modulus for c in coords]
    timing["det_crt_s"] = time.perf_counter() - t0
    ND = inorm(tuple(Delta), d)
    assert ND != 0

    res_extra = dict(method="flint/CRT", selection_prime=p0, crt_primes=used,
                     hadamard_log2_bound=bound_bits, rejected_mod_p=rejected_modp,
                     rejected_certified_exact=rejected_certified)

    if regdet:
        t0 = time.perf_counter()
        big = [[0] * (4 * M) for _ in range(4 * M)]
        for i, a in enumerate(retained):
            row = exact.row(a)
            for j in range(M):
                reg = regmat(row[j], d)
                for u in range(4):
                    for v in range(4):
                        big[4 * i + u][4 * j + v] = reg[u][v]
        nd2 = int(flint.fmpz_mat(big).det())
        timing["regdet_s"] = time.perf_counter() - t0
        res_extra["regdet_norm_agrees"] = (nd2 == ND)
        if nd2 != ND:
            raise RuntimeError("regular-representation det disagrees with CRT norm")

    g = 0
    for c in Delta:
        g = math.gcd(g, c)
    maxa1 = max(a[0] for a in retained)
    ok = ok_strong = True
    prs = []
    for p in L.primes_upto(max(maxa1, 2)):
        Ep = sum(a[0] // p for a in retained)
        v = L.vp(ND, p)
        vg = L.vp(g, p)
        if p == 2 or q % p == 0:
            chi, two, tag, admissible = 0, (0 if p == 2 else L.legendre(2, p)), "excluded (p | 2q)", False
        else:
            chi, two = L.legendre(d, p), L.legendre(2, p)
            admissible = (chi == -1 and p > H)
            tag = ("admissible" if admissible else "chi=-1, p<=H" if chi == -1
                   else "chi=+1,(2/p)=+1" if two == 1 else "chi=+1,(2/p)=-1")
        holds = v >= 4 * Ep
        strong = vg >= Ep
        if admissible:
            ok &= holds
            ok_strong &= strong
        prs.append(dict(p=p, chi=chi, two=two, tag=tag, admissible=admissible, Ep=Ep,
                        four_Ep=4 * Ep, vp=v, vp_ge_4Ep=holds, vp_gcd_Delta=vg,
                        Delta_in_pEpR=strong))

    res = dict(d=d, q=q, N=N, H=H, H_le_N=(H <= N), M=M, retained=[list(a) for a in retained],
               rows_tried=tried, max_weight=maxw,
               max_weight_bound=f"96*H^(2/3)*N^(4/3) = {96 * H ** (2 / 3) * N ** (4 / 3):.1f}",
               S1=S1, S2=S2, max_alpha1=maxa1, Delta=[str(c) for c in Delta], norm_Delta=str(ND),
               norm_digits=len(str(abs(ND))), log_abs_norm=L.log_abs_ball(ND), primes=prs,
               lemma7_holds_all_admissible=ok, lemma7_Delta_in_pEpR_all_admissible=ok_strong,
               timing=timing, **res_extra)
    if not quiet:
        L.print_text(res)
        print(f"  Delta in p^E_p R at all admissible p: {ok_strong}; CRT primes {used}; "
              f"rejections mod p {rejected_modp} (all certified exactly: "
              f"{rejected_certified == rejected_modp}); timing {timing}")
    return res


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    d, N, H = (int(x) for x in args[:3])
    res = run(d, N, H, quiet="--json" in sys.argv, regdet="--regdet" in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps(res))
