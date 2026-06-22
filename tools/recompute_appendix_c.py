#!/usr/bin/env python3
"""Roegel-style reconstruction of Calendrical Calculations, Appendix C (panel 1).

Rather than OCR the printed (raster) sample-data tables of the Ultimate Edition,
we *recompute* the values from pycalcal — exactly the LOCOMAT principle: a table
you can compute should never be transcribed. The pipeline mirrors Roegel's:

  1. recompute every cell from the implementation (pycalcal);
  2. cross-check against an independent source (the author-supplied dates1.tex,
     delivered as dates1.csv) — this is the errata-detection step;
  3. emit LaTeX that reproduces the *structure* of the book's Appendix C panel,
     with a footer naming the function behind each column (the book prints the
     equation number + page; we print the pycalcal function — column provenance).

This covers Appendix C "panel 1": the 10 calendars pycalcal implements from
CALENDRICA 3.0. The Ultimate Edition adds Babylonian, Icelandic, Samaritan,
Akan and Saudi-Islamic columns that pycalcal does not yet provide (see
docs/ultimate-edition-diff.md); those are out of scope for this prototype.

Usage:
    python tools/recompute_appendix_c.py            # -> recon/appendixC_panel1.tex
    python tools/recompute_appendix_c.py --check     # validate only, no output
"""
import csv
import sys
import os

# Allow running from anywhere: the package lives at the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pycalcal as p

WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday"]
ROMAN_EVENT = {p.KALENDS: "Kal", p.NONES: "Non", p.IDES: "Id"}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def sample_rd_dates(path):
    """The 33 canonical R.D. sample dates (column 0 of the book's panel 1)."""
    with open(path) as fh:
        return [int(row[0]) for row in csv.reader(fh) if row]


def recompute(rd):
    """Recompute every panel-1 calendar for one R.D. date, via pycalcal."""
    rom = p.roman_from_fixed(rd)
    return {
        "rd": rd,
        "weekday": WEEKDAYS[p.day_of_week_from_fixed(rd)],
        "jd": p.jd_from_fixed(rd),
        "mjd": p.mjd_from_fixed(rd),
        "gregorian": p.gregorian_from_fixed(rd),
        "iso": p.iso_from_fixed(rd),
        "julian": p.julian_from_fixed(rd),
        "roman": rom,
        "egyptian": p.egyptian_from_fixed(rd),
        "armenian": p.armenian_from_fixed(rd),
        "coptic": p.coptic_from_fixed(rd),
    }


def book_row(row):
    """Parse one dates1.csv row into the same shape as recompute(), for diffing."""
    i = iter(row)
    rd = int(next(i)); weekday = next(i)
    jd = float(next(i)); mjd = int(next(i))
    g = [int(next(i)) for _ in range(3)]
    iso = [int(next(i)) for _ in range(3)]
    jul = [int(next(i)) for _ in range(3)]
    ry, rm, rev, rc = (int(next(i)) for _ in range(4))
    rleap = (next(i) != "f")
    rom = p.roman_date(ry, rm, rev, rc, rleap)
    egy = [int(next(i)) for _ in range(3)]
    arm = [int(next(i)) for _ in range(3)]
    cop = [int(next(i)) for _ in range(3)]
    return {"rd": rd, "weekday": weekday, "jd": jd, "mjd": mjd,
            "gregorian": g, "iso": iso, "julian": jul, "roman": rom,
            "egyptian": egy, "armenian": arm, "coptic": cop}


def cross_check(csv_path):
    """Recompute vs. the author-supplied book values. Returns list of mismatches."""
    mismatches = []
    with open(csv_path) as fh:
        for row in csv.reader(fh):
            if not row:
                continue
            want = book_row(row)
            got = recompute(want["rd"])
            for col in got:
                if got[col] != want[col]:
                    mismatches.append((want["rd"], col, want[col], got[col]))
    return mismatches


# ---- LaTeX rendering -------------------------------------------------------

def ymd(d):
    return "{}.{}.{}".format(*d)


