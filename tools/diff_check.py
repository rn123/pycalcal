#!/usr/bin/env python3
"""Phase 2/3 differential check: pycalcal vs the repaired Ultimate Lisp oracle.

Generates a deterministic set of fixed dates, runs tools/diff_oracle.lisp under
SBCL to dump the Ultimate Lisp's values, computes pycalcal's values for the same
dates, and reports per-function agreement.

  * integer/date-structured *-from-fixed -> exact comparison
  * float astronomy labels                -> tolerance comparison

Functions pycalcal lacks (new Ultimate calendars) are reported separately.

Run from repo root: .venv/bin/python tools/diff_check.py
"""
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pycalcal as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOAT_TOL = 1e-6
FLOAT_LABELS = {"SOLAR-LONGITUDE-NOON", "LUNAR-LONGITUDE-MID", "LUNAR-PHASE-MID"}

SAMPLE_33 = [-214193, -61387, 25469, 49217, 171307, 210155, 253427, 369740,
             400085, 434355, 452605, 470160, 473837, 507850, 524156, 544676,
             567118, 569477, 601716, 613424, 626596, 645554, 664224, 671401,
             694799, 704424, 708842, 709409, 709580, 727274, 728714, 744313,
             764652]


def gen_dates(n=1500, seed=20260621):
    r = random.Random(seed)
    dates = set(SAMPLE_33)
    for _ in range(n):
        dates.add(r.randint(-250000, 800000))
    # boundary-ish: around each sample (leap/month edges)
    for d in SAMPLE_33:
        for off in (-1, 1, 365, -365):
            dates.add(d + off)
    return sorted(dates)


# ---- minimal Lisp value parser (ints, floats, NIL/T, strings, flat/nested lists)

def parse_sexpr(s):
    i, n = 0, len(s)
    def tokenize():
        nonlocal i
        res = []
        while i < n:
            c = s[i]
            if c.isspace():
                i += 1
            elif c == '(':
                i += 1
                res.append(tokenize())
            elif c == ')':
                i += 1
                return res
            elif c == '"':
                j = i + 1
                while j < n and s[j] != '"':
                    j += 1
                res.append(s[i + 1:j]); i = j + 1
            else:
                j = i
                while j < n and not s[j].isspace() and s[j] not in '()':
                    j += 1
                res.append(atom(s[i:j])); i = j
        return res
    if s.strip().startswith('('):
        return tokenize()[0]
    return atom(s.strip())


def atom(t):
    if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
        return t[1:-1]
    u = t.upper()
    if u == 'NIL':
        return False
    if u == 'T':
        return True
    tt = t.replace('d', 'e').replace('D', 'e').replace('L', 'e')
    try:
        return int(t)
    except ValueError:
        pass
    try:
        return float(tt)
    except ValueError:
        return t


def lisp_name_to_py(name):
    return name.lower().replace('-', '_')


def run_oracle(dates):
    with open(os.path.join(ROOT, "diff_dates.txt"), "w") as fh:
        fh.write("\n".join(str(d) for d in dates) + "\n")
    out = subprocess.run(
        ["sbcl", "--non-interactive", "--load", "tools/diff_oracle.lisp"],
        cwd=ROOT, capture_output=True, text=True, timeout=900)
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split(" ", 2)
        if len(parts) == 3 and parts[0].lstrip("-").isdigit():
            rows.append((int(parts[0]), parts[1], parts[2]))
    return rows


def py_value(name, rd):
    fn = getattr(p, lisp_name_to_py(name), None)
    if fn is None:
        return None, False
    try:
        v = fn(rd)
        return v, True
    except Exception:
        return None, False


def norm(v):
    if isinstance(v, list):
        return [norm(x) for x in v]
    if isinstance(v, bool):
        return v
    return v


def main():
    dates = gen_dates()
    print("Running Ultimate Lisp oracle over %d dates..." % len(dates))
    rows = run_oracle(dates)
    if not rows:
        sys.exit("No oracle output -- check SBCL / ultimate_calendrica.lisp")

    stats = {}   # name -> dict(tested, mism, sample, kind, no_py)
    for rd, name, raw in rows:
        st = stats.setdefault(name, dict(tested=0, mism=0, sample=None,
                                         kind="float" if name in FLOAT_LABELS else "int",
                                         no_py=False))
        lv = parse_sexpr(raw)
        if name in FLOAT_LABELS:
            label = {"SOLAR-LONGITUDE-NOON": ("solar_longitude", rd + 0.5),
                     "LUNAR-LONGITUDE-MID": ("lunar_longitude", rd),
                     "LUNAR-PHASE-MID": ("lunar_phase", rd)}[name]
            fn = getattr(p, label[0], None)
            if fn is None:
                st["no_py"] = True; continue
            try:
                pv = float(fn(label[1]))
            except Exception:
                continue
            st["tested"] += 1
            if abs(pv - float(lv)) > FLOAT_TOL:
                st["mism"] += 1
                if st["sample"] is None:
                    st["sample"] = (rd, lv, pv)
        else:
            pv, ok = py_value(name, rd)
            if not ok:
                st["no_py"] = True; continue
            st["tested"] += 1
            if norm(pv) != norm(lv):
                st["mism"] += 1
                if st["sample"] is None:
                    st["sample"] = (rd, lv, pv)

    exact, diff, nopy = [], [], []
    for name, st in stats.items():
        if st["no_py"] and st["tested"] == 0:
            nopy.append(name)
        elif st["mism"] == 0 and st["tested"] > 0:
            exact.append(name)
        elif st["tested"] > 0:
            diff.append((name, st))

    print("\n================ pycalcal vs Ultimate Lisp ================")
    print("dates: %d   functions dumped: %d" % (len(dates), len(stats)))
    print("\nEXACT/within-tol agreement (%d):\n  %s" %
          (len(exact), " ".join(sorted(exact))))
    print("\nDIFFER (%d):" % len(diff))
    for name, st in sorted(diff):
        rd, lv, pv = st["sample"]
        print("  %-38s %4d/%-4d differ  e.g. rd=%d ULT=%r py=%r %s" %
              (name, st["mism"], st["tested"], rd, lv, pv,
               "[float]" if st["kind"] == "float" else ""))
    print("\nNEW in Ultimate / no pycalcal equivalent (%d):\n  %s" %
          (len(nopy), " ".join(sorted(nopy))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
