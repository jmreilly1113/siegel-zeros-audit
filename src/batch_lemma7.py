"""Run src/lemma7_check.run over a grid of (d, N, H) in parallel and write one JSON
record per line.

Usage: python src/batch_lemma7.py OUT.jsonl N H1,H2,... d1,d2,... [--procs K] [--flint] [--regdet]
--flint uses src/lemma7_flint.run (exact, faster); --regdet also computes N(Delta) by the
regular-representation determinant as a second method (flint only).
"""
import json
import multiprocessing as mp
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lemma7_check as L  # noqa: E402


def job(args):
    d, N, H, use_flint, regdet = args
    t0 = time.perf_counter()
    if use_flint:
        import lemma7_flint as F
        res = F.run(d, N, H, quiet=True, regdet=regdet)
    else:
        res = L.run(d, N, H, quiet=True)
    res["timing"]["total_s"] = time.perf_counter() - t0
    return res


def main():
    argv = sys.argv[1:]
    procs = None
    if "--procs" in argv:
        i = argv.index("--procs")
        procs = int(argv[i + 1])
        del argv[i:i + 2]
    use_flint = "--flint" in argv
    regdet = "--regdet" in argv
    argv = [a for a in argv if a not in ("--flint", "--regdet")]
    out, N, Hs, ds = argv[0], int(argv[1]), argv[2], argv[3]
    Hs = [int(x) for x in Hs.split(",")]
    ds = [int(x) for x in ds.split(",")]
    jobs = [(d, N, H, use_flint, regdet) for H in Hs for d in ds]
    try:
        import flint
        fv = flint.__version__
    except ImportError:
        fv = None
    header = dict(kind="header", argv=sys.argv, python=sys.version, python_flint=fv,
                  platform=platform.platform(), started=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(out, "x", encoding="utf-8") as f:   # never overwrite
        f.write(json.dumps(header) + "\n")
        with mp.Pool(procs) as pool:
            for res in pool.imap_unordered(job, jobs):
                f.write(json.dumps(res) + "\n")
                f.flush()
                bad = [r["p"] for r in res["primes"] if r["admissible"] and not r["vp_ge_4Ep"]]
                print(f"d={res['d']:4d} N={res['N']} H={res['H']} maxw={res['max_weight']} "
                      f"S1={res['S1']} S2={res['S2']} lemma7={'ok' if not bad else 'FAIL ' + str(bad)} "
                      f"{res['timing']['total_s']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
