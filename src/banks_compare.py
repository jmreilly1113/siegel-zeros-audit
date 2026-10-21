"""Reconcile our explicit constant (docs/effectivity/note.md) with Banks, arXiv:2610.15483v1 (refs/banks-2610.15483.md).

Every reported value is an Arb ball at exact rational inputs; floats are used only to search for parameters.
Usage: .venv/Scripts/python -I src/banks_compare.py

Part A re-derives Banks's own chain (his Section 7 and Remark "Effectivity") and checks each numeric claim.
Part B evaluates the master inequality (derivation.md section 5) with one switch per point where the two accounts
differ; with all switches at Banks's settings it is exactly his Step 3 inequality, with all at ours it is
src/effectivity.delta0. Part C is the waterfall from his 3.0696e-3 to our 4.467e-3, plus one-at-a-time effects.

Banks's parameters and ours (notation clash): his lambda is the shift in sigma = 1 + lambda/log X (ours is 1);
his omega is our gamma (N = ceil(q^gamma)); our lambda is L/log q = (4/3) log N / log q, about (4/3) gamma.
"""
import math
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint  # noqa: E402
from flint import arb  # noqa: E402

import effectivity as ef  # noqa: E402

A, R97, RATIO, KAPPA, E_, LOG2, floor_sci = ef.A, ef.R97, ef.RATIO, ef.KAPPA, ef.E_, ef.LOG2, ef.floor_sci
H_PAPER = 86713344            # = 9216 * 97^2 = 12 * 7,226,112: Banks's H and the paper's


class Cfg:
    """One switch per difference. Defaults = Banks's accounting (his Section 7)."""

    def __init__(self, shift=Fr(3, 2), pq="banks", kappa=False, mertens_extra=False, theta="2", s1="banks",
                 lam_hi="omega+1"):
        self.shift = shift          # Banks lambda: sigma = 1 + shift/log X. Ours: 1
        self.pq = pq                # primes dividing q: 'banks' (1/(2H) ell, via S_0 in (2.3)); 'half'; 'old' (ours)
        self.kappa = kappa          # keep (e^shift/2) kappa (ours) or discard with the Mertens terms (Banks, (2.4))
        self.mertens_extra = mertens_extra  # keep 1/(2 log H) + 1/(2 L) (ours) or the 1/log H discarded (Banks)
        self.theta = theta          # '2' (Banks: sum_{p<=M} log p <= 2M) or 'PT' (Platt-Trudgian 1 + 7.5e-7)
        self.s1 = s1                # 'banks' (S1 >= N^4 M, (3/2)N^4 log M <= S1) or 'ours' (S1 >= N^4 H^(2/3) M/(4*97^2))
        self.lam_hi = lam_hi        # 'omega+1' (N <= q^(omega+1), Banks (7.1)) or 'tight' (N <= q^g + 1)

    def but(self, **kw):
        c = Cfg(**self.__dict__)
        c.__dict__.update(kw)
        return c


OURS = Cfg(shift=Fr(1), pq="old", kappa=True, mertens_extra=True, theta="PT", s1="ours", lam_hi="tight")
BANKS = Cfg()


def delta0(cfg, q0, g, H):
    """Arb ball: delta > delta0 for every real zero with q >= q0 (q != 8), N = ceil(q^g)."""
    assert isinstance(H, int) and H >= 319
    if cfg.s1 == "banks":       # S1 >= N^4 M needs H^(2/3) >= 4*97^2, i.e. H >= (4*97^2)^(3/2) = 8*97^3
        assert H >= 8 * 97 ** 3
    assert 0 < cfg.shift <= 2   # Lemma 2.1: lambda in (0, 2]
    l0 = arb(q0).log()
    gA, sA = A(g), A(cfg.shift)
    es = sA.exp()
    C1, C2 = es / (2 * sA * sA), es / 4
    lam_lo = 4 * gA / 3
    lam_hi = 4 * (gA + 1) / 3 if cfg.lam_hi == "omega+1" else lam_lo + 4 * (1 + arb(q0) ** (-gA)).log() / (3 * l0)
    L_lo = lam_lo * l0
    U_lo = L_lo.exp()
    rho = A(Fr(RATIO, H))
    H23 = arb(H) ** A(Fr(2, 3))
    logH = arb(H).log()
    if cfg.pq == "banks":
        C_ell, extra = C2 + A(Fr(1, 2 * H)), arb(0)
    elif cfg.pq == "half":
        C_ell, extra = C2 + A(Fr(1, 2)), arb(0)
    else:
        C_ell, extra = C2 + A(Fr(1, 3)), LOG2 / 2
    CH = logH + extra
    if cfg.mertens_extra:
        CH = CH + 1 / (2 * logH) + 1 / (2 * L_lo)
    if cfg.kappa:
        CH = CH + es / 2 * KAPPA
    ct = A(Fr(2)) if cfg.theta == "2" else A(Fr(1) + Fr(75, 10 ** 8))
    t1 = A(Fr(3, 4)) * (1 + rho)
    t2 = (C_ell + (1 + rho) / 2) / lam_lo
    t3 = (CH + (1 + rho) * 3 * LOG2) / L_lo
    if cfg.s1 == "banks":
        t4 = ct / L_lo                      # 2 N^4 M <= 2 S1 (with ct = 2), divided by S1 L
        t5 = 1 / L_lo                       # (3/2) N^4 log M <= S1, divided by S1 L
    else:
        t4 = ct * 4 * R97 / (H23 * L_lo)
        t5 = 6 * R97 / (H23 * U_lo)
    T = t1 + t2 + t3 + t4 + t5
    return (1 - T) / (C1 * lam_hi), dict(t1=t1, t2=t2, t3=t3, t4=t4, t5=t5, T=T, C1=C1, C_ell=C_ell, CH=CH,
                                          lam_lo=lam_lo, lam_hi=lam_hi, L_lo=L_lo)


