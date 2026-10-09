"""Consolidated Lemma 7 counts per N over several JSONL files (flint runs).

Usage: python src/summarize_all.py F1.jsonl F2.jsonl ...
"""
import json
import sys
from collections import defaultdict

runs = {}
for fn in sys.argv[1:]:
    for line in open(fn, encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") != "header":
            runs[(r["N"], r["H"], r["d"])] = r
by_n = defaultdict(lambda: dict(runs=0, fields=set(), Hs=set(), adm=0, ok_norm=0, ok_delta=0, eq=0,
                                strict=0, cls=defaultdict(lambda: [0, 0]), maxw=set(), rej=0,
                                regdet=0, regdet_ok=0))
for (N, H, d), r in runs.items():
    b = by_n[N]
    b["runs"] += 1
    b["fields"].add(d)
    b["Hs"].add(H)
    b["maxw"].add((H, r["max_weight"]))
    b["rej"] += r.get("rejected_mod_p", 0)
    if "regdet_norm_agrees" in r:
        b["regdet"] += 1
        b["regdet_ok"] += r["regdet_norm_agrees"]
    for x in r["primes"]:
        if x["Ep"] == 0:
            continue
        c = b["cls"][x["tag"]]
        c[0] += 1
        c[1] += x["vp_ge_4Ep"]
        if x["admissible"]:
            b["adm"] += 1
            b["ok_norm"] += x["vp_ge_4Ep"]
            b["ok_delta"] += x.get("Delta_in_pEpR", False)
            b["eq"] += x["vp"] == x["four_Ep"]
            b["strict"] += x.get("vp_gcd_Delta", 0) > x["Ep"]
print("sources:", " ".join(sys.argv[1:]))
for N in sorted(by_n):
    b = by_n[N]
    print(f"N={N}: runs={b['runs']} fields={len(b['fields'])} H={sorted(b['Hs'])}")
    print(f"  admissible (run,p) pairs with E_p>0: {b['adm']}; v_p(N(Delta)) >= 4E_p: {b['ok_norm']}; "
          f"Delta in p^E_p R: {b['ok_delta']}; equality v_p = 4E_p: {b['eq']}; v_p(gcd Delta) > E_p: {b['strict']}")
    print(f"  rejections mod p (all certified exactly or the run would have stopped): {b['rej']}; "
          f"regular-representation det computed in {b['regdet']} runs, agrees in {b['regdet_ok']}")
    print("  max weight by H:", sorted(b["maxw"]))
    for tag, (n, k) in sorted(b["cls"].items()):
        print(f"  class {tag:22s}: pairs {n:4d}, v_p >= 4E_p in {k:4d}")