def roman_tex(r):
    ev = ROMAN_EVENT[p.roman_event(r)]
    leap = r"$^\ast$" if p.roman_leap(r) else ""
    return "{}\\,{}\\,{}{} ({})".format(
        p.roman_count(r), ev, p.roman_month(r), leap, p.roman_year(r))


COLUMNS = [
    ("R.D.",      lambda r: str(r["rd"]),                   "(argument)"),
    ("Weekday",   lambda r: r["weekday"],                   "day\\_of\\_week\\_from\\_fixed"),
    ("J.D.",      lambda r: ("%.1f" % r["jd"]),             "jd\\_from\\_fixed"),
    ("M.J.D.",    lambda r: str(r["mjd"]),                  "mjd\\_from\\_fixed"),
    ("Gregorian", lambda r: ymd(r["gregorian"]),           "gregorian\\_from\\_fixed"),
    ("ISO",       lambda r: ymd(r["iso"]),                  "iso\\_from\\_fixed"),
    ("Julian",    lambda r: ymd(r["julian"]),              "julian\\_from\\_fixed"),
    ("Roman",     lambda r: roman_tex(r["roman"]),          "roman\\_from\\_fixed"),
    ("Egyptian",  lambda r: ymd(r["egyptian"]),            "egyptian\\_from\\_fixed"),
    ("Armenian",  lambda r: ymd(r["armenian"]),            "armenian\\_from\\_fixed"),
    ("Coptic",    lambda r: ymd(r["coptic"]),              "coptic\\_from\\_fixed"),
]


def render_latex(rows):
    colspec = "r l r r " + "l " * 7
    out = []
    a = out.append
    a(r"% Generated by tools/recompute_appendix_c.py -- do not edit by hand.")
    a(r"\documentclass[10pt]{article}")
    a(r"\usepackage[a3paper,landscape,margin=1.5cm]{geometry}")
    a(r"\usepackage{booktabs}")
    a(r"\usepackage{longtable}")
    a(r"\pagestyle{empty}")
    a(r"\setlength{\tabcolsep}{4pt}")
    a(r"\begin{document}")
    a(r"\begin{center}")
    a(r"{\large Calendrical Calculations --- Appendix C, panel 1 "
      r"(reconstruction)}\\[2pt]")
    a(r"{\small Recomputed from \texttt{pycalcal}; layout after Dershowitz \&"
      r" Reingold. $^\ast$ = Roman leap year.}")
    a(r"\end{center}")
    a(r"\footnotesize")
    a(r"\begin{longtable}{" + colspec + "}")
    a(r"\toprule")
    a(" & ".join(c[0] for c in COLUMNS) + r" \\")
    a(r"\midrule")
    a(r"\endhead")
    for r in rows:
        a(" & ".join(c[1](r) for c in COLUMNS) + r" \\")
    a(r"\midrule")
    # Roegel-style column provenance footer (the book prints eqn no. + page).
    a(r"\multicolumn{%d}{l}{\itshape pycalcal function per column:} \\" % len(COLUMNS))
    for name, _, fn in COLUMNS:
        a(r"\multicolumn{%d}{l}{\quad %s: \texttt{%s}} \\" % (len(COLUMNS), name, fn))
    a(r"\bottomrule")
    a(r"\end{longtable}")
    a(r"\end{document}")
    return "\n".join(out) + "\n"


def main():
    csv_path = os.path.join(ROOT, "dates1.csv")
    if not os.path.exists(csv_path):
        sys.exit("dates1.csv not found -- run `make testdata` first.")

    mism = cross_check(csv_path)
    if mism:
        print("CROSS-CHECK: %d discrepancy(ies) vs. book data:" % len(mism))
        for rd, col, want, got in mism:
            print("  R.D. %d  %s: book=%r  recomputed=%r" % (rd, col, want, got))
    else:
        print("CROSS-CHECK: all 33 dates x 10 calendars agree with book data.")

    if "--check" in sys.argv:
        return 0 if not mism else 1

    rows = [recompute(rd) for rd in sample_rd_dates(csv_path)]
    out_dir = os.path.join(ROOT, "recon")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "appendixC_panel1.tex")
    with open(out_path, "w") as fh:
        fh.write(render_latex(rows))
    print("Wrote %s (%d rows)" % (out_path, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
