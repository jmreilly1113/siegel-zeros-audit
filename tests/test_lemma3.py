"""Tests for src/lemma3_construct.py: exact nearest points, and that the step checks
can fail (a wrong m or u must be caught).

Run with: python -m pytest tests/ -q   (from the project root)
"""
import random
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import lemma3_construct as C  # noqa: E402


def brute_dist2(target, pts):
    """Exact distance^2 from target to conv(pts), by projecting onto every face spanned
    by an affinely independent subset of size <= 5 and keeping projections inside it."""
    best = None
    for k in range(1, min(5, len(pts)) + 1):
        for T in combinations(pts, k):
            if C.affine_rank(list(T)) != k - 1:
                continue
            G = [[C.dot(p, q) for q in T] + [Fraction(1)] for p in T] + [[Fraction(1)] * k + [Fraction(0)]]
            rhs = [C.dot(p, target) for p in T] + [Fraction(1)]
            w = C.solve(G, rhs)[:k]
            if any(x < 0 for x in w):
                continue
            y = tuple(sum(w[i] * T[i][j] for i in range(k)) for j in range(4))
            d2 = C.dot(C.vsub(target, y), C.vsub(target, y))
            best = d2 if best is None else min(best, d2)
    return best


def test_nearest_matches_brute_force():
    rng = random.Random(3)
    for _ in range(150):
        pts = list({tuple(Fraction(rng.randint(0, 3)) for _ in range(4)) for _ in range(rng.randint(1, 6))})
        target = tuple(Fraction(rng.randint(-2, 5)) for _ in range(4))
        y, d2, lam = C.nearest(target, pts)
        assert d2 == brute_dist2(target, pts)


def _instance(S, d=-7, mode="product", override=None, seed=0):
    rng = random.Random(seed)
    v = {s: Fraction(i + 1) for i, s in enumerate(S)}
    return C.run_instance(d, 2, S, v, mode, rng, C.lattice_points(S), override)


def test_honest_instances_pass():
    for S in ([(0, 0, 0, 0)], [(0, 0, 0, 0), (1, 1, 0, 0)], [(0, 1, 0, 1), (1, 0, 0, 0), (1, 1, 1, 0)]):
        for mode in ("product", "generic"):
            assert _instance(S, mode=mode)["all_ok"], (S, mode)


def test_wrong_u_is_caught():
    S = [(0, 0, 0, 0), (1, 1, 0, 0), (1, 0, 1, 1)]
    honest = _instance(S)
    u = tuple(honest["u"])
    other = next(s for s in S if s != u)
    bad = _instance(S, override={"u": other})
    assert not bad["all_ok"]


def test_non_minimal_m_is_caught():
    """A lattice point with R(Am) != 0 that is not nearest to K breaks some later step."""
    S = [(0, 0, 0, 0), (1, 1, 0, 0), (1, 0, 1, 1)]
    honest = _instance(S)
    caught = 0
    for off in product((-2, 0, 2), repeat=4):
        m = tuple(x + o for x, o in zip(honest["m"], off))
        if m == tuple(honest["m"]):
            continue
        res = _instance(S, override={"m": m})
        caught += not res["all_ok"]
    assert caught > 0
