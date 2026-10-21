"""UNREVIEWED. note-v2's master inequality with Banks's two devices, per refs/improved-constants-from-banks-devices.txt.

Input file (third-party, UNREVIEWED; read, not executed): refs/improved-constants-from-banks-devices.txt,
sha256 a680b88ef21046ac9fe0c812bc0f23b8209aa0330cdc01bea1fe2a7683627cd7. Its master inequality (lines 73-80):

  1 <= (3/4)(1+rho_H) + [e^s/4 + c + (1/2)(1+rho_H)]/lambda + (e^s/(2 s^2)) delta lambda
       + [C_H + (1+rho_H) log 8]/L + (1+7.5e-7) 4*97^2/(H^{2/3} L) + 6*97^2/(H^{2/3} U),
  C_H = log H + 1/(2 log H) + 1/(2L) + (e^s/2) kappa,

with c = 1/(2H) (device 2, Banks's (1/2)S_0 device) or c = c_q (note-v2), and s the shift (device 1; note-v2 s = 1).
This is the same formula as src/effectivity_banks_device.py; this module adds the device switch, the c_q options of
note-v2, and a refined search. Arb ball arithmetic at exact rationals; printed bounds = lower endpoint rounded down.
Usage: .venv/Scripts/python -I src/effectivity_banks_devices.py
"""
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint  # noqa: E402
from flint import arb  # noqa: E402

import effectivity as ef  # noqa: E402

A, R97, RATIO, KAPPA, floor_sci = ef.A, ef.R97, ef.RATIO, ef.KAPPA, ef.floor_sci
LABEL = "UNREVIEWED"
INPUT_SHA256 = "a680b88ef21046ac9fe0c812bc0f23b8209aa0330cdc01bea1fe2a7683627cd7"
NOTE_V2 = {10 ** 10 + 1: ("old", Fr(153, 10), 2818382931, "4.4673780338e-03"),
           400001: ("old", Fr(201, 10), 1995262314, "3.3992904026e-03"),
           3: ("half", Fr(671, 5), 1122018454, "5.0425352961e-04")}


def delta0(q0, g, H, s=Fr(1), device=True, cq="old"):
    """Arb ball for delta0. device=True: c = 1/(2H). device=False: c = c_q ('old' = ln2/(2 log q0) + 1/3, 'half' = 1/2)."""
    assert isinstance(H, int) and H >= 319 and 0 < s <= 2
    l0 = arb(q0).log()
    gA, sA = A(g), A(s)
    es = sA.exp()
    lam_lo = 4 * gA / 3
    lam_hi = lam_lo + 4 * (1 + arb(q0) ** (-gA)).log() / (3 * l0)
    L = lam_lo * l0
    U = L.exp()
    rho = A(Fr(RATIO, H))
    if device:
        c = A(Fr(1, 2 * H))
    elif cq == "half":
        c = A(Fr(1, 2))
    else:
        c = arb(2).log() / (2 * l0) + A(Fr(1, 3))
    Cl = es / 4 + c
    logH = arb(H).log()
    CH = logH + 1 / (2 * logH) + 1 / (2 * L) + es / 2 * KAPPA
    T = (A(Fr(3, 4)) * (1 + rho) + (Cl + (1 + rho) / 2) / lam_lo + (CH + (1 + rho) * 3 * arb(2).log()) / L
         + A(Fr(1) + Fr(75, 10 ** 8)) * 4 * R97 / (arb(H) ** A(Fr(2, 3)) * L) + 6 * R97 / (arb(H) ** A(Fr(2, 3)) * U))
    C1 = es / (2 * sA * sA)
    return (1 - T) / (C1 * lam_hi), dict(T=T, C1=C1, Cl=Cl, CH=CH, lam_lo=lam_lo, lam_hi=lam_hi, L=L)


def side_conditions(q0, g, H, s):
    """The brief's list, at q0 and (by monotonicity in q) for all q >= q0, with N = ceil(q^g)."""
    l0 = arb(q0).log()
    L_lo = 4 * A(g) * l0 / 3          # L = (4/3) log N >= (4/3) g log q >= (4/3) g log q0
    return [("H >= 319", H >= 319),
            ("N >= H (g log q0 > log H)", bool(A(g) * l0 > arb(H).log())),
            ("H^(2/3) N^(4/3) >= 2*97^2 (via N >= H: H^2 >= 2*97^2)", H * H >= 2 * R97),
            ("U >= 3 (L >= log 3)", bool(L_lo > arb(3).log())),
            ("L >= s", bool(L_lo >= A(s))),
            ("sigma = 1 + s/L in (1, 2] (s > 0 and L >= s)", 0 < s and bool(L_lo >= A(s))),
            ("0 < s <= 2 (Banks Lemma 2.1)", 0 < s <= 2),
            ("kappa < 0", bool(KAPPA < 0))]


