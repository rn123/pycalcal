#!/usr/bin/env python3
"""Generate the Appendix C sample-data tables from pycalcal, laid out in panels
like the book, so they can be compared side-by-side with the printed Ultimate
Edition Appendix C (whose pages are un-OCR-able images).

Outputs (in recon/):
  appendixC_full.tex  -- 7 landscape longtables (compile with pdflatex)
  appendixC_full.csv  -- one row per date, every column (for programmatic diff)

Values are computed by the Ultimate-Edition pycalcal (differential-verified vs
the Ultimate Lisp; see docs/ultimate-check-report.md). Dates are rendered as the
book does -- raw function output, negative = B.C.E., leap flags as t/f.

Run from repo root: .venv/bin/python tools/gen_appendix_c.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pycalcal as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
ROMAN_EV = {p.KALENDS: "Kal", p.NONES: "Non", p.IDES: "Id"}


def sample_dates():
    with open(os.path.join(ROOT, "dates1.csv")) as fh:
        return [int(r[0]) for r in csv.reader(fh) if r]


# ---- cell renderers (return a plain string) -------------------------------

def d(v):
    """Render a raw calendar list: space-joined, bool -> t/f."""
    out = []
    for x in v:
        out.append("t" if x is True else ("f" if x is False else str(x)))
    return " ".join(out)


def weekday(rd):
    return WEEKDAYS[p.day_of_week_from_fixed(rd)]


def jd(rd):
    return "%.1f" % float(p.jd_from_fixed(rd))


def roman(rd):
    r = p.roman_from_fixed(rd)
    leap = "*" if p.roman_leap(r) else ""
    return "%d %s %d%s %d" % (p.roman_count(r), ROMAN_EV[p.roman_event(r)],
                              p.roman_month(r), leap, p.roman_year(r))


def easter_g(rd, fn):
    g = p.gregorian_year_from_fixed(rd)
    return d(p.gregorian_from_fixed(fn(g)))


def fnum(x):
    return "%.6f" % float(x)


def gyear(rd):
    return p.gregorian_year_from_fixed(rd)


# ---- panels: (title, [(header, renderer), ...]) ---------------------------

PANELS = [
    ("I. Day count and Western calendars", [
        ("R.D.", str),
        ("Weekday", weekday),
        ("J.D.", jd),
        ("M.J.D.", lambda rd: str(p.mjd_from_fixed(rd))),
        ("Gregorian", lambda rd: d(p.gregorian_from_fixed(rd))),
        ("ISO", lambda rd: d(p.iso_from_fixed(rd))),
        ("Julian", lambda rd: d(p.julian_from_fixed(rd))),
        ("Roman", roman),
        ("Egyptian", lambda rd: d(p.egyptian_from_fixed(rd))),
        ("Armenian", lambda rd: d(p.armenian_from_fixed(rd))),
    ]),
    ("II. Coptic, Ethiopic, Akan, Icelandic, Easter", [
        ("R.D.", str),
        ("Coptic", lambda rd: d(p.coptic_from_fixed(rd))),
        ("Ethiopic", lambda rd: d(p.ethiopic_from_fixed(rd))),
        ("Akan", lambda rd: d(p.akan_name_from_fixed(rd))),
        ("Icelandic", lambda rd: d(p.icelandic_from_fixed(rd))),
        ("Easter (Orth.)", lambda rd: easter_g(rd, p.orthodox_easter)),
        ("Easter (Greg.)", lambda rd: easter_g(rd, p.easter)),
        ("Easter (Astro.)", lambda rd: easter_g(rd, p.astronomical_easter)),
    ]),
    ("III. Islamic, Hebrew, Samaritan, Babylonian", [
        ("R.D.", str),
        ("Islamic (arith.)", lambda rd: d(p.islamic_from_fixed(rd))),
        ("Islamic (obs.)", lambda rd: d(p.observational_islamic_from_fixed(rd))),
        ("Umm al-Qura", lambda rd: d(p.saudi_islamic_from_fixed(rd))),
        ("Hebrew (std.)", lambda rd: d(p.hebrew_from_fixed(rd))),
        ("Hebrew (obs.)", lambda rd: d(p.observational_hebrew_from_fixed(rd))),
        ("Samaritan", lambda rd: d(p.samaritan_from_fixed(rd))),
        ("Babylonian", lambda rd: d(p.babylonian_from_fixed(rd))),
    ]),
    ("IV. Persian, Baha'i, French Revolutionary", [
        ("R.D.", str),
        ("Persian (astro.)", lambda rd: d(p.persian_from_fixed(rd))),
        ("Persian (arith.)", lambda rd: d(p.arithmetic_persian_from_fixed(rd))),
        ("Baha'i (Western)", lambda rd: d(p.bahai_from_fixed(rd))),
        ("Baha'i (astro.)", lambda rd: d(p.astro_bahai_from_fixed(rd))),
        ("French (orig.)", lambda rd: d(p.french_from_fixed(rd))),
        ("French (arith.)", lambda rd: d(p.arithmetic_french_from_fixed(rd))),
    ]),
    ("V. Mayan, Aztec, Balinese", [
        ("R.D.", str),
        ("Mayan Long Count", lambda rd: d(p.mayan_long_count_from_fixed(rd))),
        ("Mayan Haab", lambda rd: d(p.mayan_haab_from_fixed(rd))),
        ("Mayan Tzolkin", lambda rd: d(p.mayan_tzolkin_from_fixed(rd))),
        ("Aztec Xihuitl", lambda rd: d(p.aztec_xihuitl_from_fixed(rd))),
        ("Aztec Tonalpohualli", lambda rd: d(p.aztec_tonalpohualli_from_fixed(rd))),
        ("Balinese Pawukon", lambda rd: d(p.bali_pawukon_from_fixed(rd))),
    ]),
    ("VI. Chinese, Hindu, Tibetan", [
        ("R.D.", str),
        ("Chinese", lambda rd: d(p.chinese_from_fixed(rd))),
        ("Hindu solar", lambda rd: d(p.hindu_solar_from_fixed(rd))),
        ("Hindu lunar", lambda rd: d(p.hindu_lunar_from_fixed(rd))),
        ("Astro Hindu solar", lambda rd: d(p.astro_hindu_solar_from_fixed(rd))),
        ("Astro Hindu lunar", lambda rd: d(p.astro_hindu_lunar_from_fixed(rd))),
        ("Old Hindu solar", lambda rd: d(p.old_hindu_solar_from_fixed(rd))),
        ("Old Hindu lunar", lambda rd: d(p.old_hindu_lunar_from_fixed(rd))),
        ("Tibetan", lambda rd: d(p.tibetan_from_fixed(rd))),
    ]),
    ("VII. Astronomy (U.T.)", [
        ("R.D.", str),
        ("Solar long. (noon)", lambda rd: fnum(p.solar_longitude(rd + 0.5))),
        ("Next equinox/solst.", lambda rd: fnum(min(
            p.solar_longitude_after(p.SPRING, rd),
            p.solar_longitude_after(p.SUMMER, rd),
            p.solar_longitude_after(p.AUTUMN, rd),
            p.solar_longitude_after(p.WINTER, rd)))),
        ("Lunar long. (midn.)", lambda rd: fnum(p.lunar_longitude(rd))),
        ("Next new moon", lambda rd: fnum(p.new_moon_at_or_after(rd))),
    ]),
]


def render_latex(dates):
    out = [r"% Generated by tools/gen_appendix_c.py -- do not edit.",
           r"\documentclass[8pt]{extarticle}",
           r"\usepackage[a3paper,landscape,margin=1cm]{geometry}",
           r"\usepackage{longtable,booktabs}",
           r"\setlength{\tabcolsep}{3pt}\pagestyle{empty}",
           r"\begin{document}",
           r"\begin{center}{\large Calendrical Calculations --- Appendix C "
           r"(reconstruction from pycalcal, Ultimate Edition)}\\[2pt]",
           r"{\footnotesize 33 sample dates; raw function output, negative = "
           r"B.C.E., leap flags as t/f. $^\ast$ = Roman leap year.}\end{center}"]
    for title, cols in PANELS:
        out.append(r"\section*{%s}" % title.replace("'", "'"))
        out.append(r"\footnotesize")
        out.append(r"\begin{longtable}{r " + "l " * (len(cols) - 1) + "}")
        out.append(r"\toprule")
        out.append(" & ".join("\\textbf{%s}" % c[0].replace("&", "\\&")
                              for c in cols) + r" \\")
        out.append(r"\midrule\endhead")
        for rd in dates:
            cells = [c[1](rd).replace("&", "\\&") for c in cols]
            out.append(" & ".join(cells) + r" \\")
        out.append(r"\bottomrule\end{longtable}\newpage")
    out.append(r"\end{document}")
    return "\n".join(out) + "\n"


def main():
    dates = sample_dates()
    out_dir = os.path.join(ROOT, "recon")
    os.makedirs(out_dir, exist_ok=True)

    # CSV: every column flattened.
    headers = ["R.D."]
    for _, cols in PANELS:
        headers += [c[0] for c in cols if c[0] != "R.D."]
    with open(os.path.join(out_dir, "appendixC_full.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(headers)
        for rd in dates:
            row = [rd]
            for _, cols in PANELS:
                row += [c[1](rd) for c in cols if c[0] != "R.D."]
            w.writerow(row)

    tex_path = os.path.join(out_dir, "appendixC_full.tex")
    with open(tex_path, "w") as fh:
        fh.write(render_latex(dates))
    print("Wrote recon/appendixC_full.tex and recon/appendixC_full.csv"
          " (%d dates, %d panels)" % (len(dates), len(PANELS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
