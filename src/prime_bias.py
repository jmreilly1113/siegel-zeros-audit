"""Prime-bias context table (docs/tasks.md task 4). Descriptive only; tests no lemma.

For every fundamental discriminant D with |D| <= DMAX (both signs, D != 1),
chi_D = Kronecker symbol (D/.), compute for X in XS
    S_+(D,X) = sum_{p<=X, chi_D(p)=+1} log p / p,
    S_-(D,X) = sum_{p<=X, chi_D(p)=-1} log p / p,
and the counts of primes of each sign.

Bulk sums are float64 (EXPLORATORY). chi_D(p) is computed exactly in integers
(Euler's criterion via vectorised int64 modular exponentiation; values < 1e6 so
products < 1e12 fit). The 20 smallest S_+ at the largest X are recomputed with
python-flint arb ball arithmetic and an independently computed chi (fmpz.jacobi).

Usage:
    .venv/Scripts/python src/prime_bias.py [--dmax 100000] [--procs 3] [--date 2026-10-08]
"""
import argparse
import math
import os
import platform
import sys
import time
from multiprocessing import Pool

import numpy as np

XS = (10**4, 10**5, 10**6)


def primes_upto(n):
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0].astype(np.int64)


def is_squarefree(n):
    n = abs(n)
    d = 2
    while d * d <= n:
        if n % (d * d) == 0:
            return False
        d += 1
    return True


def squarefree_mask(n):
    m = np.ones(n + 1, dtype=bool)
    m[0] = False
    for k in range(2, int(n**0.5) + 1):
        m[k * k::k * k] = False
    return m


def fundamental_discriminants(dmax):
    """All fundamental D with |D| <= dmax, D != 1, sorted by |D| then sign."""
    sf = squarefree_mask(dmax)
    out = []
    for D in range(-dmax, dmax + 1):
        if D in (0, 1):
            continue
        a = abs(D)
        r = D % 4
        if r == 1:
            if sf[a]:
                out.append(D)
        elif r == 0:
            m = D // 4
            if m % 4 in (2, 3) and sf[abs(m)]:
                out.append(D)
    out.sort(key=lambda d: (abs(d), d))
    return np.array(out, dtype=np.int64)


def chi_at_2(Ds):
    r = Ds % 8
    out = np.zeros(len(Ds), dtype=np.int8)
    out[r == 1] = 1
    out[r == 5] = -1          # D even -> 0
    return out


def chi_at_odd_p(Ds, p):
    """Legendre symbol (D/p) for odd prime p, vectorised over D (Euler's criterion)."""
    a = Ds % p                 # in [0, p)
    e = (p - 1) // 2
    result = np.ones_like(a)
    base = a.copy()
    while e:
        if e & 1:
            result = (result * base) % p
        e >>= 1
        if e:
            base = (base * base) % p
    out = np.zeros(len(Ds), dtype=np.int8)
    out[result == 1] = 1
    out[result == p - 1] = -1
    return out                  # a == 0 -> result 0 -> chi 0


def chi_vec(Ds, p):
    return chi_at_2(Ds) if p == 2 else chi_at_odd_p(Ds, int(p))


def _worker(args):
    Ds, primes = args
    nD = len(Ds)
    nb = len(XS)
    Sp = np.zeros((nb, nD))
    Sm = np.zeros((nb, nD))
    Np = np.zeros((nb, nD), dtype=np.int64)
    Nm = np.zeros((nb, nD), dtype=np.int64)
    for p in primes:
        p = int(p)
        band = next(i for i, X in enumerate(XS) if p <= X)   # band i: XS[i-1] < p <= XS[i]
        c = chi_vec(Ds, p)
        w = math.log(p) / p
        pos = c == 1
        neg = c == -1
        Sp[band, pos] += w
        Sm[band, neg] += w
        Np[band, pos] += 1
        Nm[band, neg] += 1
    return Sp, Sm, Np, Nm


