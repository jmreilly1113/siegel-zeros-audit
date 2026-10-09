"""Compare two JSONL result files (e.g. Fraction reference vs flint) run by run.

Usage: python src/compare_runs.py REF.jsonl OTHER.jsonl
Compares retained, S1, S2, max_weight, Delta, norm_Delta and per-prime vp for every (d, N, H)
present in both files.
"""
import json
import sys


def load(fn):
    out = {}
    for line in open(fn, encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") != "header":
            out[(r["d"], r["N"], r["H"])] = r
    return out


a, b = load(sys.argv[1]), load(sys.argv[2])
common = sorted(set(a) & set(b))
keys = ["retained", "S1", "S2", "max_weight", "Delta", "norm_Delta"]
bad = 0
for k in common:
    diffs = [x for x in keys if a[k][x] != b[k][x]]
    pa = [(r["p"], r["vp"], r["Ep"]) for r in a[k]["primes"]]
    pb = [(r["p"], r["vp"], r["Ep"]) for r in b[k]["primes"]]
    if pa != pb:
        diffs.append("primes")
    extra = {x: b[k][x] for x in ("regdet_norm_agrees", "rejected_mod_p", "crt_primes") if x in b[k]}
    print(k, "AGREE" if not diffs else f"DIFFER in {diffs}", extra)
    bad += bool(diffs)
print(f"{len(common)} runs compared, {bad} disagreements; only in first: {len(set(a) - set(b))}, "
      f"only in second: {len(set(b) - set(a))}")
