"""Regression test: the Arb certificate in src/explicit_c.py still certifies F > 0."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import explicit_c as X  # noqa: E402


def test_certificates_hold():
    arb = X.arb
    for l0, t, d in [(arb(3).log(), "226.915", "0.00030379"),
                     (arb(400000).log(), "34.483", "0.00199806"),
                     (arb(10 ** 10).log(), "26.595", "0.0025893")]:
        assert X.rigorous(l0, arb(t), arb(d)) > 0


def test_F_increasing_in_l_at_fixed_t():
    arb = X.arb
    t, d = arb("26.595"), arb("0.0025893")
    vals = [X.rigorous(arb(l), t, d) for l in (23.1, 30, 50, 100)]
    assert all(vals[i + 1] > vals[i] for i in range(len(vals) - 1))