def compute(Ds, primes, procs):
    # interleave primes across workers for load balance
    chunks = [primes[i::procs * 8] for i in range(procs * 8)]
    with Pool(procs) as pool:
        parts = pool.map(_worker, [(Ds, ch) for ch in chunks])
    Sp = sum(x[0] for x in parts)
    Sm = sum(x[1] for x in parts)
    Np = sum(x[2] for x in parts)
    Nm = sum(x[3] for x in parts)
    # cumulative over bands -> values at each X
    return (np.cumsum(Sp, axis=0), np.cumsum(Sm, axis=0),
            np.cumsum(Np, axis=0), np.cumsum(Nm, axis=0))


def validate_chi(Ds, primes, n=500, seed=12345):
    """Compare chi_vec against flint fmpz.jacobi (odd p) and sympy kronecker_symbol."""
    import flint
    from sympy.functions.combinatorial.numbers import kronecker_symbol
    rng = np.random.default_rng(seed)
    bad = []
    pairs = [(int(rng.choice(Ds)), int(rng.choice(primes))) for _ in range(n)]
    pairs += [(int(D), 2) for D in rng.choice(Ds, 50)]
    pairs += [(-163, 41), (-163, 163), (5, 5), (-4, 2), (8, 3), (-3, 3), (12, 3)]
    for D, p in pairs:
        ours = int(chi_vec(np.array([D], dtype=np.int64), p)[0])
        ref_s = int(kronecker_symbol(D, p))
        ref_f = int(flint.fmpz(D).jacobi(p)) if p != 2 else ref_s
        if not (ours == ref_s == ref_f):
            bad.append((D, p, ours, ref_s, ref_f))
    return len(pairs), bad


