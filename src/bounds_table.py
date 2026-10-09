"""Task 3: compare the actual determinants with the paper's bounds.

For every run in the given JSONL files (from src/batch_lemma7.py) computes, with Arb balls:
  - Lemma 6 (4.4) normalizations: S1 / (M H^(2/3) U) against c0 = 1/(4*97^2), and
    S2 / (M H^(-1/3) U) against C0 = 192. (The lemma is claimed only for N large in terms of H.)
  - (5.1): LHS = (1/4) log|N(Delta)|, RHS = (M/2) log M + (S1+S2)(log N + ell/2 + log 8).
    Checks LHS <= RHS rigorously.
  - (5.6): L_all = sum over admissible p of E_p log p, L_U = same restricted to p <= U,
    and the second line of (5.6), S1 * sum_{adm p <= U} log p / p - M * sum_{p <= U} log p.
    Checks L_all <= LHS (consequence of Lemma 7) and line2 <= L_U (floor(x) >= x - 1), rigorously.
  - Descriptive: LHS / (S1 log U), and the paper's leading terms S1 log U vs (S1+S2)(3/4) log U.
  - Descriptive: share of log|N(Delta)| explained by primes p <= max alpha_1, split into
    admissible / chi=+1,(2/p)=+1 / other good-free classes / p | 2q; and a hypothetical
    L_hyp = sum over ALL p > H, p not dividing 2q, p <= max alpha_1, of E_p log p (what the
    divisibility bound would give if every such prime were admissible), as a fraction of LHS.
    L_hyp / LHS > 1 would mean the paper's contradiction mechanism is already visible at this N.

Usage: python src/bounds_table.py RUNS1.jsonl [RUNS2.jsonl ...]
"""
import json
import sys
from pathlib import Path

import flint

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lemma7_check as L  # noqa: E402

sys.set_int_max_str_digits(0)
arb = flint.arb
C0 = arb(192)
c0 = 1 / arb(4 * 97 ** 2)


def le(x, y):
    """Rigorous x <= y for arb balls; None if undecided."""
    if (y - x) >= 0:
        return True
    if (y - x) < 0:
        return False
    return None


def mid(x):
    return float(x.mid())


def main():
    runs = {}
    for fn in sys.argv[1:]:
        for line in open(fn, encoding="utf-8"):
            r = json.loads(line)
            if r.get("kind") == "header":
                continue
            r["_src"] = fn
            runs[(r["N"], r["H"], r["d"])] = r       # later files override earlier duplicates
    print("sources:", ", ".join(sys.argv[1:]))
    print("python-flint", flint.__version__, "| all inequality checks are rigorous (Arb); ratios are Arb midpoints")
    print()
    hdr = (f"{'N':>2} {'H':>2} {'d':>4} {'q':>4} {'S1/(MH^2/3U)':>12} {'S2/(MH^-1/3U)':>13} {'S2/S1':>6} "
           f"{'LHS=logN/4':>11} {'RHS(5.1)':>10} {'LHS/RHS':>7} {'ok5.1':>5} "
           f"{'L_all':>8} {'L_U':>8} {'line2':>9} {'okL7':>4} {'ok5.6':>5} {'LHS/(S1logU)':>12} "
           f"{'S1logU':>8} {'(S1+S2)3/4logU':>14} {'sh_adm':>6} {'sh_++':>6} {'sh_oth':>6} {'sh_2q':>6} {'Lhyp/LHS':>8}")
    print(hdr)
    allok = True
    out = []
    for key in sorted(runs):
        r = runs[key]
        N, H, d, q, M, S1, S2 = r["N"], r["H"], r["d"], r["q"], r["M"], r["S1"], r["S2"]
        U = arb(N) ** (arb(4) / 3)
        ell = arb(q).log()
        nd = int(r["norm_Delta"])
        LHS = arb(flint.fmpz(abs(nd))).log() / 4
        RHS = arb(M) / 2 * arb(M).log() + (S1 + S2) * (arb(N).log() + ell / 2 + arb(8).log())
        adm = [x for x in r["primes"] if x["admissible"]]
        L_all = sum((x["Ep"] * arb(x["p"]).log() for x in adm), arb(0))
        adm_U = [x for x in adm if le(arb(x["p"]), U)]
        L_U = sum((x["Ep"] * arb(x["p"]).log() for x in adm_U), arb(0))
        # admissible primes <= U, including those with E_p = 0 (not listed when p > max alpha1)
        pU = [p for p in L.primes_upto(int(mid(U)) + 1) if le(arb(p), U)]
        adm_all_U = [p for p in pU if p > H and (2 * q) % p and L.legendre(d, p) == -1]
        line2 = (S1 * sum((arb(p).log() / p for p in adm_all_U), arb(0))
                 - M * sum((arb(p).log() for p in pU), arb(0)))
        ok51, okL7, ok56 = le(LHS, RHS), le(L_all, LHS), le(line2, L_U)
        allok &= bool(ok51 and okL7 and ok56)
        a = S1 / (M * arb(H) ** (arb(2) / 3) * U)
        b = S2 / (M * arb(H) ** (arb(-1) / 3) * U)
        lead_lo = S1 * U.log()
        lead_hi = (S1 + S2) * arb(3) / 4 * U.log()
        logN = 4 * LHS
        share = {}
        for cls, f in (("adm", lambda x: x["admissible"]),
                       ("pp", lambda x: x["tag"] == "chi=+1,(2/p)=+1"),
                       ("oth", lambda x: x["tag"] in ("chi=+1,(2/p)=-1", "chi=-1, p<=H")),
                       ("2q", lambda x: x["tag"].startswith("excluded"))):
            share[cls] = mid(sum((x["vp"] * arb(x["p"]).log() for x in r["primes"] if f(x)), arb(0)) / logN)
        L_hyp = sum((x["Ep"] * arb(x["p"]).log() for x in r["primes"]
                     if x["p"] > H and not x["tag"].startswith("excluded")), arb(0))
        print(f"{N:>2} {H:>2} {d:>4} {q:>4} {mid(a):>12.4f} {mid(b):>13.4f} {S2 / S1:>6.3f} "
              f"{mid(LHS):>11.1f} {mid(RHS):>10.1f} {mid(LHS / RHS):>7.3f} {str(ok51):>5} "
              f"{mid(L_all):>8.1f} {mid(L_U):>8.1f} {mid(line2):>9.1f} {str(okL7):>4} {str(ok56):>5} "
              f"{mid(LHS / lead_lo):>12.3f} {mid(lead_lo):>8.1f} {mid(lead_hi):>14.1f} "
              f"{share['adm']:>6.3f} {share['pp']:>6.3f} {share['oth']:>6.3f} {share['2q']:>6.3f} "
              f"{mid(L_hyp / LHS):>8.3f}")
        out.append(dict(N=N, H=H, d=d, ok51=ok51, okL7=okL7, ok56=ok56))
    print()
    print(f"c0 = {mid(c0):.3e}, C0 = 192. Runs: {len(out)}. All rigorous checks True: {allok}")


if __name__ == "__main__":
    main()
