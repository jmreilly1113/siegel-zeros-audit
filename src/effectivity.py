"""Explicit constant for "Uniform exclusion of Landau-Siegel zeros" (docs/effectivity/derivation.md, step 3).

Every inequality claimed proved is evaluated in Arb ball arithmetic (python-flint) with exact rational inputs.
Floating point is used only to *search* for good parameters; the reported values are then certified in Arb.

Master inequality (derivation.md section 5). If a real zero with delta = (1 - beta) log q exists, then
  1 <= t1 + t2 + t3 + t4 + t5 + C_delta * delta * lambda,
  t1 = 3/4 (1 + rho_H)                 rho_H = 7,226,112 / H          (Lemma 6, c0 = 1/(4*97^2), C0 = 192)
  t2 = (C_ell + (1 + rho_H)/2) / lambda   C_ell = e/4 + c_q            ((2.1)-(2.2) explicit; c_q = 1/2)
  t3 = (C_H(U) + (1 + rho_H) log 8) / L    C_H = log H + 1/(2 log H) + 1/(2L) + (e/2) kappa
  t4 = C_theta 4*97^2 / (H^(2/3) L)        C_theta = 1 + 7.5e-7       (Platt-Trudgian Cor. 2)
  t5 = 6*97^2 / (H^(2/3) U)
with lambda = L/ell, L = log U = (4/3) log N, N = ceil(q^gamma), kappa = psi(3/2)/2 - (log pi)/2.
For q >= q0: lambda in [lam_lo, lam_hi] = [4g/3, 4g/3 + (4/3) log(1 + q0^-g)/log q0], L >= lam_lo log q0,
U >= q0^(4g/3); t2..t5 are decreasing in L and lambda; the delta term is largest at lam_hi.
So every zero with q >= q0 (q != 8) has delta > delta0 := (1 - T_up) / (C_delta lam_hi),
T_up = t1 + t2(lam_lo) + t3(L_lo) + t4(L_lo) + t5(U_lo).

Usage: .venv/Scripts/python -I src/effectivity.py [--quick]
"""
import math
import sys
from fractions import Fraction as Fr

import flint
from flint import arb

flint.ctx.prec = 256

R97 = 97 ** 2
RATIO = 768 * R97  # C0/c0 = 192 * 4 * 97^2 = 7,226,112