def rigorous_splus(D, X, primes):
    """S_+(D,X) in arb ball arithmetic; chi from flint/sympy independently of numpy code."""
    import flint
    from sympy.functions.combinatorial.numbers import kronecker_symbol
    flint.ctx.prec = 128
    s = flint.arb(0)
    fD = flint.fmpz(D)
    for p in primes:
        p = int(p)
        if p > X:
            break
        c = int(kronecker_symbol(D, 2)) if p == 2 else int(fD.jacobi(p))
        if c == 1:
            s += flint.arb(p).log() / p
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dmax", type=int, default=10**5)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--date", default="2026-10-08")
    ap.add_argument("--outdir", default="results")
    args = ap.parse_args()

    import flint
    import matplotlib
    t0 = time.time()
    primes = primes_upto(XS[-1])
    Ds = fundamental_discriminants(args.dmax)
    assert len(primes) == 78498 or XS[-1] != 10**6

    nval, bad = validate_chi(Ds, primes)
    if bad:
        print("CHI VALIDATION FAILED", bad[:10])
        sys.exit(1)

    Sp, Sm, Np, Nm = compute(Ds, primes, args.procs)
    t_main = time.time() - t0

    # exact (float64) total Mertens sums for reference
    lw = np.log(primes.astype(float)) / primes
    tot = [lw[primes <= X].sum() for X in XS]

    base = os.path.join(args.outdir, f"{args.date}-prime-bias")
    for path in (base + "-table.csv", base + "-summary.txt"):
        if os.path.exists(path):
            print("refusing to overwrite", path)
            sys.exit(1)

    q = np.abs(Ds)
    ell = np.log(q.astype(float))
    with open(base + "-table.csv", "w", newline="") as f:
        cols = ["D", "q", "ell"]
        for X in XS:
            e = int(round(math.log10(X)))
            cols += [f"S_plus_1e{e}", f"S_minus_1e{e}", f"n_plus_1e{e}", f"n_minus_1e{e}"]
        f.write(",".join(cols) + "\n")
        for j, D in enumerate(Ds):
            row = [str(int(D)), str(int(q[j])), f"{ell[j]:.10f}"]
            for i in range(len(XS)):
                row += [f"{Sp[i, j]:.10f}", f"{Sm[i, j]:.10f}", str(int(Np[i, j])), str(int(Nm[i, j]))]
            f.write(",".join(row) + "\n")

    # rigorous rechecks
    order_last = np.argsort(Sp[-1])[:20]
    t1 = time.time()
    rig = [(int(Ds[j]), Sp[-1, j], rigorous_splus(int(Ds[j]), XS[-1], primes)) for j in order_last]
    t_rig = time.time() - t1

    L = []
    w = L.append
    w("Prime-bias context table (docs/tasks.md task 4). DESCRIPTIVE CONTEXT ONLY; tests no lemma.")
    w("LABEL: EXPLORATORY (float64) for all bulk sums. chi_D(p) values are exact integer computations.")
    w(f"Command: .venv/Scripts/python src/prime_bias.py --dmax {args.dmax} --procs {args.procs} --date {args.date}")
    w(f"Python {platform.python_version()}, numpy {np.__version__}, python-flint {flint.__version__}, "
      f"matplotlib {matplotlib.__version__}, platform {platform.platform()}")
    w(f"Runtime: main computation {t_main:.1f}s; rigorous rechecks {t_rig:.1f}s")
    w(f"Fundamental discriminants: {len(Ds)} (negative {int((Ds<0).sum())}, positive {int((Ds>0).sum())}), |D| <= {args.dmax}")
    w(f"Primes up to {XS[-1]}: {len(primes)}")
    w(f"chi validation: {nval} (D,p) pairs vs sympy kronecker_symbol and flint fmpz.jacobi: all agree")
    w("")
    w("Reference: sum_{p<=X} log p/p (float64) and log X - 1.3325:")
    for X, t in zip(XS, tot):
        w(f"  X=1e{int(round(math.log10(X)))}: {t:.6f}   log X - 1.3325 = {math.log(X)-1.3325:.6f}   half log X = {math.log(X)/2:.6f}")
    w("")
    w("Summary of S_+(D,X) - (1/2) log X:")
    for i, X in enumerate(XS):
        for label, mask in (("all", np.ones(len(Ds), bool)), ("D<0", Ds < 0), ("D>0", Ds > 0)):
            v = Sp[i, mask] - 0.5 * math.log(X)
            qs = np.percentile(v, [1, 5, 25, 50, 75, 95, 99])
            w(f"  X=1e{int(round(math.log10(X)))} {label:4s} n={mask.sum():6d} mean={v.mean():+.4f} sd={v.std():.4f} "
              f"min={v.min():+.4f} max={v.max():+.4f} pct1/5/25/50/75/95/99=" + "/".join(f"{x:+.3f}" for x in qs))
    w("")
    w("Summary of S_+(D,X) - S_-(D,X) = sum_{p<=X} chi_D(p) log p/p (all D):")
    for i, X in enumerate(XS):
        v = Sp[i] - Sm[i]
        qs = np.percentile(v, [1, 5, 25, 50, 75, 95, 99])
        w(f"  X=1e{int(round(math.log10(X)))} mean={v.mean():+.4f} sd={v.std():.4f} min={v.min():+.4f} max={v.max():+.4f} "
          "pct1/5/25/50/75/95/99=" + "/".join(f"{x:+.3f}" for x in qs))
    w("")
    for i, X in enumerate(XS):
        e = int(round(math.log10(X)))
        w(f"20 smallest S_+ at X=1e{e} (float64):")
        w("   rank        D        ell     S_plus    S_minus  S_plus/ell  n_plus  n_minus")
        for r, j in enumerate(np.argsort(Sp[i])[:20], 1):
            w(f"  {r:4d} {int(Ds[j]):9d} {ell[j]:9.4f} {Sp[i,j]:10.5f} {Sm[i,j]:10.5f} {Sp[i,j]/ell[j]:10.4f} {int(Np[i,j]):7d} {int(Nm[i,j]):8d}")
        w("")
    w("20 largest S_+ at X=1e6 (float64), for contrast:")
    for j in np.argsort(Sp[-1])[::-1][:20]:
        w(f"  D={int(Ds[j]):9d}  S_plus={Sp[-1,j]:.5f}  S_minus={Sm[-1,j]:.5f}")
    w("")
    w("Minimum of S_+(D,X)/ell over D, and min S_+ within |D| ranges:")
    for i, X in enumerate(XS):
        e = int(round(math.log10(X)))
        r = Sp[i] / ell
        j = int(np.argmin(r))
        w(f"  X=1e{e}: min S_+/ell = {r[j]:.4f} at D={int(Ds[j])}")
        for lo, hi in ((3, 100), (100, 1000), (1000, 10**4), (10**4, 10**5 + 1)):
            m = (q >= lo) & (q < hi)
            if not m.any():
                continue
            jj = np.nonzero(m)[0][np.argmin(Sp[i, m])]
            w(f"      |D| in [{lo},{hi}): min S_+ = {Sp[i,jj]:.4f} at D={int(Ds[jj])} (ell={ell[jj]:.3f})")
    w("")
    w("Rigorous recheck (python-flint arb, prec=128; chi from flint fmpz.jacobi / sympy) of the 20 smallest S_+ at X=1e6:")
    w("        D   float64 S_plus   arb S_plus (ball)   float64 inside ball?")
    for D, fv, a in rig:
        inside = a.contains(flint.arb(float(fv))) or abs(float(a.mid()) - fv) < 1e-9
        w(f"  {D:9d}  {fv:.12f}  {a.str(20, radius=True)}  diff={fv-float(a.mid()):+.2e} agree_1e-9={inside}")
    text = "\n".join(L) + "\n"
    with open(base + "-summary.txt", "w") as f:
        f.write(text)
    print(text)

    plot(Ds, ell, Sp, base)


