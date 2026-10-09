# Full xbench suite: every kernel that appears in the README graph, in the
# graph's order, with the dynamically linked guest (xbench_dyn against
# libSystem, cache mode) — the same measurement the README numbers come from.
# Takes a while (calibration + 5 reps + alternating order per kernel); expect
# upwards of 20 minutes on a quiet machine.
"""Full README-graph xbench suite (dynamic build, cache mode).

Usage:
    python3 tools/bench/xbench_full.py                  # this tree's ocerz
    OCERZ=~/AArchX-c/ocerz OCERZ_LABEL=C python3 tools/bench/xbench_full.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xbench_suite import suite, mermaid, README_ORDER

if __name__ == "__main__":
    # xbench_dyn is the libSystem-linked build the README graph measures.
    os.environ.setdefault("OCERZ_HOSTWQ", "1")
    import xbench_suite as xs
    xs.XB = os.environ.get(
        "XB", os.path.join(xs.REPO, "tests/guest/benchbin/xbench_dyn"))
    res = suite(README_ORDER, reps=int(os.environ.get("REPS", "5")),
                target=float(os.environ.get("TARGET", "0.6")))
    mermaid(res)
