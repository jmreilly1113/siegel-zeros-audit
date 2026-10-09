"""Summarize lemma3_construct.py JSONL output.

Usage: python src/summarize_lemma3.py results/<file>.jsonl [...]
"""
from collections import Counter, defaultdict
import json
import sys


def main():
    rows = []
    for fn in sys.argv[1:]:
        with open(fn) as f:
            rows += [json.loads(line) for line in f if line.strip()]
    print(f"files: {', '.join(sys.argv[1:])}")
    print(f"instances: {len(rows)}, all checks passed: {sum(r['all_ok'] for r in rows)}")
    fails = Counter(k for r in rows for k, v in r["checks"].items() if not v)
    print(f"failed checks: {dict(fails) if fails else 'none'}")
    nchecks = Counter(len(r["checks"]) for r in rows)
    print(f"checks per instance: {dict(nchecks)}")
    by = defaultdict(list)
    for r in rows:
        by[(r["N"], r["mode"])].append(r)
    for (N, mode), rs in sorted(by.items()):
        print(f"\nN={N} mode={mode}: {len(rs)} instances, fields d={sorted(set(r['d'] for r in rs))}")
        print(f"  |S| range {min(r['S_size'] for r in rs)}..{max(r['S_size'] for r in rs)}; "
              f"#(K cap Z^4) range {min(r['lattice_pts_in_K'] for r in rs)}..{max(r['lattice_pts_in_K'] for r in rs)}")
        print(f"  dim P counts: {dict(sorted(Counter(r['dim_P'] for r in rs).items()))}")
        print(f"  dim G counts: {dict(sorted(Counter(r['dim_G'] for r in rs).items()))}")
        print(f"  dist^2(m, K) values: {dict(sorted(Counter(r['dist2_m'] for r in rs).items(), key=lambda kv: eval(kv[0])))}")
        if mode == "generic":
            z = [r["closer_zeros_outside_K"] for r in rs]
            print(f"  instances where R vanished at lattice points outside K closer than m: "
                  f"{sum(1 for x in z if x)} (max {max(z)} such points)")
            print(f"  null-space dimension range: {min(r['null_dim'] for r in rs)}..{max(r['null_dim'] for r in rs)}")


if __name__ == "__main__":
    main()
