#!/usr/bin/env python3
"""Body-level diff of every shared definition between calendrica-3.0.cl (clean)
and ultimate_calendrica.lisp (repaired Ultimate). Reports which function/constant
BODIES changed between editions -- the precise port list for full parity.

Normalization: strip comments, collapse whitespace, lowercase. So only real code
differences are reported (formatting/comment noise removed).

Run from repo root: .venv/bin/python tools/lisp_body_diff.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repair_ultimate_lisp import strip_comment, _extract_top_forms

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEEP = {"defun", "defconstant", "defmacro", "defparameter", "defvar"}


def forms_of(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    raw = raw.replace("‘", "`").replace("’", "'") \
             .replace("“", '"').replace("”", '"')
    blob = "\n".join(strip_comment(ln) for ln in raw.splitlines())
    blob = re.sub(r"\((?:Table\s+)?\d+\.\d+[a-z]?\)", " ", blob)
    out = {}
    for form in _extract_top_forms(blob, KEEP):
        m = re.match(r"\(\s*(def\w+)\s+([A-Za-z0-9*+/<>=!?._-]+)", form)
        if not m:
            continue
        kind, name = m.group(1).lower(), m.group(2).lower()
        norm = re.sub(r"\s+", " ", form).strip().lower()
        out[name] = (kind, norm)
    return out


def main():
    a = forms_of(os.path.join(ROOT, "calendrica-3.0.cl"))
    b = forms_of(os.path.join(ROOT, "ultimate_calendrica.lisp"))
    shared = sorted(set(a) & set(b))
    changed = [n for n in shared if a[n][1] != b[n][1]]
    only_b = sorted(set(b) - set(a))
    only_a = sorted(set(a) - set(b))

    print("3.0 defs: %d   Ultimate defs: %d   shared: %d" % (len(a), len(b), len(shared)))
    print("\nCHANGED BODIES (%d) -- the port targets for full parity:" % len(changed))
    for n in sorted(changed):
        print("  %-34s [%s]" % (n, a[n][0]))
    print("\nNEW in Ultimate (%d):" % len(only_b))
    print("  " + " ".join(only_b))
    print("\nOnly in 3.0 / renamed away (%d):" % len(only_a))
    print("  " + " ".join(only_a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
