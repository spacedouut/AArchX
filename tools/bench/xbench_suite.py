# Shared harness for the xbench kernel suites: paired-delta timing against
# Rosetta on the same machine. Tests/xbench_compare.py drives it via env
# knobs; this file exists so the short and full suites share one definition
# of the kernel order used by the README graph.
"""Shared xbench harness. Used by xbench_short.py and xbench_full.py.

Env: OCERZ (translator binary), XB (xbench guest binary), REPS, TARGET,
OCERZ_LABEL for the column heading. Prints raw median deltas for both
engines, the ratio, and a mermaid `bar [...]` line in README order."""
import os, subprocess, sys, time, statistics

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OCERZ = os.environ.get("OCERZ", os.path.join(REPO, "ocerz"))
XB = os.environ.get("XB", os.path.join(REPO, "tests/guest/benchbin/xbench"))
LABEL = os.environ.get("OCERZ_LABEL", "Ocerz")
REPS = int(os.environ.get("REPS", "3"))
TARGET = float(os.environ.get("TARGET", "0.6"))

# README graph order; the DFLT scales are seeds, recalibrated per machine.
DFLT = dict(icall=50000000, jtab=50000000, depchain=100000000, brmiss=50000000,
            memcpy=2000000, str=20000000, hash=20000, idiv=10000000,
            fpsse=30000000, fpvec=5000, chase=30000000, qsort=30,
            leafcall=50000000, mixed=20000, vm=500000,
            x87=20000, x87pc24=20000)
README_ORDER = ["memcpy", "str", "fpvec", "mixed", "vm", "fpsse", "depchain",
                "icall", "brmiss", "qsort", "jtab", "hash", "idiv", "chase",
                "leafcall"]

LAST_ERR = {}
def run(engine, k, n):
    cmd = [XB, k, str(n)] if engine == "R" else [OCERZ, XB, k, str(n)]
    t0 = time.perf_counter()
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    LAST_ERR[(engine, k, n)] = (r.returncode, r.stderr[-2000:])
    return time.perf_counter() - t0, r.stdout


def suite(kernels, reps=REPS, target=TARGET):
    """Run `kernels` with the paired-delta method; return {k: (n, rmed, omed, ratio)}."""
    print(f"engine under test: {OCERZ}")
    print(f"guest binary:      {XB}   reps={reps} target={target}s")
    hdr = f"{'kernel':<10}{'scale':>12}{'Rosetta_s':>11}{LABEL + '_s':>11}{'ratio':>9}  verdict"
    print(hdr); print("-" * len(hdr))
    out = {}
    for k in kernels:
        n = DFLT[k]
        for _ in range(6):
            t, _ = run("R", k, n)
            if t >= target * 0.5: break
            n = max(2, int(n * min(30.0, target / max(t, 0.02))))
        half = max(1, n // 2)
        rd, od, ratios = [], [], []
        for rep in range(reps):
            if rep % 2 == 0:
                rl, ro = run("R", k, half); ol, oo = run("O", k, half)
                rh, ro2 = run("R", k, n);   oh, oo2 = run("O", k, n)
            else:
                oh, oo2 = run("O", k, n);   rh, ro2 = run("R", k, n)
                ol, oo = run("O", k, half); rl, ro = run("R", k, half)
            if ro != oo or ro2 != oo2:
                print(f"{k}: OUTPUT MISMATCH half rosetta={ro!r} ocerz={oo!r} "
                      f"full rosetta={ro2!r} ocerz={oo2!r}")
                for key in (("O", k, half), ("O", k, n)):
                    rc, err = LAST_ERR.get(key, (None, b""))
                    print(f"  ocerz {key}: rc={rc} stderr={err!r}")
                sys.exit(2)
            rd.append(max(rh - rl, 1e-3)); od.append(max(oh - ol, 1e-3))
            ratios.append(od[-1] / rd[-1])
        rm, om, ratio = statistics.median(rd), statistics.median(od), statistics.median(ratios)
        out[k] = (n, rm, om, ratio)
        print(f"{k:<10}{n:>12}{rm:>11.4f}{om:>11.4f}{ratio:>8.3f}x  "
              f"{'WIN' if ratio < 1.0 else 'LOSE'}")
    return out


def mermaid(results):
    """README-graph xychart lines, in README kernel order."""
    ks = [k for k in README_ORDER if k in results]
    print("\nmermaid lines (README order):")
    print("    x-axis [" + ", ".join(ks) + "]")
    print("    bar [" + ", ".join(f"{results[k][3]:.2f}" for k in ks) + "]")
