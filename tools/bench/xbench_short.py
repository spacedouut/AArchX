# Short xbench suite: a representative handful of kernels at a low rep count,
# meant to give raw lower-level numbers (median seconds per engine, not just
# the ratio) in a couple of minutes. Run the full suite for the README set.
"""Short xbench suite — quick lower-level numbers.

Six kernels that cover the translator's regimes (string/memory libcalls,
packed FP, a dependent ALU chain, indirect calls, a branchy mix, pointer
chasing) timed with the same paired-delta method as tests/xbench_compare.py,
but reporting raw median deltas so absolute speed is visible too.

Usage:
    python3 tools/bench/xbench_short.py                 # this tree's ocerz
    OCERZ=~/AArchX-c/ocerz OCERZ_LABEL=C python3 tools/bench/xbench_short.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xbench_suite import suite, mermaid

KERNELS = os.environ.get(
    "KERNELS", "memcpy,str,fpvec,depchain,icall,mixed,vm,chase").split(",")

if __name__ == "__main__":
    res = suite(KERNELS, reps=int(os.environ.get("REPS", "3")),
                target=float(os.environ.get("TARGET", "0.5")))
    mermaid(res)