def fgrid(q0, gs, Hs, ss, device=True, cq="old"):
    """EXPLORATORY vectorized float evaluation (mirrors delta0); returns (best value, g, H, s)."""
    l0 = math.log(q0)
    kap = float(KAPPA.mid())
    g = np.asarray([float(x) for x in gs])[:, None]
    Hv = np.asarray(Hs, dtype=float)[None, :]
    best = (-1.0, None, None, None)
    for s in ss:
        sf = float(s)
        es = math.exp(sf)
        lam = 4 * g / 3
        L = lam * l0
        rho = RATIO / Hv
        c = 1 / (2 * Hv) if device else (0.5 if cq == "half" else math.log(2) / (2 * l0) + 1 / 3)
        lh = np.log(Hv)
        CH = lh + 1 / (2 * lh) + 1 / (2 * L) + es / 2 * kap
        T = (0.75 * (1 + rho) + (es / 4 + c + (1 + rho) / 2) / lam + (CH + (1 + rho) * math.log(8)) / L
             + 1.00000075 * 4 * R97 / (Hv ** (2 / 3) * L))
        lam_hi = lam + 4 / 3 * np.log1p(q0 ** (-g)) / l0
        d = (1 - T) / (es / (2 * sf * sf) * lam_hi)
        ok = (g * l0 > lh) & (L >= sf) & (Hv >= 319)
        d = np.where(ok, d, -1.0)
        i = np.unravel_index(np.argmax(d), d.shape)
        if d[i] > best[0]:
            best = (float(d[i]), gs[i[0]], int(Hs[i[1]]), s)
    return best


def search(q0, s_fixed=None, device=True, cq="old"):
    """Coarse grid (gamma step 1/10, H = 10^(h/20), s step 1/20), then refine (gamma 1/100, H x10^(+-1/200), s 1/200)."""
    gs = [Fr(i, 10) for i in range(5, 4000)]
    Hs = sorted({int(10 ** (h / 20)) for h in range(50, 260)} | {319})
    ss = [s_fixed] if s_fixed is not None else [Fr(i, 20) for i in range(2, 41)]
    d, g, H, s = fgrid(q0, gs, Hs, ss, device, cq)
    g2 = [g + Fr(k, 100) for k in range(-10, 11) if g + Fr(k, 100) > 0]
    H2 = sorted({max(319, int(round(H * 10 ** (k / 200)))) for k in range(-20, 21)})
    s2 = [s_fixed] if s_fixed is not None else [s + Fr(k, 200) for k in range(-10, 11) if 0 < s + Fr(k, 200) <= 2]
    return fgrid(q0, g2, H2, s2, device, cq)


def main():
    flint.ctx.prec = 256
    print(f"{LABEL}: note-v2 master inequality with Banks's two devices (src/effectivity_banks_devices.py; Arb prec 256 bits)")
    print(f"python {sys.version.split()[0]}, python-flint {flint.__version__}, numpy {np.__version__}")
    print(f"input: refs/improved-constants-from-banks-devices.txt (UNREVIEWED third-party; sha256 {INPUT_SHA256}; read, not executed)")
    print("\n== Check: s = 1, no device reproduces note-v2's three certified values")
    for q0, (cq, g, H, v2) in NOTE_V2.items():
        d, _ = delta0(q0, g, H, Fr(1), device=False, cq=cq)
        print(f"   q0 {q0}: {floor_sci(d)} vs note-v2 {v2}: {'MATCH' if floor_sci(d) == v2 else 'MISMATCH'}")
        assert floor_sci(d) == v2, "STOP: contradiction with note-v2"
    for label, s_fixed in [("(a) s = 3/2 fixed", Fr(3, 2)), ("(b) s optimized (grid 1/20, refined to 1/200)", None)]:
        print(f"\n== {label}, both devices ({LABEL})")
        for q0 in (10 ** 10 + 1, 400001, 3):
            fd, g, H, s = search(q0, s_fixed)
            d, p = delta0(q0, g, H, s)
            sc = side_conditions(q0, g, H, s)
            assert all(ok for _, ok in sc)
            print(f"   q0 = {q0}: gamma = {g}, H = {H}, s = {s}: delta0 = {d.str(15)}  certified > {floor_sci(d)}  ({LABEL})")
            print(f"      float search value {fd:.10e}; C1 = {p['C1'].str(8)}, C_ell = {p['Cl'].str(10)}, T = {p['T'].str(10)}, "
                  f"lambda in [{p['lam_lo'].str(8)}, {p['lam_hi'].str(8)}]")
            print("      side conditions (at q0, implied for all q >= q0): " + "; ".join(f"{n}: OK" for n, ok in sc))


if __name__ == "__main__":
    main()