def fsearch(cfg, q0, H=None, g=None, shift_free=False):
    """EXPLORATORY float search over gamma (step 1/10), H (grid) and optionally the shift (step 1/20)."""
    best = None
    Hs = [H] if H else sorted({int(10 ** (x / 40)) for x in range(100, 520)} | {319, H_PAPER})
    gs = [g] if g is not None else [Fr(i, 10) for i in range(10, 2500)]
    shifts = [Fr(i, 20) for i in range(4, 41)] if shift_free else [cfg.shift]
    l0 = math.log(q0)
    for s in shifts:
        es = math.exp(s)
        C1, C2 = es / (2 * s * s), es / 4
        Cell, extra = {"banks": (None, 0.0), "half": (C2 + 0.5, 0.0), "old": (C2 + 1 / 3, math.log(2) / 2)}[cfg.pq]
        for Hh in Hs:
            if Hh < 319 or (cfg.s1 == "banks" and Hh < 8 * 97 ** 3):
                continue
            rho, h23, lh = RATIO / Hh, Hh ** (2 / 3), math.log(Hh)
            ce = C2 + 1 / (2 * Hh) if cfg.pq == "banks" else Cell
            for gg in gs:
                gf = float(gg)
                if gf * l0 <= lh:   # N >= H
                    continue
                lam = 4 * gf / 3
                L = lam * l0
                lam_hi = 4 * (gf + 1) / 3 if cfg.lam_hi == "omega+1" else lam
                CH = lh + extra + ((1 / (2 * lh) + 1 / (2 * L)) if cfg.mertens_extra else 0) + \
                    (es / 2 * float(KAPPA.mid()) if cfg.kappa else 0)
                ct = 2.0 if cfg.theta == "2" else 1.00000075
                t45 = (ct + 1) / L if cfg.s1 == "banks" else ct * 4 * R97 / (h23 * L)
                T = 0.75 * (1 + rho) + (ce + (1 + rho) / 2) / lam + (CH + (1 + rho) * math.log(8)) / L + t45
                d = (1 - T) / (C1 * lam_hi)
                if best is None or d > best[0]:
                    best = (d, gg, Hh, s)
    return best


def show(label, cfg, q0, g, H):
    d, p = delta0(cfg, q0, g, H)
    lo = floor_sci(d) if d > 0 else "not positive"
    print(f"{label}\n    q0 = {q0}, gamma = {g}, H = {H}, shift = {cfg.shift}: delta0 = {d.str(12)}  certified > {lo}")
    print(f"    t1 {p['t1'].str(6)}  t2 {p['t2'].str(6)}  t3 {p['t3'].str(6)}  t4 {p['t4'].str(6)}  t5 {p['t5'].str(4)}"
          f"  T {p['T'].str(8)}  C1 {p['C1'].str(6)}  lambda in [{p['lam_lo'].str(6)}, {p['lam_hi'].str(6)}]")
    return d


