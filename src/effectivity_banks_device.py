"""UNREVIEWED. Explicit constant with Banks's primes-dividing-q device (docs/effectivity/derivation-banks-device.md).

Same pipeline as src/effectivity.py (Arb ball arithmetic at exact rational parameters, printed bounds = Arb lower
endpoint rounded down), with two changes, both from Banks, arXiv:2610.15483v1, Lemma 2.1:
  (D1) primes dividing q: instead of (I6) sum_{p|q} log p/p <= c_q ell, the primes p | q stay in the
       Lambda(n)(1+chi(n)) sum with weight 1 ((2.5), (2.6)), and only those with p > H cost
       (1/2) sum_{p>H, p|q} log p/p <= ell/(2H) ((2.8) and the bound after it). C_ell = e^s/4 + c_dev, c_dev = 1/(2H).
  (D2) shift: sigma = 1 + s/log X with s in (0, 2] (Banks's lambda), so C_delta = e^s/(2 s^2), the ell/2 term carries
       e^s/4, and kappa enters as (e^s/2) kappa. s = 1 gives derivation.md's constants.
Everything else (Mertens with E cancelling, theta, Lemma 6, Archimedean bound, the master inequality) is unchanged.
Usage: .venv/Scripts/python -I src/effectivity_banks_device.py
"""
import math
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint  # noqa: E402
from flint import arb  # noqa: E402

import effectivity as ef  # noqa: E402

A, R97, RATIO, KAPPA, LOG2, floor_sci = ef.A, ef.R97, ef.RATIO, ef.KAPPA, ef.LOG2, ef.floor_sci
C_THETA = Fr(1) + Fr(75, 10 ** 8)       # Platt-Trudgian Cor. 2, as in effectivity.py
LABEL = "UNREVIEWED"


def delta0(q0, g, H, s, c_dev=None):
    """Arb ball: every real zero with q >= q0 (q != 8) and N = ceil(q^g) has delta > delta0. UNREVIEWED.
    s: shift (Fraction in (0, 2]); c_dev: coefficient of ell for primes p > H dividing q (default 1/(2H))."""
    assert isinstance(H, int) and H >= 319 and 0 < s <= 2
    c_dev = Fr(1, 2 * H) if c_dev is None else c_dev
    l0 = arb(q0).log()
    gA, sA = A(g), A(s)
    es = sA.exp()
    C_delta = es / (2 * sA * sA)                    # Banks (2.3): C1 >= e^s/(2 s^2)
    C_ell = es / 4 + A(c_dev)                       # Banks (2.4): C2 + 1/(2H), C2 >= e^s/4
    lam_lo = 4 * gA / 3
    lam_hi = lam_lo + (4 * (1 + arb(q0) ** (-gA)).log()) / (3 * l0)
    L_lo = lam_lo * l0
    U_lo = L_lo.exp()
    rho = A(Fr(RATIO, H))
    H23 = arb(H) ** A(Fr(2, 3))
    logH = arb(H).log()
    CH = logH + 1 / (2 * logH) + 1 / (2 * L_lo) + es / 2 * KAPPA   # (I4)-(I5) with E cancelling; kappa < 0 kept
    t1 = A(Fr(3, 4)) * (1 + rho)
    t2 = (C_ell + (1 + rho) / 2) / lam_lo
    t3 = (CH + (1 + rho) * 3 * LOG2) / L_lo
    t4 = A(C_THETA) * 4 * R97 / (H23 * L_lo)
    t5 = 6 * R97 / (H23 * U_lo)
    T = t1 + t2 + t3 + t4 + t5
    d0 = (1 - T) / (C_delta * lam_hi)
    return d0, dict(t1=t1, t2=t2, t3=t3, t4=t4, t5=t5, T=T, lam_lo=lam_lo, lam_hi=lam_hi, L_lo=L_lo, C_delta=C_delta,
                    C_ell=C_ell, CH=CH)


def side_conditions(q0, g, H, s):
    """effectivity.side_conditions plus the conditions the shift and the device need, for every q >= q0."""
    out = ef.side_conditions(q0, g, H)
    L_lo = 4 * A(g) * arb(q0).log() / 3
    out.append(("D2 0 < s <= 2 (Banks Lemma 2.1: lambda in (0,2])", 0 < s <= 2))
    out.append(("D2 sigma = 1 + s/L <= 2, i.e. L >= s (so (sigma+eps)/2 <= 3/2 and the zeta bound applies)", bool(L_lo >= A(s))))
    out.append(("D2 X = U >= 8 (Banks Lemma 2.1 hypothesis), i.e. L >= log 8", bool(L_lo > 3 * LOG2)))
    out.append(("D1 H >= 319 (Mertens upper bound at H) and H >= 3 ((log t)/t decreasing for t >= e)", H >= 319))
    return out


