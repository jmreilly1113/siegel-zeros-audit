"""Step 4: an explicit value of c in the paper's theorem, CONDITIONAL on the paper's argument
(Lemmas 6, 7, (5.1), (5.6)) and on classical explicit inputs listed below. Not a finding: an
inference whose bookkeeping needs an expert check. See docs/explicit-constant.md.

Explicit inputs (classical; references in docs/explicit-constant.md):
  (I1) Re(-L'/L(s,chi)) = 1/2 log(q/pi) + 1/2 psi((s+eps)/2) - sum_rho Re 1/(s-rho)  (primitive chi)
  (I2) -zeta'/zeta(s) < 1/(s-1) for real s > 1
  (I3) psi(x) <= psi(3/2) = 2 - gamma - 2 log 2 for x in (1/2, 3/2]
  (I4) sum_{p<=x} log p/p > log x + E - 1/(2 log x), E = -1.332582..., x > 1   (Rosser-Schoenfeld 1962)
  (I5) sum_{p<=x} log p/p < log x, x > 1                                          (Rosser-Schoenfeld 1962)
  (I6) theta(x) < 1.01624 x, x > 0                                                (Rosser-Schoenfeld 1962)
Paper inputs: Lemma 6 with H = 86713344 gives S2/S1 <= 1/12 and M/S1 <= 1/(c0 H^(2/3) U);
(5.1); (5.6) first line (from Lemma 7).

Derived contradiction condition (all logs natural, l = log q, L = log U = (4/3) log N):
  F = 3/16 - A/L - 1/(2 L^2) - (e/2) delta L / l - K/(D L) - 3/(2 D e^L) > 0
  A = (e/4 + 1/3 + 13/24) l + b + (13/12) log 8,
  b = -E + (log 2)/2 + log H - (e/2)(1/2 log pi - 1/2 psi(3/2)),
  K = 1.01624, D = c0 H^(2/3).
If F > 0 for some integer N >= H, a real zero with (1 - beta) log q = delta cannot exist.

For fixed t = L/l, F is increasing in l, so a check at l0 with L in [t l0, t l0 + eps] covers all
l >= l0 (choosing N = ceil(exp(3 t l / 4)) for each q).

Usage: python src/explicit_c.py
"""
import sys

import flint

arb = flint.arb
ctx = flint.ctx
ctx.prec = 200

H = arb(86713344)
c0 = 1 / arb(4 * 97 ** 2)
D = c0 * H ** (arb(2) / 3)
e = arb(1).exp()
pi = arb.pi()
EULER = arb.const_euler()
E_RS = arb("-1.332582275733220881765828776071027748")  # Rosser-Schoenfeld E = -gamma - sum log p/(p(p-1))
psi32 = 2 - EULER - 2 * arb(2).log()
K = arb("1.01624")
log8 = arb(8).log()
b = -E_RS + arb(2).log() / 2 + H.log() - (e / 2) * (pi.log() / 2 - psi32 / 2)
a = e / 4 + arb(1) / 3


def A(l):
    return (a + arb(13) / 24) * l + b + arb(13) / 12 * log8


def F(l, L, delta):
    return (arb(3) / 16 - A(l) / L - 1 / (2 * L * L) - (e / 2) * delta * L / l
            - K / (D * L) - 3 / (2 * D * L.exp()))


def best(l0):
    """Float search for (t, delta) maximizing delta with F > 0 at l0; then a rigorous check."""
    l = float(l0.mid())
    best_d, best_t = 0.0, None
    t = 1.0
    while t < 2000:
        L = t * l
        if L >= float((arb(4) / 3 * H.log()).mid()):
            core = float((arb(3) / 16 - A(arb(l)) / L - 1 / (2 * L * L) - K / (D * L)
                          - 3 / (2 * D * arb(L).exp())).mid())
            d = core * l / (float(e.mid()) / 2 * L)
            if d > best_d:
                best_d, best_t = d, t
        t *= 1.002
    return best_d, best_t


def rigorous(l0, t, delta, eps=arb("1e-6")):
    """Lower bound of F over L in [t l0, t l0 + eps], valid for all l >= l0 (F increasing in l
    at fixed t; the eps covers rounding N up to an integer)."""
    Llo = t * l0
    Lhi = t * l0 + eps
    val = (arb(3) / 16 - A(l0) / Llo - 1 / (2 * Llo * Llo) - (e / 2) * delta * Lhi / l0
           - K / (D * Llo) - 3 / (2 * D * Llo.exp()))
    return val


def main():
    print("Explicit-c computation (CONDITIONAL; see docs/explicit-constant.md). python-flint", flint.__version__)
    print(f"D = c0 H^(2/3) = {D.str(8)}; b = {b.str(8)}; a + 13/24 = {(a + arb(13) / 24).str(8)}; "
          f"psi(3/2) = {psi32.str(8)}")
    for name, l0 in [("all q >= 3 (l0 = log 3)", arb(3).log()),
                     ("q > 4e5 (Platt below)", arb(400000).log()),
                     ("q > 1e10 (Lu-Zaman-Zhao below)", arb(10 ** 10).log())]:
        d, t = best(l0)
        # back off slightly and certify
        dcert = arb(round(d * 0.999, 8))
        tt = arb(round(t, 6))
        lowF = rigorous(l0, tt, dcert)
        ok = lowF > 0
        print(f"{name}: l0 = {l0.str(6)}, best t = L/l = {t:.3f}, delta_max ~ {d:.6g}; "
              f"certified delta = {dcert.str(8)} with F >= {lowF.str(6)} > 0: {ok}")
        # required N
        N_log10 = float((3 * tt * l0 / 4 / arb(10).log()).mid())
        print(f"   (N = ceil(exp(3 t l / 4)) ~ 10^{N_log10:.1f} at l = l0)")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
