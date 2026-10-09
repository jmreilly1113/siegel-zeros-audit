"""EXPLORATORY: greedy weighted selection (Section 4) modulo degree-one primes only, for N too
large for the exact pipeline. Records S1, S2, max weight, rows tried, for Lemma 6 / (4.4).

Retained rows are certified independent over K (independent mod P implies independent over K).
Rejections are NOT certified: a row dependent mod P might be independent over K. The selection is
run at two different primes and the retained sets must agree; agreement is strong evidence but not
a proof that the set equals the exact greedy set. Results must be labeled exploratory.

Usage: python src/selection_modp.py N H1,H2,... d1,d2,...    (prints one JSON line per run)
"""
import json
import sys
import time
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lemma7_flint as F  # noqa: E402


def select(pts, d, H, p, s, t):
    M = len(pts)
    mr = F.ModRows(pts, p, s, t, 8)
    ech = F.ModEchelon(p)
    retained, tried, w = [], 0, 0
    while len(retained) < M:
        for a2 in range(w // H + 1):
            for a3 in range((w - H * a2) // H + 1):
                alpha = (w - H * (a2 + a3), a2, a3)
                tried += 1
                r = ech.reduce(mr.row(alpha))
                if r.any():
                    ech.add(r)
                    retained.append(alpha)
                    if len(retained) == M:
                        break
            if len(retained) == M:
                break
        w += 1
    return retained, tried, w - 1


def main():
    N = int(sys.argv[1])
    Hs = [int(x) for x in sys.argv[2].split(",")]
    ds = [int(x) for x in sys.argv[3].split(",")]
    pts = list(product(range(N), repeat=4))
    M = len(pts)
    U = N ** (4 / 3)
    for d in ds:
        g = F.split_primes(d)
        (p1, s1, t1), (p2, s2, t2) = next(g), next(g)
        for H in Hs:
            t0 = time.perf_counter()
            r1, tried, maxw = select(pts, d, H, p1, s1, t1)
            r2, _, _ = select(pts, d, H, p2, s2, t2)
            S1 = sum(a[0] for a in r1)
            S2 = sum(a[1] + a[2] for a in r1)
            print(json.dumps(dict(
                label="EXPLORATORY (mod-p selection, rejections not certified)",
                d=d, N=N, H=H, H_le_N=H <= N, M=M, primes=[p1, p2], two_primes_agree=(r1 == r2),
                rows_tried=tried, max_weight=maxw, weight_bound=96 * H ** (2 / 3) * U,
                S1=S1, S2=S2, S2_over_S1=S2 / S1,
                S1_norm=S1 / (M * H ** (2 / 3) * U), S2_norm=S2 / (M * H ** (-1 / 3) * U),
                max_alpha1=max(a[0] for a in r1), max_alpha23=max(max(a[1], a[2]) for a in r1),
                seconds=time.perf_counter() - t0)), flush=True)


if __name__ == "__main__":
    main()
