"""Sanity tests for src/lemma7_check.py.

Run with: python -m pytest tests/ -q   (from the project root)
"""
import random
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import lemma7_check as L  # noqa: E402

FIELDS = [5, -7, 13, -11, -3, 17]


def rand_elt(rng):
    return tuple(Fraction(rng.randint(-9, 9)) for _ in range(4))


def test_mul_matches_embedding():
    """Multiplication rule agrees with a floating-point complex embedding."""
    rng = random.Random(0)
    for d in FIELDS:
        a = complex(d) ** 0.5
        b = 2 ** 0.5

        def ev(z):
            return float(z[0]) + float(z[1]) * a + float(z[2]) * b + float(z[3]) * a * b

        for _ in range(50):
            x, y = rand_elt(rng), rand_elt(rng)
            assert abs(ev(L.mul(x, y, d)) - ev(x) * ev(y)) < 1e-6 * (1 + abs(ev(x) * ev(y)))


def test_norm_is_rational_and_inverse_works():
    rng = random.Random(1)
    for d in FIELDS:
        for _ in range(50):
            x = rand_elt(rng)
            if L.is_zero(x):
                continue
            assert L.mul(x, L.inv(x, d), d) == L.ONE


def test_frobenius_congruence_5_2():
    """theta^p == g_p(theta) mod pR for odd p not dividing 2q with chi(p) = -1 (eq. 5.2),
    and theta^p == theta when chi(p) = +1 and (2/p) = +1."""
    rng = random.Random(2)
    for d in FIELDS:
        for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
            if (2 * d) % p == 0:
                continue
            chi, two = L.legendre(d, p), L.legendre(2, p)
            if chi == -1:
                g = L.sigma if two == 1 else L.sigmatau
            elif two == 1:
                g = lambda z: z  # noqa: E731
            else:
                g = L.tau
            for _ in range(10):
                t = rand_elt(rng)
                diff = L.sub(L.power(t, p, d, {}), g(t))
                assert all(c.denominator == 1 and c.numerator % p == 0 for c in diff)
