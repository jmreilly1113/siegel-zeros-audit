"""Numerical check of the HeckeSevenEighths L-function definition (statement check, step 5c fallback).

COMPUTED (numerical), not proved. Three ways of computing L(s, chi) at real s > 1:

  DEF  -- from the challenge's own definitions (HeckeSevenEighths.lean lines 9-235), mirrored term by term:
          hurwitzEvenFEPair, rescale, product, xShift/yShift/parityPair, finitePair, WeakFEPair.Lambda,
          latticeL and LFunction = latticeL / 6. Lambda_0 = mellin f_modif is evaluated as
          int_1^inf t^(s-1) (f - f0) dt + eps * int_1^inf t^(-s) (g - g0) dt, which is the Mellin integral of
          f_modif after the substitution t -> 1/t on (0,1) and the functional equation f(1/x) = eps x^k g(x)
          (the WeakFEPair field h_feq, proved in the challenge file). The functional equation is also spot-checked
          numerically below. mpmath, 40 digits, adaptive quadrature: not rigorous.
  NORM -- independent: (1/6) * sum over (x, y) != 0 with x^2 - xy + y^2 <= X of chi(x + y w) / (x^2 - xy + y^2)^s,
          in Arb (python-flint). The tail is bounded rigorously by the trivial-character tail
          zeta(s) L(s, chi_-3) - (its own partial sum), which dominates |tail| for every chi with |chi| <= 1.
  DIR  -- independent: the Dirichlet factorization L(s, psi o N) = L(s, psi) L(s, psi chi_-3) (Prop.
          prop:hecke-dirichlet-transfer, paper.tex l.6733-6751; exact here because the modulus 7 is prime to 3),
          each Dirichlet L computed in Arb as q^(-s) sum_a chi(a) zeta(s, a/q).

Characters: modulus O (period 1 and 2) and modulus (7) with chi = psi^i(N(alpha) mod 7), i = 0..5
(period 7 and 14). The structure of (O/7)^x and the units is checked by enumeration first.
Usage: .venv/Scripts/python src/hecke_numeric.py > results/2026-10-20-statement-checks/hecke-numeric-v2.txt
(v2, 2026-10-20: per-list caches and the exact g0 test fixed; v1 output kept as hecke-numeric.txt)
"""
import cmath
import math
import sys
import time

import flint
import mpmath as mp

mp.mp.dps = 30
TAU = 2 * math.pi

# ---------- arithmetic in O = Z[w], w^2 + w + 1 = 0, elements as (x, y) = x + y w ----------
def mul(a, b):
    (x1, y1), (x2, y2) = a, b
    # (x1 + y1 w)(x2 + y2 w) = x1x2 + (x1y2 + x2y1) w + y1y2 w^2,  w^2 = -1 - w
    return (x1 * x2 - y1 * y2, x1 * y2 + x2 * y1 - y1 * y2)

def norm(a):
    x, y = a
    return x * x - x * y + y * y