def fsearch(q0, H=None, s=None):
    """EXPLORATORY float search over s (step 1/20), gamma (step 1/10), H (grid); mirrors delta0."""
    l0, kap = math.log(q0), float(KAPPA.mid())
    best = None
    for ss in ([s] if s is not None else [Fr(i, 20) for i in range(4, 41)]):
        sf = float(ss)
        es = math.exp(sf)
        Cd, C2 = es / (2 * sf * sf), es / 4
        for Hh in ([H] if H else sorted({int(10 ** (x / 40)) for x in range(100, 520)} | {319, 86713344})):
            if Hh < 319:
                continue
            rho, h23, lh = RATIO / Hh, Hh ** (2 / 3), math.log(Hh)
            for gi in range(10, 4000):
                gf = gi / 10
                if gf * l0 <= lh:
                    continue
                lam = 4 * gf / 3
                L = lam * l0
                if L < sf:
                    continue
                CH = lh + 1 / (2 * lh) + 1 / (2 * L) + es / 2 * kap
                T = 0.75 * (1 + rho) + (C2 + 1 / (2 * Hh) + (1 + rho) / 2) / lam + (CH + (1 + rho) * math.log(8)) / L \
                    + 1.00000075 * 4 * R97 / (h23 * L)
                d = (1 - T) / (Cd * lam)
                if best is None or d > best[0]:
                    best = (d, Fr(gi, 10), Hh, ss)
    return best


def main():
    flint.ctx.prec = 256
    print(f"{LABEL}: explicit constant with Banks's primes-dividing-q device (src/effectivity_banks_device.py; Arb prec 256 bits)")
    print(f"python {sys.version.split()[0]}, python-flint {flint.__version__}")
    print(f"{LABEL}: not part of docs/effectivity/note.md or note-v2. Derivation: docs/effectivity/derivation-banks-device.md")
    ok1, ok2, ok3, worst = ef.lemma12_check()
    print(f"Lemma 12 final inequality, all s > 1 (reused from effectivity.py): (i) {ok1}; (ii) {ok2} (min lower bound of phi > "
          f"{floor_sci(worst, 4)}); (iii) {ok3}")
    old = {400001: ("3.3992904026e-03", Fr(201, 10), 1995262314), 10 ** 10 + 1: ("4.4673780338e-03", Fr(153, 10), 2818382931)}
    for label, q0 in [("Platt regime: q > 4*10^5", 400001), ("LZZ regime: q > 10^10", 10 ** 10 + 1)]:
        _, g, H, s = fsearch(q0)
        d, p = delta0(q0, g, H, s)
        sc = side_conditions(q0, g, H, s)
        print(f"\n[{label}] {LABEL}")
        print(f"   q0 = {q0}, gamma = {g}, H = {H}, shift s = {s}, c_dev = 1/(2H)")
        print(f"   C_delta = {p['C_delta'].str(10)}  C_ell = {p['C_ell'].str(10)}  C_H = {p['CH'].str(10)}")
        print(f"   lambda in [{p['lam_lo'].str(8)}, {p['lam_hi'].str(8)}], L >= {p['L_lo'].str(8)}")
        print(f"   t1 = {p['t1'].str(10)}  t2 = {p['t2'].str(10)}  t3 = {p['t3'].str(10)}  t4 = {p['t4'].str(8)}  t5 = {p['t5'].str(4)}  T = {p['T'].str(12)}")
        print(f"   delta0 = {d.str(15)}   certified: delta0 > {floor_sci(d)}   ({LABEL})")
        print("   side conditions (at q0, implied for all q >= q0): " + "; ".join(f"{n}: {'OK' if ok else 'FAIL'}" for n, ok in sc))
        assert all(ok for _, ok in sc)
        print(f"   note.md value for this regime (certified): {old[q0][0]}; ratio new/old = {(d / A(Fr(old[q0][0]))).str(6)}")
        d1, _ = delta0(q0, old[q0][1], old[q0][2], Fr(1))
        print(f"   device alone at note.md's (gamma, H) and shift 1: delta0 > {floor_sci(d1)}")


if __name__ == "__main__":
    main()