def part_a():
    flint.ctx.prec = 256        # other modules (tests) may lower the global precision
    print("== Part A: Banks's own chain (Section 7, Remark 'Effectivity'), every numeric claim in Arb")
    s = A(Fr(3, 2))
    es = s.exp()
    C1, C2 = 2 * es / 9, es / 4
    kB = arb.pi().log() / 2 - ef.PSI32 / 2                 # Banks's kappa = -(our kappa)
    H = H_PAPER
    logH = arb(H).log()
    omega_real = 8 * (C2 + A(Fr(8, 5)))
    omega = 22
    checks = [
        ("C1 = e^(3/2)/(2 (3/2)^2) = 2 e^(3/2)/9 = 0.99594 (Lemma 2.1)", C1, abs(C1 - es / (2 * s * s)) < A(Fr(1, 10 ** 60)) and C1 < A(Fr(99594, 10 ** 5)) + A(Fr(1, 10 ** 5))),
        ("C2 = e^(3/2)/4 = 1.12043", C2, bool(C2 < A(Fr(112043, 10 ** 5)))),
        ("kappa_Banks = (log pi)/2 - psi(3/2)/2 = 0.5541... > 0", kB, bool(kB > 0) and bool(abs(kB + KAPPA) < A(Fr(1, 10 ** 60)))),
        ("e^(3/2) kappa/2 > 0.277 and 1/log 319 < 0.174 (proof of (2.4))", es * kB / 2, bool(es * kB / 2 > A(Fr(277, 1000))) and bool(1 / arb(319).log() < A(Fr(174, 1000)))),
        ("H = 9216 * 97^2 = 86,713,344 >= 8 * 97^3 = 7,301,384", arb(H), H == 9216 * R97 and H >= 8 * 97 ** 3),
        ("H^(2/3) >= 4 * 97^2 (Lemma 4.2 hypotheses, S1 >= N^4 M)", arb(H) ** A(Fr(2, 3)), bool(arb(H) ** A(Fr(2, 3)) >= 4 * R97)),
        ("768 * 97^2 / H = 1/12 exactly", A(Fr(768 * R97, H)), Fr(768 * R97, H) == Fr(1, 12)),
        ("omega = ceil(8 (C2 + 8/5)) = 22", omega_real, bool(omega_real > 21) and bool(omega_real < 22)),
        ("log q0 = log 10^10 > 23", arb(10 ** 10).log(), bool(arb(10 ** 10).log() > 23)),
        ("log H + 3 + (13/12) log 8 < 24", logH + 3 + A(Fr(13, 12)) * 3 * LOG2, bool(logH + 3 + A(Fr(13, 12)) * 3 * LOG2 < 24)),
        ("1/(2H) + 13/24 + 24/23 < 8/5", A(Fr(1, 2 * H) + Fr(13, 24) + Fr(24, 23)), Fr(1, 2 * H) + Fr(13, 24) + Fr(24, 23) < Fr(8, 5)),
        ("3 (C2 + 8/5)/(4 omega) <= 3/32 (last step)", 3 * (C2 + A(Fr(8, 5))) / (4 * omega), bool(3 * (C2 + A(Fr(8, 5))) / (4 * omega) <= A(Fr(3, 32)))),
    ]
    for name, v, ok in checks:
        print(f"  {'OK  ' if ok else 'FAIL'} {name}: {v.str(10)}")
    d0 = A(Fr(9, 128 * (omega + 1))) / C1
    d0b = 81 / (5888 * es)
    print(f"  delta0 = 9/(128 (omega+1) C1) = {d0.str(15)}; 81/(5888 e^(3/2)) = {d0b.str(15)}; certified > {floor_sci(d0)}")
    print(f"  agrees with Banks's 3.069...e-3: {bool(d0 > A(Fr(3069, 10 ** 6))) and bool(d0 < A(Fr(3070, 10 ** 6)))}; "
          f"supports his stated 3.0e-3: {bool(d0 > A(Fr(3, 1000)))}")
    return all(ok for _, _, ok in checks), d0