UNITS = [(1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (1, 1)]  # 1, -1, w, -w, w^2 = -1-w, -w^2 = 1+w

def check_structure():
    out = []
    for u in UNITS:
        assert norm(u) == 1
    # O/7 = {x + y w : x, y mod 7}; units of O/7 are the classes with N not = 0 mod 7 (7 splits, O/7 = F7 x F7)
    cls = [(x, y) for x in range(7) for y in range(7)]
    phi = lambda a: ((a[0] + 2 * a[1]) % 7, (a[0] + 4 * a[1]) % 7)  # w -> 2, w -> 4: roots of t^2+t+1 mod 7
    assert all((2 * 2 + 2 + 1) % 7 == 0 for _ in [0]) and (4 * 4 + 4 + 1) % 7 == 0
    assert len({phi(a) for a in cls}) == 49  # phi is a bijection O/7 -> F7^2
    # phi is a ring map: check on all pairs
    for a in cls:
        for b in cls:
            m = mul(a, b)
            assert phi((m[0] % 7, m[1] % 7)) == ((phi(a)[0] * phi(b)[0]) % 7, (phi(a)[1] * phi(b)[1]) % 7)
    unitsmod7 = [a for a in cls if norm(a) % 7 != 0]
    img = {(u[0] % 7, u[1] % 7) for u in UNITS}
    out.append(f"(O/7)^x has {len(unitsmod7)} elements (expected 36); the 6 units of O map to {len(img)} distinct classes")
    assert len(unitsmod7) == 36 and len(img) == 6
    # N(alpha) mod 7 = product of the two coordinates of phi
    assert all(norm(a) % 7 == (phi(a)[0] * phi(a)[1]) % 7 for a in cls)
    out.append("quotient (O/7)^x / image(units) has order 6; characters trivial on units = psi^i(N mod 7), i = 0..5 (checked below)")
    return out

# psi: character of (Z/7)^x with psi(3) = exp(2 pi i / 6); 3 generates (Z/7)^x
LOG3 = {pow(3, k, 7): k for k in range(6)}

def psi_pow(i, n):
    n %= 7
    return 0 if n == 0 else cmath.exp(1j * TAU * i * LOG3[n] / 6)

def psi_exp(i, n):
    """exponent class (mod 6) of psi^i(n), or None for 0."""
    n %= 7
    return None if n == 0 else (i * LOG3[n]) % 6

class Char:
    def __init__(self, name, value, expo, trivial):
        self.name, self.value, self.expo, self.trivial = name, value, expo, trivial

def char_top():
    return Char("modulus O (trivial)", lambda a: 1.0, lambda a: 0, True)

def char_mod7(i):
    return Char(f"modulus (7), psi^{i} o N", lambda a: psi_pow(i, norm(a)), lambda a: psi_exp(i, norm(a)), i == 0)

def check_char_mod7(i):
    """residue trivial on units; constant on classes mod 7; multiplicative on O/7."""
    ch = char_mod7(i)
    for u in UNITS:
        assert abs(ch.value(u) - 1) < 1e-15
    cls = [(x, y) for x in range(7) for y in range(7)]
    for a in cls:
        for b in cls:
            m = mul(a, b)
            assert abs(ch.value(m) - ch.value(a) * ch.value(b)) < 1e-12
    for a in cls:
        for k in range(1, 3):
            assert abs(ch.value((a[0] + 7 * k, a[1] - 7 * k)) - ch.value(a)) < 1e-12

# ---------- DEF: the challenge definitions, mirrored ----------
def even_kernel(c, x, tol=mp.mpf(10) ** -45):
    # evenKernel c x = sum_n exp(-pi (n + c)^2 x), c in R/Z
    c = mp.mpf(c) - mp.floor(c)
    s, n = mp.mpf(0), 0
    while True:
        t1 = mp.e ** (-mp.pi * (n + c) ** 2 * x)
        t2 = mp.e ** (-mp.pi * (-n - 1 + c) ** 2 * x)
        s += t1 + t2
        if t1 < tol and t2 < tol and n > 0:
            return s
        n += 1

def cos_kernel(c, x, tol=mp.mpf(10) ** -45):
    # cosKernel c x = sum_n cos(2 pi n c) exp(-pi n^2 x)
    s, n = mp.mpf(1), 1
    while True:
        t = mp.e ** (-mp.pi * n ** 2 * x)
        s += 2 * mp.cos(2 * mp.pi * n * c) * t
        if t < tol:
            return s
        n += 1

def components(chi, N, modulus7):
    """the finitePair components: list of (w, xs, ys, u, v) over (a, b, e)."""
    comps = []
    L = N
    for a in range(N):
        for b in range(N):
            w = chi.value((a, b))
            if w == 0:
                continue
            for e in (0, 1):
                xs = mp.mpf(2 * a - b - L * e) / (2 * L)
                ys = mp.mpf(b + L * e) / (2 * L)
                comps.append((mp.mpc(w), xs, ys, mp.mpf(L) ** 2, 3 * mp.mpf(L) ** 2))
    return Comps(comps)

def pair_data(comps):
    # rescale: eps = u^(-1/2); product: eps = (u v)^(-1/2), f0 = f0x * f0y, g0 = 1 * 1; finitePair: eps = 1
    f0 = mp.mpc(0)
    g0 = mp.mpc(0)
    for (w, xs, ys, u, v) in comps:
        epsi = 1 / mp.sqrt(u * v)
        fx = 1 if mp.almosteq(xs, mp.nint(xs), 1e-30) else 0
        fy = 1 if mp.almosteq(ys, mp.nint(ys), 1e-30) else 0
        f0 += w * fx * fy
        g0 += w * epsi
    return f0, g0

class Comps(list):
    """The component list, carrying its own caches of f and g (v2: v1 keyed a global cache by id(), which
    Python reuses after a list is freed, so the h_feq spot checks of v1 could read another list's values)."""
    def __init__(self, items):
        super().__init__(items)
        self.fc, self.gc = {}, {}

def f_val(comps, t):
    if t not in comps.fc:
        comps.fc[t] = _f_val(comps, t)
    return comps.fc[t]

def g_val(comps, t):
    if t not in comps.gc:
        comps.gc[t] = _g_val(comps, t)
    return comps.gc[t]

def _f_val(comps, t):
    return mp.fsum(w * even_kernel(xs, u * t) * even_kernel(ys, v * t) for (w, xs, ys, u, v) in comps)

def _g_val(comps, t):
    return mp.fsum(w / mp.sqrt(u * v) * cos_kernel(xs, t / u) * cos_kernel(ys, t / v) for (w, xs, ys, u, v) in comps)

_COMPS = {}

def L_def(chi, N, s):
    if (chi.name, N) not in _COMPS:
        _COMPS[(chi.name, N)] = components(chi, N, None)
    comps = _COMPS[(chi.name, N)]
    f0, g0 = pair_data(comps)
    s = mp.mpf(s)
    i1 = mp.quad(lambda t: t ** (s - 1) * (f_val(comps, t) - f0), [1, 2, 4, mp.inf])
    i2 = mp.quad(lambda t: t ** (-s) * (g_val(comps, t) - g0), [1, 2, 4, 8, 16, mp.inf])
    lam0 = i1 + i2                      # eps = 1 for finitePair
    lam = lam0 - f0 / s - g0 / (1 - s)  # WeakFEPair.Lambda with k = 1, eps = 1
    return mp.pi ** s / mp.gamma(s) * lam / 6, f0, g0, comps

def feq_spot(comps, x):
    """h_feq: f(1/x) = eps x^k g(x) with eps = 1, k = 1 (direct sums on both sides)."""
    return f_val(comps, 1 / mp.mpf(x)), mp.mpf(x) * g_val(comps, mp.mpf(x))

# ---------- NORM: independent lattice sum, Arb ----------
def L_norm(chi, s, X):
    sa = flint.arb(s)
    tot = flint.acb(0)
    triv = flint.arb(0)
    R = int(math.isqrt(4 * X // 3)) + 2
    for x in range(-R - 1, R + 2):
        for y in range(-R - 1, R + 2):
            n = x * x - x * y + y * y
            if n == 0 or n > X:
                continue
            term = flint.arb(n) ** (-sa)
            triv += term
            v = chi.value((x, y))
            if v != 0:
                e = chi.expo((x, y))
                tot += flint.acb(flint.arb(2 * e) / 6).exp_pi_i() * term if e else term
    return tot / 6, triv / 6

def dirichlet_L(s, q, chi_vals):
    sa = flint.acb(s)
    tot = flint.acb(0)
    for a in range(1, q + 1):
        c = chi_vals(a)
        if c == 0:
            continue
        tot += c * sa.zeta(flint.acb(flint.arb(a) / q))
    return tot * flint.acb(q) ** (-sa)

def chi_m3(n):
    n %= 3
    return 0 if n == 0 else (1 if n == 1 else -1)

def acb_psi(i, n):
    e = psi_exp(i, n)
    return 0 if e is None else flint.acb(flint.arb(2 * e) / 6).exp_pi_i()

def L_dir(chi_kind, i, s):
    if chi_kind == "top":
        z = flint.acb(s).zeta()
        return z * dirichlet_L(s, 3, lambda a: chi_m3(a))
    return dirichlet_L(s, 7, lambda a: acb_psi(i, a)) * dirichlet_L(s, 21, lambda a: acb_psi(i, a) * chi_m3(a))

def main():
    flint.ctx.prec = 200
    t0 = time.time()
    print("Hecke L-function numerical check (COMPUTED, numerical; not a proof)")
    print(f"python {sys.version.split()[0]}, python-flint {flint.__version__}, mpmath {mp.__version__}, mp.dps {mp.mp.dps}, arb prec {flint.ctx.prec}")
    for line in check_structure():
        print(line)
    for i in range(6):
        check_char_mod7(i)
    print("checked by enumeration: each psi^i o N is trivial on the 6 units, multiplicative on O/7, constant on classes mod 7")
    S_POINTS = [2, 3, "5/2"]
    X = 40000
    cases = [("top", 0, char_top(), [1, 2])] + [("mod7", i, char_mod7(i), [7, 14]) for i in (0, 1, 2, 3)]
    print()
    print(f"NORM truncation: x^2 - xy + y^2 <= {X}; |tail| <= trivial tail = zeta(s)L(s,chi_-3) - partial sum (Arb)")
    for kind, i, chi, periods in cases:
        print()
        print(f"== {chi.name}")
        for N in periods:
            if (chi.name, N) not in _COMPS:
                _COMPS[(chi.name, N)] = components(chi, N, None)
            comps = _COMPS[(chi.name, N)]
            f0, g0 = pair_data(comps)
            # exact g0 check: count exponent classes of sum over (a, b) in [0, N)^2 of chi(a + b w)
            counts = [0] * 6
            for a in range(N):
                for b in range(N):
                    e = chi.expo((a, b))
                    if e is not None:
                        counts[e] += 1
            # exact test (v2): sum_k c_k z^k with z = exp(2 pi i/6) is 0 iff 2*Re = 2c0+c1-c2-2c3-c4+c5 = 0
            # and (2/sqrt 3)*Im = c1+c2-c4-c5 = 0 (v1 wrongly required all six counts equal)
            exact_zero = (2 * counts[0] + counts[1] - counts[2] - 2 * counts[3] - counts[4] + counts[5] == 0
                          and counts[1] + counts[2] - counts[4] - counts[5] == 0)
            print(f"   period {N}: {len(comps)} components; f0 = {mp.nstr(f0, 6)}; g0 = {mp.nstr(g0, 6)}; "
                  f"exponent counts of sum_(a,b) chi(a+bw) = {counts} ({'sum exactly 0 => g0 = 0' if exact_zero else 'sum nonzero'})")
            fa, fb = feq_spot(comps, mp.mpf(3) / 2)
            print(f"   h_feq spot check at x = 3/2: f(1/x) = {mp.nstr(fa, 12)}, x g(x) = {mp.nstr(fb, 12)}, diff {mp.nstr(abs(fa - fb), 3)}")
        for s in S_POINTS:
            sv = mp.mpf(eval(s)) if isinstance(s, str) else mp.mpf(s)
            sa = flint.arb(5) / 2 if s == "5/2" else flint.arb(s)
            norm_part, triv_part = L_norm(chi, sa, X)
            ref_triv = L_dir("top", 0, sa)
            tail = (ref_triv.real - triv_part)
            dref = L_dir(kind, i, sa)
            print(f"   s = {s}:")
            print(f"     DIR  {dref.str(18, radius=False)}  (Arb radius {flint.arb(dref.real.rad()).str(2)})")
            print(f"     NORM {norm_part.str(18, radius=False)}  (+ tail, |tail| <= {tail.str(3, radius=False)})")
            for N in periods:
                v, f0, g0, _ = L_def(chi, N, sv)
                dv = flint.acb(str(mp.re(v)), str(mp.im(v)))
                diff_dir = abs(complex(mp.re(v), mp.im(v)) - complex(float(dref.real.mid()), float(dref.imag.mid())))
                diff_norm = abs(complex(mp.re(v), mp.im(v)) - complex(float(norm_part.real.mid()), float(norm_part.imag.mid())))
                print(f"     DEF  period {N:2d}: {mp.nstr(v, 18)}   |DEF-DIR| = {diff_dir:.2e}   |DEF-NORM| = {diff_norm:.2e}")
        sys.stdout.flush()
    print()
    print(f"total time {time.time() - t0:.0f} s")

if __name__ == "__main__":
    main()
