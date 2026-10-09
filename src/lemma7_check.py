"""Exact small-N check of the determinant construction in
"Uniform exclusion of Landau-Siegel zeros" (openai/math, Oct 1 2026), Sections 4-5.

Elements of K = Q(a, b), a^2 = d, b^2 = 2, are 4-tuples (z1, z2, z3, z4)
meaning z1 + z2*a + z3*b + z4*ab, with Fraction coefficients.
"""
from fractions import Fraction
from itertools import product
import json
import sys
import time

# N(Delta) exceeds Python's default 4300-digit str() limit from N = 4 on
sys.set_int_max_str_digits(0)

ONE = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
ZERO = (Fraction(0),) * 4


def mul(x, y, d):
    x1, x2, x3, x4 = x
    y1, y2, y3, y4 = y
    return (
        x1*y1 + d*x2*y2 + 2*x3*y3 + 2*d*x4*y4,
        x1*y2 + x2*y1 + 2*(x3*y4 + x4*y3),
        x1*y3 + x3*y1 + d*(x2*y4 + x4*y2),
        x1*y4 + x4*y1 + x2*y3 + x3*y2,
    )


def add(x, y):
    return tuple(u + v for u, v in zip(x, y))


def sub(x, y):
    return tuple(u - v for u, v in zip(x, y))


def sigma(z):      # a -> -a
    return (z[0], -z[1], z[2], -z[3])


def tau(z):        # b -> -b
    return (z[0], z[1], -z[2], -z[3])


def sigmatau(z):
    return (z[0], -z[1], -z[2], z[3])


def norm(z, d):
    """N(z) = z sigma(z) tau(z) sigmatau(z), a rational number."""
    w = mul(mul(z, sigma(z), d), mul(tau(z), sigmatau(z), d), d)
    assert w[1] == w[2] == w[3] == 0
    return w[0]


def inv(z, d):
    c = mul(mul(sigma(z), tau(z), d), sigmatau(z), d)
    n = norm(z, d)
    return tuple(t / n for t in c)


def power(z, e, d, cache):
    key = (z, e)
    if key in cache:
        return cache[key]
    r = ONE
    base, k = z, e
    while k:
        if k & 1:
            r = mul(r, base, d)
        base = mul(base, base, d)
        k >>= 1
    cache[key] = r
    return r


def is_zero(z):
    return all(t == 0 for t in z)


class Echelon:
    """Incremental row echelon basis over K, used for the greedy row selection."""

    def __init__(self, ncols, d):
        self.rows = []      # (pivot_col, row normalized so pivot entry is 1)
        self.ncols = ncols
        self.d = d

    def reduce(self, row):
        row = list(row)
        for piv, b in self.rows:
            c = row[piv]
            if not is_zero(c):
                row = [sub(row[j], mul(c, b[j], self.d)) for j in range(self.ncols)]
        return row

    def try_add(self, row):
        r = self.reduce(row)
        for j, c in enumerate(r):
            if not is_zero(c):
                ci = inv(c, self.d)
                r = [mul(ci, t, self.d) for t in r]
                self.rows.append((j, r))
                return True
        return False


def det(mat, d):
    """Determinant over K by Gaussian elimination."""
    m = [list(r) for r in mat]
    n = len(m)
    result = ONE
    for i in range(n):
        p = next((k for k in range(i, n) if not is_zero(m[k][i])), None)
        if p is None:
            return ZERO
        if p != i:
            m[i], m[p] = m[p], m[i]
            result = tuple(-t for t in result)
        piv = m[i][i]
        result = mul(result, piv, d)
        pinv = inv(piv, d)
        for k in range(i + 1, n):
            f = mul(m[k][i], pinv, d)
            if not is_zero(f):
                m[k] = [sub(m[k][j], mul(f, m[i][j], d)) for j in range(n)]
    return result


