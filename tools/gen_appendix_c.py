#!/usr/bin/env python3
"""Generate the Appendix C sample-data tables from pycalcal, laid out to match
the printed Ultimate Edition (4th ed.) Appendix C exactly, panel by panel, so the
output lines up page-for-page with the book (pp. 756-761).

Column headers, order, and groupings were read from the printed tables by VLM:
  p.756  Akan, Coptic, Ethiopic, ISO, Icelandic, Islamic{Arith,Obs,Umm al-Qura},
         Hebrew{Standard,Observational}
  p.757  Persian{Astro,Arith}, Baha'i{Western,Astro}, French Rev{Orig,Modified},
         Easter (same year){Julian,Gregorian,Astronomical}
  p.758  Mayan{Long Count,Haab,Tzolkin}, Aztec{Xihuitl,Tonalpohualli},
         Balinese Pawukon, Babylonian, Samaritan
  p.759  Chinese{Date,Name,Next Zhongqi}, Hindu Solar{Old,Modern,Astronomical},
         Hindu Lunisolar{Old,Modern,Astronomical}, Tibetan
  p.760  Ephemeris Correction, Equation of Time, Solar Longitude at 12:00:00 U.T.,
         Next Solstice/Equinox, Dawn in Paris, Midday in Tehran, Sunset in Jerusalem
  p.761  Lunar Position at 00:00:00 U.T.{Longitude,Latitude,Altitude},
         Next New Moon, In Mecca{Moonrise,Moonset}

The 4th-edition Appendix C OMITS Gregorian/Julian/Roman/Egyptian/Armenian/weekday/
JD/MJD; those are emitted as a clearly-labelled SUPPLEMENT (panel S), not in the book.

Outputs (recon/): appendixC_full.tex (compile w/ pdflatex) + appendixC_full.csv.
Values come from the Ultimate-Edition pycalcal (differential-verified vs the
Ultimate Lisp). Raw function output; negative = B.C.E.; leap flags t/f.

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
PARIS_DAWN_ALPHA = p.angle(18, 0, 0)   # astronomical dawn


def sample_dates():
    with open(os.path.join(ROOT, "dates1.csv")) as fh:
        return [int(r[0]) for r in csv.reader(fh) if r]


# ---- cell renderers --------------------------------------------------------

def d(v):
    return " ".join("t" if x is True else ("f" if x is False else str(x))
                    for x in v)


def fnum(x):
    return "%.6f" % float(x)


def ftime(moment):
    if moment == p.BOGUS:
        return "---"
    h, m, s = p.clock_from_moment(moment)
    return "%02d:%02d:%02d" % (int(h), int(m), int(round(float(s))))


def easter_g(rd, fn):
    return d(p.gregorian_from_fixed(fn(p.gregorian_year_from_fixed(rd))))


def roman(rd):
    r = p.roman_from_fixed(rd)
    leap = "*" if p.roman_leap(r) else ""
    return "%d %s %d%s %d" % (p.roman_count(r), ROMAN_EV[p.roman_event(r)],
                              p.roman_month(r), leap, p.roman_year(r))


RD = ("R.D.", [("", str)])   # the index column, reused in every panel


# A panel is (page-ref, title, [group, ...]); a group is (group-label, [(sub, fn)]).
PANELS = [
    ("p.756", "Akan / Coptic / Ethiopic / ISO / Icelandic / Islamic / Hebrew", [
        RD,
        ("Akan", [("", lambda rd: d(p.akan_name_from_fixed(rd)))]),
        ("Coptic", [("", lambda rd: d(p.coptic_from_fixed(rd)))]),
        ("Ethiopic", [("", lambda rd: d(p.ethiopic_from_fixed(rd)))]),
        ("ISO", [("", lambda rd: d(p.iso_from_fixed(rd)))]),
        ("Icelandic", [("", lambda rd: d(p.icelandic_from_fixed(rd)))]),
        ("Islamic", [("Arith.", lambda rd: d(p.islamic_from_fixed(rd))),
                     ("Obs.", lambda rd: d(p.observational_islamic_from_fixed(rd))),
                     ("Umm al-Qura", lambda rd: d(p.saudi_islamic_from_fixed(rd)))]),
        ("Hebrew", [("Standard", lambda rd: d(p.hebrew_from_fixed(rd))),
                    ("Observational",
                     lambda rd: d(p.observational_hebrew_from_fixed(rd)))]),
    ]),
    ("p.757", "Persian / Baha'i / French Revolutionary / Easter", [
        RD,
        ("Persian", [("Astro.", lambda rd: d(p.persian_from_fixed(rd))),
                     ("Arith.", lambda rd: d(p.arithmetic_persian_from_fixed(rd)))]),
        ("Baha'i", [("Western", lambda rd: d(p.bahai_from_fixed(rd))),
                    ("Astro.", lambda rd: d(p.astro_bahai_from_fixed(rd)))]),
        ("French Revolutionary",
         [("Original", lambda rd: d(p.french_from_fixed(rd))),
          ("Modified", lambda rd: d(p.arithmetic_french_from_fixed(rd)))]),
        ("Easter (same year)",
         [("Julian", lambda rd: easter_g(rd, p.orthodox_easter)),
          ("Gregorian", lambda rd: easter_g(rd, p.easter)),
          ("Astronomical", lambda rd: easter_g(rd, p.astronomical_easter))]),
    ]),
    ("p.758", "Mayan / Aztec / Balinese / Babylonian / Samaritan", [
        RD,
        ("Mayan", [("Long Count", lambda rd: d(p.mayan_long_count_from_fixed(rd))),
                   ("Haab", lambda rd: d(p.mayan_haab_from_fixed(rd))),
                   ("Tzolkin", lambda rd: d(p.mayan_tzolkin_from_fixed(rd)))]),
        ("Aztec", [("Xihuitl", lambda rd: d(p.aztec_xihuitl_from_fixed(rd))),
                   ("Tonalpohualli",
                    lambda rd: d(p.aztec_tonalpohualli_from_fixed(rd)))]),
        ("Balinese Pawukon", [("", lambda rd: d(p.bali_pawukon_from_fixed(rd)))]),
        ("Babylonian", [("", lambda rd: d(p.babylonian_from_fixed(rd)))]),
        ("Samaritan", [("", lambda rd: d(p.samaritan_from_fixed(rd)))]),
    ]),
    ("p.759", "Chinese / Hindu Solar / Hindu Lunisolar / Tibetan", [
        RD,
        ("Chinese", [("Date", lambda rd: d(p.chinese_from_fixed(rd))),
                     ("Name", lambda rd: d(p.chinese_day_name(rd))),
                     ("Next Zhongqi",
                      lambda rd: fnum(p.major_solar_term_on_or_after(rd)))]),
        ("Hindu Solar",
         [("Old", lambda rd: d(p.old_hindu_solar_from_fixed(rd))),
          ("Modern", lambda rd: d(p.hindu_solar_from_fixed(rd))),
          ("Astronomical", lambda rd: d(p.astro_hindu_solar_from_fixed(rd)))]),
        ("Hindu Lunisolar",
         [("Old", lambda rd: d(p.old_hindu_lunar_from_fixed(rd))),
          ("Modern", lambda rd: d(p.hindu_lunar_from_fixed(rd))),
          ("Astronomical", lambda rd: d(p.astro_hindu_lunar_from_fixed(rd)))]),
        ("Tibetan", [("", lambda rd: d(p.tibetan_from_fixed(rd)))]),
    ]),
    ("p.760", "Solar astronomy and times", [
        RD,
        ("Ephemeris Correction",
         [("", lambda rd: fnum(p.ephemeris_correction(rd + 0.5)))]),
        ("Equation of Time", [("", lambda rd: fnum(p.equation_of_time(rd + 0.5)))]),
        ("Solar Longitude 12:00:00 U.T.",
         [("", lambda rd: fnum(p.solar_longitude(rd + 0.5)))]),
        ("Next Solstice/Equinox", [("", lambda rd: fnum(min(
            p.solar_longitude_after(p.SPRING, rd),
            p.solar_longitude_after(p.SUMMER, rd),
            p.solar_longitude_after(p.AUTUMN, rd),
            p.solar_longitude_after(p.WINTER, rd))))]),
        ("Dawn in Paris",
         [("", lambda rd: ftime(p.dawn(rd, p.PARIS, PARIS_DAWN_ALPHA)))]),
        ("Midday in Tehran", [("", lambda rd: ftime(p.midday(rd, p.TEHRAN)))]),
        ("Sunset in Jerusalem", [("", lambda rd: ftime(p.sunset(rd, p.JERUSALEM)))]),
    ]),
    ("p.761", "Lunar astronomy", [
        RD,
        ("Lunar Position at 00:00:00 U.T.",
         [("Longitude", lambda rd: fnum(p.lunar_longitude(rd))),
          ("Latitude", lambda rd: fnum(p.lunar_latitude(rd))),
          ("Altitude", lambda rd: fnum(p.lunar_altitude(rd, p.MECCA)))]),
        ("Next New Moon", [("", lambda rd: fnum(p.new_moon_at_or_after(rd)))]),
        ("In Mecca", [("Moonrise", lambda rd: ftime(p.moonrise(rd, p.MECCA))),
                      ("Moonset", lambda rd: ftime(p.moonset(rd, p.MECCA)))]),
    ]),
    # ---- supplement: columns the 4th-edition Appendix C does NOT include ----
    ("supp.", "SUPPLEMENT (not in 4th-ed Appendix C): Western basics", [
        RD,
        ("Weekday", [("", lambda rd: WEEKDAYS[p.day_of_week_from_fixed(rd)])]),
        ("J.D.", [("", lambda rd: "%.1f" % float(p.jd_from_fixed(rd)))]),
        ("M.J.D.", [("", lambda rd: str(p.mjd_from_fixed(rd)))]),
        ("Gregorian", [("", lambda rd: d(p.gregorian_from_fixed(rd)))]),
        ("Julian", [("", lambda rd: d(p.julian_from_fixed(rd)))]),
        ("Roman", [("", roman)]),
        ("Egyptian", [("", lambda rd: d(p.egyptian_from_fixed(rd)))]),
        ("Armenian", [("", lambda rd: d(p.armenian_from_fixed(rd)))]),
    ]),
]


def tex(s):
    return s.replace("&", "\\&").replace("'", "'")


def render_latex(dates):
    out = [r"% Generated by tools/gen_appendix_c.py -- do not edit.",
           r"\documentclass[8pt]{extarticle}",
           r"\usepackage[a3paper,landscape,margin=1cm]{geometry}",
           r"\usepackage{longtable,booktabs}",
           r"\setlength{\tabcolsep}{3pt}\pagestyle{empty}",
           r"\begin{document}",
           r"\begin{center}{\large Calendrical Calculations --- Appendix C "
           r"(reconstruction from pycalcal, Ultimate Edition)}\\[2pt]",
           r"{\footnotesize Panels mirror the printed 4th-ed.\ Appendix C "
           r"pp.\,756--761. 33 sample dates; raw function output, negative = "
           r"B.C.E., leap flags t/f. Times = standard clock (HH:MM:SS), "
           r"`---' = none that day. Lunar altitude observer = Mecca (prose does "
           r"not fix it).}\end{center}"]
    for ref, title, groups in PANELS:
        ncol = sum(len(subs) for _, subs in groups)
        out.append(r"\section*{%s \hfill {\normalsize\itshape %s}}"
                   % (tex(title), ref))
        out.append(r"\footnotesize")
        out.append(r"\begin{longtable}{r " + "l " * (ncol - 1) + "}")
        out.append(r"\toprule")
        # group header row
        grow = " & ".join(r"\multicolumn{%d}{c}{%s}" % (len(subs), tex(lbl))
                          for lbl, subs in groups)
        out.append(grow + r" \\")
        # sub header row (blank where a group has no sub-labels)
        if any(sub for _, subs in groups for sub, _ in subs):
            srow = " & ".join(tex(sub) for _, subs in groups for sub, _ in subs)
            out.append(srow + r" \\")
        out.append(r"\midrule\endhead")
        for rd in dates:
            cells = [tex(fn(rd)) for _, subs in groups for _, fn in subs]
            out.append(" & ".join(cells) + r" \\")
        out.append(r"\bottomrule\end{longtable}\newpage")
    out.append(r"\end{document}")
    return "\n".join(out) + "\n"


def main():
    dates = sample_dates()
    out_dir = os.path.join(ROOT, "recon")
    os.makedirs(out_dir, exist_ok=True)

    headers = ["R.D."]
    for ref, _, groups in PANELS:
        for lbl, subs in groups:
            for sub, _ in subs:
                if lbl == "R.D.":
                    continue
                name = lbl if not sub else ("%s %s" % (lbl, sub))
                headers.append("[%s] %s" % (ref, name))
    with open(os.path.join(out_dir, "appendixC_full.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(headers)
        for rd in dates:
            row = [rd]
            for _, _, groups in PANELS:
                for lbl, subs in groups:
                    if lbl == "R.D.":
                        continue
                    for _, fn in subs:
                        row.append(fn(rd))
            w.writerow(row)

    with open(os.path.join(out_dir, "appendixC_full.tex"), "w") as fh:
        fh.write(render_latex(dates))
    print("Wrote recon/appendixC_full.tex and recon/appendixC_full.csv"
          " (%d dates, %d panels incl. supplement)" % (len(dates), len(PANELS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
