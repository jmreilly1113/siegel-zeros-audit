"""Summarize a JSONL file from src/batch_lemma7.py: per-run table and per-prime-class counts.

Usage: python src/summarize_lemma7.py IN.jsonl
"""
import json
import sys
from collections import defaultdict

recs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
hdr = [r for r in recs if r.get("kind") == "header"]
runs = sorted((r for r in recs if r.get("kind") != "header"), key=lambda r: (r["N"], r["H"], r["d"]))
if hdr:
    print("source:", sys.argv[1])
    print("command:", " ".join(hdr[0]["argv"]))
    print("python:", hdr[0]["python"].split()[0], "| python-flint:", hdr[0]["python_flint"])
print()
print(f"{'d':>4} {'q':>4} {'N':>2} {'H':>2} {'H<=N':>5} {'maxw':>4} {'bound':>7} {'S1':>5} {'S2':>5} "
      f"{'S2/S1':>6} {'log|N(D)| (Arb)':>34} {'L7':>4}  admissible p: 4E_p/v_p")
classes = defaultdict(lambda: [0, 0, None])   # tag -> [cases, cases with v_p >= 4E_p, min margin]
for r in runs:
    adm = " ".join(f"{x['p']}:{x['four_Ep']}/{x['vp']}" for x in r["primes"] if x["admissible"])
    print(f"{r['d']:>4} {r['q']:>4} {r['N']:>2} {r['H']:>2} {str(r['H_le_N']):>5} {r['max_weight']:>4} "
          f"{r['max_weight_bound'].split('= ')[1]:>7} {r['S1']:>5} {r['S2']:>5} {r['S2']/r['S1']:>6.3f} "
          f"{r['log_abs_norm']['arb']:>34} {'ok' if r['lemma7_holds_all_admissible'] else 'FAIL':>4}  {adm}")
    for x in r["primes"]:
        if x["Ep"] == 0:
            continue
        c = classes[x["tag"]]
        c[0] += 1
        c[1] += x["vp_ge_4Ep"]
        m = x["vp"] - x["four_Ep"]
        c[2] = m if c[2] is None else min(c[2], m)
print()
print("Per prime class, over all (run, prime) pairs with E_p > 0:")
print(f"  {'class':22s} {'pairs':>6} {'v_p>=4E_p':>10} {'min(v_p-4E_p)':>14}")
for tag, (n, k, m) in sorted(classes.items()):
    print(f"  {tag:22s} {n:>6} {k:>10} {m:>14}")
print()
print("Lemma 7 holds at every admissible prime in every run:",
      all(r["lemma7_holds_all_admissible"] for r in runs), f"({len(runs)} runs)")
