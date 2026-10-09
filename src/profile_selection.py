"""Time the greedy selection of src/lemma7_check.py with a time cap, recording elapsed
time and coefficient size each time a row is retained. Used to estimate the cost of a
full run (task 1, N = 4) without waiting for it.

Usage: python src/profile_selection.py d N H CAP_SECONDS
Prints one JSON object.
"""
import json
import sys
import time
from fractions import Fraction
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lemma7_check as L  # noqa: E402


def max_bits(rows):
    m = 0
    for _, r in rows:
        for z in r:
            for c in z:
                m = max(m, c.numerator.bit_length(), c.denominator.bit_length())
    return m


def main():
    d, N, H, cap = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    pts = list(product(range(N), repeat=4))
    M = len(pts)
    thetas = [tuple(Fraction(c) for c in n) for n in pts]
    cache = {}

    def row(alpha):
        a1, a2, a3 = alpha
        return [L.mul(L.mul(L.power(t, a1, d, cache), L.power(L.sigma(t), a2, d, cache), d),
                      L.power(L.sigmatau(t), a3, d, cache), d) for t in thetas]

    ech = L.Echelon(M, d)
    marks = []      # (retained count, tried count, elapsed s, max bits in echelon basis)
    tried = 0
    t0 = time.perf_counter()
    w = 0
    done = False
    while not done:
        for a2 in range(w // H + 1):
            for a3 in range((w - H * a2) // H + 1):
                alpha = (w - H * (a2 + a3), a2, a3)
                tried += 1
                if ech.try_add(row(alpha)):
                    k = len(ech.rows)
                    el = time.perf_counter() - t0
                    bits = max_bits(ech.rows) if k % 8 == 0 or k == M else None
                    marks.append((k, tried, round(el, 3), bits, w))
                    if k == M:
                        done = True
                        break
                if time.perf_counter() - t0 > cap:
                    done = True
                    break
            if done:
                break
        w += 1
    print(json.dumps(dict(d=d, N=N, H=H, M=M, cap_s=cap, retained=len(ech.rows),
                          tried=tried, elapsed_s=time.perf_counter() - t0, marks=marks)))


if __name__ == "__main__":
    main()
