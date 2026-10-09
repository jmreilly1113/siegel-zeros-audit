"""Cross-check src/lemma7_flint.py against the Fraction reference src/lemma7_check.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import lemma7_check as L  # noqa: E402
import lemma7_flint as F  # noqa: E402

KEYS = ["retained", "S1", "S2", "max_weight", "Delta", "norm_Delta"]


def test_flint_matches_fraction_N2():
    for d in [5, -7, -1, 6, 13, -3]:
        for H in [1, 2, 3]:
            a = L.run(d, 2, H, quiet=True)
            b = F.run(d, 2, H, quiet=True, regdet=True)
            assert all(a[k] == b[k] for k in KEYS), (d, H)
            assert b["regdet_norm_agrees"]
            assert [(r["p"], r["vp"]) for r in a["primes"]] == [(r["p"], r["vp"]) for r in b["primes"]]


def test_regmat_is_multiplication():
    d = -7
    x, y = (1, 2, -3, 4), (5, -1, 2, 7)
    reg = F.regmat(y, d)
    prod = [sum(x[u] * reg[u][v] for u in range(4)) for v in range(4)]
    assert tuple(prod) == F.imul(x, y, d)


def test_split_primes():
    for d in [5, -7, -1, 6]:
        g = F.split_primes(d)
        for _ in range(3):
            p, s, t = next(g)
            assert p % 8 == 1 and (s * s - d) % p == 0 and (t * t - 2) % p == 0