def plot(Ds, ell, Sp, base):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    neg = Ds < 0
    for i, X in enumerate(XS):
        e = int(round(math.log10(X)))
        path = f"{base}-splus-vs-ell-1e{e}.png"
        fig, ax = plt.subplots(figsize=(7.5, 5), dpi=130)
        ax.scatter(ell[~neg], Sp[i, ~neg], s=1, alpha=0.25, color="#2a78d6", label="D > 0", rasterized=True)
        ax.scatter(ell[neg], Sp[i, neg], s=1, alpha=0.25, color="#eb6834", label="D < 0", rasterized=True)
        ax.axhline(0.5 * math.log(X), color="#444", lw=1, ls="--", label="½ log X (typical)")
        xx = np.linspace(ell.min(), ell.max(), 50)
        ax.plot(xx, xx, color="#888", lw=1, ls=":", label="S₊ = ℓ")
        ax.set_xlabel("ℓ = log |D|")
        ax.set_ylabel("S₊(D, X) = Σ log p / p over p ≤ X with χ_D(p) = +1")
        ax.set_title(f"S₊ against log conductor, X = 10^{e} (float64, exploratory)")
        ax.spines[["top", "right"]].set_visible(False)
        leg = ax.legend(markerscale=8, frameon=False, loc="lower right")
        for h in leg.legend_handles:
            h.set_alpha(1)
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
    path = f"{base}-hist.png"
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=130)
    colors = ["#86b6ef", "#2a78d6", "#104281"]
    bins = np.linspace(-4, 4, 161)
    for i, X in enumerate(XS):
        e = int(round(math.log10(X)))
        ax.hist(Sp[i] - 0.5 * math.log(X), bins=bins, histtype="step", lw=1.5, color=colors[i], label=f"X = 10^{e}")
    ax.set_xlabel("S₊(D, X) − ½ log X")
    ax.set_ylabel("number of fundamental discriminants")
    ax.set_title(f"Distribution over {len(Ds)} fundamental D, |D| ≤ 10^5 (float64, exploratory)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    main()