def floor_sci(v, digits=11):
    """lower endpoint of arb v, rounded DOWN to `digits` significant digits, as a string 'd.ddd...e-XX' (v > 0)"""
    man, ex = v.lower().man_exp()
    x = Fr(int(man)) * (Fr(2) ** int(ex))
    assert x > 0
    k = len(str(x.numerator // x.denominator)) - 1 if x >= 1 else -len(str(x.denominator // x.numerator))
    while Fr(10) ** k > x:
        k -= 1
    while Fr(10) ** (k + 1) <= x:
        k += 1
    m = int(x / Fr(10) ** (k - digits + 1))  # floor, x > 0
    s = str(m)
    return f"{s[0]}.{s[1:]}e{k:+03d}"


def A(x):
    """exact rational (Fraction or int) -> arb"""
    if isinstance(x, Fr):
        return arb(x.numerator) / arb(x.denominator)
    return arb(x)


E_ = arb(1).exp()
PI = arb.pi()
EULER = arb.const_euler()
LOG2 = arb(2).log()
PSI32 = 2 - EULER - 2 * LOG2          # psi(3/2) = 2 - gamma - 2 log 2
KAPPA = PSI32 / 2 - PI.log() / 2      # kappa = psi(3/2)/2 - (log pi)/2  (< 0, checked below)


class Config:
    """Inputs; defaults are derivation.md. Switches reproduce the 2026-10-08 inputs for the reconciliation."""

    def __init__(self, c_q="half", use_kappa=True, theta="PT", mertens_H="RS6", fifth_exact=True):
        self.c_q = c_q            # 'half' (c_q = 1/2), 'one' (paper/Joe: 1), 'old' (ln2/(2 ell) + 1/3)
        self.use_kappa = use_kappa
        self.theta = theta        # 'PT' (1 + 7.5e-7) or 'RS9' (1.01624)
        self.mertens_H = mertens_H  # 'RS6': log H + E + 1/(2 log H) (E cancels); 'old': sum < log H (unsourced I5)
        self.fifth_exact = fifth_exact

    def c_theta(self):
        return A(Fr(1) + Fr(75, 10 ** 8)) if self.theta == "PT" else A(Fr(101624, 100000))


def delta0(cfg, q0, g, H):
    """Arb lower-bound ball for delta0 at q0 (integer), gamma g (Fraction), H (int >= 319). Returns (delta0, parts)."""
    assert H >= 319 and isinstance(H, int)
    l0 = arb(q0).log()
    gA = A(g)
    lam_lo = 4 * gA / 3
    lam_hi = lam_lo + (4 * (1 + arb(q0) ** (-gA)).log()) / (3 * l0)
    L_lo = lam_lo * l0
    U_lo = (L_lo).exp()
    rho = A(Fr(RATIO, H))
    H23 = arb(H) ** (A(Fr(2, 3)))
    # c_q * ell / L handled through C_ell / lambda; the 'old' option has an ell-free part ln2/2 that goes into C_H
    if cfg.c_q == "half":
        C_ell, extra_const = E_ / 4 + A(Fr(1, 2)), arb(0)
    elif cfg.c_q == "one":
        C_ell, extra_const = E_ / 4 + 1, arb(0)
    else:
        C_ell, extra_const = E_ / 4 + A(Fr(1, 3)), LOG2 / 2
    C_delta = E_ / 2
    logH = arb(H).log()
    if cfg.mertens_H == "RS6":
        CH = logH + 1 / (2 * logH) + 1 / (2 * L_lo)
    else:  # old: lower bound at X keeps E and -1/(2 log X); upper at H by 'sum < log H'
        E_M = A(Fr(-13325822757, 10 ** 10)).union(A(Fr(-13325822758, 10 ** 10)))  # E = -1.33258227573...
        CH = logH - E_M + 1 / (2 * L_lo)
    if cfg.use_kappa:
        CH = CH + C_delta * KAPPA  # (e/2) kappa, negative
    CH = CH + extra_const
    t1 = A(Fr(3, 4)) * (1 + rho)
    t2 = (C_ell + (1 + rho) / 2) / lam_lo
    t3 = (CH + (1 + rho) * A(Fr(3)) * LOG2) / L_lo
    t4 = cfg.c_theta() * 4 * R97 / (H23 * L_lo)
    t5 = (6 * R97 / (H23 * U_lo)) if cfg.fifth_exact else arb(0)
    T = t1 + t2 + t3 + t4 + t5
    d0 = (1 - T) / (C_delta * lam_hi)
    return d0, dict(t1=t1, t2=t2, t3=t3, t4=t4, t5=t5, T=T, lam_lo=lam_lo, lam_hi=lam_hi, L_lo=L_lo, U_lo=U_lo,
                    CH=CH, C_ell=C_ell)


def side_conditions(q0, g, H):
    """SC2-SC5, SC9 for every q >= q0 with N = ceil(q^g): returns list of (name, certified bool)."""
    l0 = arb(q0).log()
    gA = A(g)
    logN_lo = gA * l0                      # N >= q^g >= q0^g
    out = []
    out.append(("SC2 H >= 319", H >= 319))
    out.append(("SC3 N >= H (log N >= g log q0 > log H)", bool(logN_lo > arb(H).log())))
    # SC4: H^(2/3) N^(4/3) >= 2*97^2; N >= H gives H^2 >= 2*97^2 when H >= 138
    out.append(("SC4 H^(2/3)N^(4/3) >= 2*97^2 (via N >= H and H^2 >= 2*97^2)", H * H >= 2 * R97))
    L_lo = 4 * logN_lo / 3
    out.append(("SC5 U >= 3 (L >= log 3)", bool(L_lo > arb(3).log())))
    out.append(("SC9 s = 1 + 1/L <= 2 (L >= 1)", bool(L_lo > 1)))
    out.append(("kappa < 0", bool(KAPPA < 0)))
    return out


# ---------- Lemma 12, final elementary inequality, for all sigma > 1 ----------
def lemma12_check():
    """Prove phi(s) := 1/(2s-1) - [1/(s-1) - (1 - 2^-s)/s - 3^(1-s)/(s-1)] > 0 for all s > 1.

    (i)  1 < s <= 1.01, t = s - 1: (1 - 3^-t)/t <= log 3 (since 1 - e^-u <= u), and (1 - 2^-s)/s >= 1/(2(1+t)),
         so bracket <= log 3 - 1/(2(1+t)) <= log 3 - 1/2.02; and 1/(2s-1) >= 1/1.02. Need log 3 - 1/2.02 < 1/1.02.
    (ii) 1.01 <= s <= 5: Arb on a subdivision of [1.01, 5] (interval balls), phi > 0 on each piece.
    (iii) s >= 5: bracket = [1 + (s-1)2^-s]/(s(s-1)) - 3^(1-s)/(s-1) <= 2/(s(s-1)) since (s-1)2^-s <= 1,
         and 2/(s(s-1)) < 1/(2s-1) iff s^2 - 5s + 2 > 0, true for s >= 5 (25 - 25 + 2 > 0, increasing).
    """
    log3 = arb(3).log()
    ok1 = bool(log3 - 1 / A(Fr(202, 100)) < 1 / A(Fr(102, 100)))

    def phi(s):
        return 1 / (2 * s - 1) - ((1 - arb(3) ** (1 - s)) / (s - 1) - (1 - arb(2) ** (-s)) / s)

    a, b, n = Fr(101, 100), Fr(5), 4000
    ok2, worst = True, None
    for i in range(n):
        lo = a + (b - a) * i / n
        hi = a + (b - a) * (i + 1) / n
        s = A(lo).union(A(hi))  # ball containing [lo, hi]
        v = phi(s)
        if not v > 0:
            ok2 = False
        worst = v if worst is None or v.lower() < worst.lower() else worst
    ok3 = (25 - 25 + 2 > 0)  # s^2 - 5s + 2 at s = 5, and derivative 2s - 5 > 0 for s >= 5
    return ok1, ok2, ok3, worst


def float_search(cfg, q0, H_fixed=None):
    """EXPLORATORY float search for (gamma, H) maximizing delta0 (mirrors delta0 in floats)."""
    e, l0 = math.e, math.log(q0)
    kap = float(KAPPA.mid())
    best = (-1, None, None)
    Hs = [H_fixed] if H_fixed else sorted({int(10 ** (x / 20)) for x in range(50, 260)} | {319})
    for H in Hs:
        if H < 319:
            continue
        rho = RATIO / H
        for gi in range(1, 4000):
            g = gi * 0.1
            lam = 4 * g / 3
            L = lam * l0
            if g * l0 <= math.log(H):
                continue
            Cell = e / 4 + (0.5 if cfg.c_q == "half" else 1.0 if cfg.c_q == "one" else 1 / 3)
            CH = math.log(H) + 1 / (2 * math.log(H)) + 1 / (2 * L) + (e / 2 * kap if cfg.use_kappa else 0)                 + (math.log(2) / 2 if cfg.c_q == "old" else 0)
            T = 0.75 * (1 + rho) + (Cell + (1 + rho) / 2) / lam + (CH + (1 + rho) * math.log(8)) / L \
                + 1.0000008 * 4 * R97 / (H ** (2 / 3) * L)
            d = (1 - T) / (e / 2 * lam)
            if d > best[0]:
                best = (d, g, H)
    return best


def certify(cfg, q0, g, H, label):
    d0, parts = delta0(cfg, q0, g, H)
    sc = side_conditions(q0, g, H)
    lo = floor_sci(d0) if d0 > 0 else None
    return dict(label=label, q0=q0, g=g, H=H, d0=d0, d0_lower=lo, parts=parts, sc=sc)


def fmt(r):
    p = r["parts"]
    lines = [f"[{r['label']}] q0 = {r['q0']}, gamma = {r['g']} (= {float(r['g']):.6g}), H = {r['H']}",
             f"   lambda in [{p['lam_lo'].str(8)}, {p['lam_hi'].str(8)}], L >= {p['L_lo'].str(8)}",
             f"   t1 = {p['t1'].str(10)}  t2 = {p['t2'].str(10)}  t3 = {p['t3'].str(10)}",
             f"   t4 = {p['t4'].str(10)}  t5 = {p['t5'].str(5)}  sum T = {p['T'].str(12)}",
             f"   delta0 = {r['d0'].str(15)}   certified: delta0 > {r['d0_lower']}" if r["d0_lower"] else "   delta0 not positive",
             "   side conditions: " + "; ".join(f"{n}: {'OK' if ok else 'FAIL'}" for n, ok in r["sc"])]
    return "\n".join(lines)


def main():
    quick = "--quick" in sys.argv
    print("Explicit constant for the Siegel paper (src/effectivity.py; Arb prec 256 bits)")
    print(f"python {sys.version.split()[0]}, python-flint {flint.__version__}")
    print(f"constants: e = {E_.str(20)}, gamma = {EULER.str(20)}, psi(3/2) = {PSI32.str(20)}, kappa = {KAPPA.str(20)}")
    ok1, ok2, ok3, worst = lemma12_check()
    print(f"Lemma 12 final inequality, all s > 1: (i) (1,1.01]: {ok1}; (ii) [1.01,5] Arb, 4000 pieces: {ok2} "
          f"(min lower bound of phi > {floor_sci(worst, 4)}); (iii) s >= 5: {ok3}")
    results = []
    for cname, cfg in [("approved inputs (c_q = 1/2)", Config()),
                       ("best valid inputs (c_q: ln2/(2 ell) + 1/3, derivation (I6) option 3)", Config(c_q="old"))]:
        print()
        print("===== " + cname)
        for label, q0 in [("Platt regime: q > 4*10^5", 400001), ("LZZ regime: q > 10^10", 10 ** 10 + 1),
                          ("argument alone: q >= 3, q != 8", 3)]:
            d, g, H = float_search(cfg, q0)
            r = certify(cfg, q0, Fr(round(g * 10), 10), H, label + " [optimized over gamma, H]")
            results.append((cname, r)); print(fmt(r))
            d2, g2, _ = float_search(cfg, q0, H_fixed=86713344)
            r = certify(cfg, q0, Fr(round(g2 * 10), 10), 86713344, label + " [paper's H]")
            results.append((cname, r)); print(fmt(r))
    cfg = Config()
    # reconciliation with docs/explicit-constant.md (2026-10-08): old inputs
    old = Config(c_q="old", use_kappa=True, theta="RS9", mertens_H="old", fifth_exact=True)
    print("\nReconciliation with docs/explicit-constant.md (old inputs: c_q = ln2/(2l)+1/3, kappa kept, theta RS Thm 9,"
          " primes <= H by the unsourced 'sum < log H', H = 86,713,344, its t = L/ell):")
    for label, q0, t in [("all q >= 3", 3, Fr(2269, 10)), ("q > 4e5", 400001, Fr(3448, 100)), ("q > 1e10", 10 ** 10 + 1, Fr(2660, 100))]:
        gF = 3 * t / 4
        r_old = certify(old, q0, gF, 86713344, f"old inputs, {label}, t = {float(t)}")
        r_new = certify(cfg, q0, gF, 86713344, f"new inputs, {label}, same t and H")
        print(fmt(r_old)); print(fmt(r_new))
    return results


if __name__ == "__main__":
    main()