def vp(n, p):
    n = abs(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def legendre(a, p):
    t = pow(a % p, (p - 1) // 2, p)
    return -1 if t == p - 1 else t


def primes_upto(n):
    s = [True] * (n + 1)
    s[0:2] = [False, False]
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            s[i*i::i] = [False] * len(s[i*i::i])
    return [i for i, v in enumerate(s) if v]


def squarefree(n):
    n = abs(n)
    k = 2
    while k * k <= n:
        if n % (k * k) == 0:
            return False
        k += 1
    return True


def run(d, N, H, quiet=False):
    """Build Delta for Q(sqrt d, sqrt 2), box size N, weight H. Returns a dict of results;
    prints a text summary unless quiet."""
    assert d not in (0, 1, 2) and squarefree(d), "d must be squarefree, d != 0, 1, 2"
    # The paper assumes 1 <= H <= N (Section 4). Lemma 7's proof only uses p > H, so H > N
    # is allowed here for testing Lemma 7, and flagged in the output.
    assert H >= 1
    q = abs(d) if d % 4 == 1 else 4 * abs(d)
    pts = list(product(range(N), repeat=4))
    M = len(pts)
    thetas = [tuple(Fraction(c) for c in n) for n in pts]
    cache = {}
    timing = {}

    def row(alpha):
        a1, a2, a3 = alpha
        return [mul(mul(power(t, a1, d, cache), power(sigma(t), a2, d, cache), d),
                    power(sigmatau(t), a3, d, cache), d) for t in thetas]

    # enumerate indices by weight w = a1 + H*a2 + H*a3; ties broken lexicographically
    t0 = time.perf_counter()
    ech = Echelon(M, d)
    retained = []
    tried = 0
    w = 0
    while len(retained) < M:
        for a2 in range(w // H + 1):
            for a3 in range((w - H * a2) // H + 1):
                a1 = w - H * (a2 + a3)
                alpha = (a1, a2, a3)
                tried += 1
                if ech.try_add(row(alpha)):
                    retained.append(alpha)
                    if len(retained) == M:
                        break
            if len(retained) == M:
                break
        w += 1
    timing["selection_s"] = time.perf_counter() - t0
    maxw = w - 1

    S1 = sum(a[0] for a in retained)
    S2 = sum(a[1] + a[2] for a in retained)
    t0 = time.perf_counter()
    Delta = det([row(a) for a in retained], d)
    timing["det_s"] = time.perf_counter() - t0
    assert all(t.denominator == 1 for t in Delta), "Delta not in Z[a,b]"
    t0 = time.perf_counter()
    ND = norm(Delta, d)
    timing["norm_s"] = time.perf_counter() - t0
    assert ND.denominator == 1 and ND != 0
    ND = int(ND)
    logN = log_abs_ball(ND)

    maxa1 = max(a[0] for a in retained)
    ok = True
    primes = []
    for p in primes_upto(max(maxa1, 2)):
        Ep = sum(a[0] // p for a in retained)
        v = vp(ND, p)
        if p == 2 or q % p == 0:
            chi, two, tag = 0, (0 if p == 2 else legendre(2, p)), "excluded (p | 2q)"
            admissible = False
        else:
            chi, two = legendre(d, p), legendre(2, p)
            admissible = (chi == -1 and p > H)
            if admissible:
                tag = "admissible"
            elif chi == -1:
                tag = "chi=-1, p<=H"
            elif two == 1:
                tag = "chi=+1,(2/p)=+1"
            else:
                tag = "chi=+1,(2/p)=-1"
        holds = v >= 4 * Ep
        if admissible and not holds:
            ok = False
        primes.append(dict(p=p, chi=chi, two=two, tag=tag, admissible=admissible,
                           Ep=Ep, four_Ep=4 * Ep, vp=v, vp_ge_4Ep=holds))

    res = dict(d=d, q=q, N=N, H=H, H_le_N=(H <= N), M=M, retained=[list(a) for a in retained],
               rows_tried=tried, max_weight=maxw,
               max_weight_bound=f"96*H^(2/3)*N^(4/3) = {96 * H ** (2 / 3) * N ** (4 / 3):.1f}",
               S1=S1, S2=S2, max_alpha1=maxa1,
               Delta=[str(int(t)) for t in Delta], norm_Delta=str(ND),
               norm_digits=len(str(abs(ND))), log_abs_norm=logN,
               primes=primes, lemma7_holds_all_admissible=ok, timing=timing)
    if not quiet:
        print_text(res)
    return res


def log_abs_ball(n):
    """Rigorous enclosure of log|n| for a nonzero integer n, via Arb if available."""
    try:
        import flint
        b = flint.arb(flint.fmpz(abs(n))).log()
        return dict(mid=float(b.mid()), rad=float(b.rad()), arb=b.str(20, radius=True))
    except ImportError:
        return dict(mid=None, rad=None, arb=None, note="python-flint not installed")


def print_text(res):
    print(f"d={res['d']} q={res['q']} N={res['N']} H={res['H']} M={res['M']} "
          f"max weight={res['max_weight']} S1={res['S1']} S2={res['S2']}")
    print(f"  log|N(Delta)| = {res['norm_digits']} digits")
    for r in res["primes"]:
        if not r["Ep"] or r["p"] == 2 or r["tag"].startswith("excluded"):
            continue
        flag = "  <-- VIOLATES Lemma 7" if r["admissible"] and not r["vp_ge_4Ep"] else ""
        tag = r["tag"] if r["tag"] in ("admissible", "chi=+1,(2/p)=+1") else "other"
        print(f"  p={r['p']:3d} chi={r['chi']:+d} (2/p)={r['two']:+d} {tag:18s} "
              f"4E_p={r['four_Ep']:4d} v_p(N)={r['vp']:4d}{flag}")
    print("  Lemma 7 holds for all admissible p tested" if res["lemma7_holds_all_admissible"]
          else "  Lemma 7 FAILED")


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if x != "--json"]
    d, N, H = (int(x) for x in args[:3])
    if "--json" in sys.argv:
        print(json.dumps(run(d, N, H, quiet=True)))
    else:
        run(d, N, H)
