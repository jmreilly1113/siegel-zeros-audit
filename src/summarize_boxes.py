"""Summarize src/interpolation_boxes.py output: minimal full-rank boxes per field, compared
with the box condition (3.1) and the boxes of Corollary 4.

Usage: python src/summarize_boxes.py IN.jsonl
"""
import json
import sys

recs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
N = recs[0]["N"]
M = N ** 4
# smallest number of rows in any box satisfying (3.1): t_j >= 3(N-1), prod(t_j - 3(N-1) + 1) > (4N-3)^4
lo = 3 * (N - 1)
best = None
for b1 in range(1, 200):
    for b2 in range(1, 200):
        need = (4 * N - 3) ** 4 // (b1 * b2) + 1
        b3 = max(1, need)
        if b1 * b2 * b3 <= (4 * N - 3) ** 4:
            continue
        rows = (b1 + lo) * (b2 + lo) * (b3 + lo)
        if best is None or rows < best[0]:
            best = (rows, (b1 + lo - 1, b2 + lo - 1, b3 + lo - 1))
U = N ** (4 / 3)
print(f"source: {sys.argv[1]}")
print(f"N = {N}, M = {M}")
print(f"Smallest box allowed by (3.1): t = {best[1]}, {best[0]} rows")
for H in range(1, N + 1):
    T = (32 * H ** (2 / 3) * U, 32 * H ** (-1 / 3) * U, 32 * H ** (-1 / 3) * U)
    rows = 1
    for t in T:
        rows *= int(t) + 1
    print(f"Corollary 4 box for H = {H}: floor(T) = {tuple(int(t) for t in T)}, {rows} rows")
print()
print(f"{'d':>4} {'kernel':>6} {'4ab':>5} {'#minimal':>8} {'min rows':>8} {'max rows':>8} {'all cert.':>9}  minimal boxes (t1,t2,t3)")
sigs = {}
for r in recs:
    rows = r["minimal_box_rows"]
    print(f"{r['d']:>4} {str(r['kernel_claim']):>6} {str(r['minor_is_4ab']):>5} {len(rows):>8} "
          f"{min(rows):>8} {max(rows):>8} {str(all(r['exact_minimality_certified'])):>9}  "
          + " ".join("(%d,%d,%d)" % tuple(b) for b in r["minimal_boxes"]))
    sigs.setdefault(json.dumps(r["minimal_boxes"]), []).append(r["d"])
print()
print("Fields grouped by identical minimal-box sets:")
for k, ds in sigs.items():
    print("  ", ds)
print()
print("Symmetry t2 <-> t3 of the minimal-box set:",
      {r["d"]: sorted(tuple(b) for b in r["minimal_boxes"]) ==
       sorted((b[0], b[2], b[1]) for b in r["minimal_boxes"]) for r in recs})