def main():
    flint.ctx.prec = 256
    print("Banks comparison (src/banks_compare.py; Arb prec 256 bits)")
    print(f"python {sys.version.split()[0]}, python-flint {flint.__version__}")
    okA, d_banks = part_a()

    print("\n== Part B check: the generalized function at our settings reproduces src/effectivity.delta0")
    for q0, g, H in [(400001, Fr(201, 10), 1995262314), (10 ** 10 + 1, Fr(153, 10), 2818382931)]:
        a, _ = delta0(OURS, q0, g, H)
        b, _ = ef.delta0(ef.Config(c_q="old"), q0, g, H)
        print(f"  q0 {q0}: ours-generalized {a.str(15)} | effectivity {b.str(15)} | overlap {a.overlaps(b)}")

    print("\n== Part B: Banks's Step 3 inequality solved exactly (no 3/32 rounding, no log q > 23 absorption)")
    q0 = 10 ** 10
    show("B1 Banks's accounting, his parameters", BANKS, q0, Fr(22), H_PAPER)

    print("\n== Part C: waterfall, Banks -> ours, q0 = 10^10 (each step keeps the previous switches)")
    steps = [("B1 Banks's Step 3, exact solve", BANKS),
             ("B2 + tight lambda upper end (N <= q^g + 1)", BANKS.but(lam_hi="tight")),
             ("B3 + our S1, S23 bounds (S1 >= N^4 H^(2/3) M/(4*97^2), exact t5)", BANKS.but(lam_hi="tight", s1="ours")),
             ("B4 + Platt-Trudgian theta (1 + 7.5e-7 for 2)", BANKS.but(lam_hi="tight", s1="ours", theta="PT")),
             ("B5 + kappa and the Mertens terms kept", BANKS.but(lam_hi="tight", s1="ours", theta="PT", kappa=True, mertens_extra=True)),
             ("B6 + shift 1 (ours) for 3/2", BANKS.but(lam_hi="tight", s1="ours", theta="PT", kappa=True, mertens_extra=True, shift=Fr(1))),
             ("B7 + our primes-dividing-q bound (c_q = ln2/(2 ell) + 1/3) for Banks's 1/(2H)", OURS)]
    for label, cfg in steps:
        show(label + "  [gamma = 22, H = paper's]", cfg, q0, Fr(22), H_PAPER)
    print("  -- the same steps with gamma free (H = paper's), then gamma and H free:")
    for label, cfg in steps:
        d, g, _, _ = fsearch(cfg, q0, H=H_PAPER)
        show(label + "  [gamma free]", cfg, q0, g, H_PAPER)
    d, g, H, _ = fsearch(OURS, 10 ** 10 + 1)
    show("B8 ours, gamma and H free (note.md LZZ row: 4.4673780338e-3 at gamma 153/10, H 2,818,382,931)", OURS, 10 ** 10 + 1, Fr(153, 10), 2818382931)

    print("\n== Part C: one switch at a time, from OURS (LZZ row) back to Banks's choice; gamma, H re-optimized")
    base, _ = delta0(OURS, 10 ** 10 + 1, Fr(153, 10), 2818382931)
    print(f"  ours: {base.str(12)}")
    for name, kw in [("shift 3/2", dict(shift=Fr(3, 2))), ("primes | q as Banks (1/(2H))", dict(pq="banks")),
                     ("kappa and Mertens terms dropped", dict(kappa=False, mertens_extra=False)),
                     ("theta constant 2", dict(theta="2")), ("Banks's S1 bounds", dict(s1="banks")),
                     ("lambda upper end (omega+1)", dict(lam_hi="omega+1"))]:
        cfg = OURS.but(**kw)
        _, g, H, _ = fsearch(cfg, 10 ** 10 + 1)
        d, _ = delta0(cfg, 10 ** 10 + 1, g, H)
        print(f"  {name:38s} gamma {str(g):>7s} H {H:>13d}: {d.str(10)}  ratio to ours {(d / base).str(5)}")
    for name, kw in [("H fixed at the paper's", None)]:
        _, g, _, _ = fsearch(OURS, 10 ** 10 + 1, H=H_PAPER)
        d, _ = delta0(OURS, 10 ** 10 + 1, g, H_PAPER)
        print(f"  {name:38s} gamma {str(g):>7s} H {H_PAPER:>13d}: {d.str(10)}  ratio to ours {(d / base).str(5)}")

    print("\n== Not in note.md: ours with Banks's primes-dividing-q accounting, shift also optimized")
    for q0 in (400001, 10 ** 10 + 1):
        cfg = OURS.but(pq="banks")
        _, g, H, s = fsearch(cfg, q0, shift_free=True)
        show(f"  q0 = {q0}", cfg.but(shift=s), q0, g, H)

    print("\n== Platt case (q0 = 4*10^5 + 1, note.md row 1): how the bounded terms enter")
    show("  ours (note.md row 1)", OURS, 400001, Fr(201, 10), 1995262314)
    l0 = arb(400001).log()
    print(f"  log q0 = {l0.str(8)} (< 23, so Banks's absorption step does not apply);"
          f" log H = {arb(1995262314).log().str(8)}; L >= (4/3) gamma log q0 = {(4 * A(Fr(201, 10)) / 3 * l0).str(8)}")
    print(f"  Banks's accounting at q0 = 4*10^5 + 1, gamma and H free: ", end="")
    _, g, H, _ = fsearch(BANKS, 400001)
    d, _ = delta0(BANKS, 400001, g, H)
    print(f"gamma {g}, H {H}: {d.str(10)}")
    print(f"\nPart A all checks OK: {okA}")


if __name__ == "__main__":
    main()
