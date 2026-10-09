"""EXPLORATORY numerical spot checks of the classical inputs (I2), (I4)-(I6) used in
src/explicit_c.py, over finite ranges. The cited theorems cover all x; this only guards against
transcription errors in the constants. Usage: python src/check_classical_inputs.py XMAX"""
import sys
import numpy as np
import mpmath as mp

XMAX = int(sys.argv[1])
s = np.ones(XMAX + 1, dtype=bool); s[:2] = False
for i in range(2, int(XMAX ** 0.5) + 1):
    if s[i]: s[i * i::i] = False
P = np.nonzero(s)[0].astype(np.float64)
lp = np.log(P)
cum_lp_over_p = np.cumsum(lp / P)
theta = np.cumsum(lp)
E = -1.332582275733220881765828776071027748
# check at each prime p (just before the next prime the sums are constant, and the bounds are
# monotone in x between primes in the direction that makes the prime the worst case or close to it)
x = P
lower = np.log(x) + E - 1 / (2 * np.log(x))
ok4 = np.all(cum_lp_over_p[1:] > lower[1:])
# (I4) also just before each prime: sum over p < x, x -> next prime
xm = P[1:] - 1e-9
ok4b = np.all(cum_lp_over_p[:-1] > np.log(xm) + E - 1 / (2 * np.log(xm)))
ok5 = np.all(cum_lp_over_p < np.log(x))
ok6 = np.all(theta < 1.01624 * x)
print(f"primes up to {XMAX}: {len(P)}")
print("(I4) sum log p/p > log x + E - 1/(2 log x), at primes and just below primes:", bool(ok4), bool(ok4b))
print("(I5) sum log p/p < log x at primes:", bool(ok5), " max of (sum - log x):", float(np.max(cum_lp_over_p - np.log(x))))
print("(I6) theta(x) < 1.01624 x at primes:", bool(ok6), " max theta(p)/p:", float(np.max(theta / x)))
mp.mp.dps = 30
worst = max((s1 - 1) * (-mp.zeta(s1, derivative=1) / mp.zeta(s1)) for s1 in [1 + mp.mpf(k) / 1000 for k in range(1, 1001)])
print("(I2) max over s = 1.001..2.000 of (s-1)(-zeta'/zeta(s)) =", mp.nstr(worst, 12), "(< 1 required)")
print("(I3) psi(3/2) =", mp.nstr(mp.digamma(1.5), 12), "; psi(1/2) =", mp.nstr(mp.digamma(0.5), 12))
