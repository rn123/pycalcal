#!/usr/bin/env python3
"""Generate the Appendix C sample-data tables from pycalcal, matching the printed
Ultimate Edition (4th ed.) Appendix C exactly: column names, groupings, two-row
grouped headers, full-height vertical rules between columns, and double top/bottom
rules. Panels mirror book pp. 756-761 (plus a clearly-labelled supplement of the
Western basics, which the 4th-ed Appendix C omits).

Headers were transcribed from the printed pages by VLM at 400 dpi:
  756 Akan,Coptic,Ethiopic,ISO,Icelandic, Islamic{Arithmetic,Observational,Umm al-Qura},
      Hebrew{Standard,Observational}
  757 Persian{Astronomical,Arithmetic}, Baha'i{Western,Astronomical},
      French Revolutionary{Original,Modified}, Easter (same year){Julian,Gregorian,Astronomical}
  758 Mayan{Long Count,Haab,Tzolkin}, Aztec{Xihuitl,Tonalp.}, Balinese Pawukon, Babylonian, Samaritan
  759 Chinese{Date,Name,Next Zhongqi}, Hindu Solar{Old,Modern,Astronomical},
      Hindu Lunisolar{Old,Modern,Astronomical}, Tibetan
  760 Ephemeris Correction, Equation of Time, Solar Longitude at 12:00:00 U.T. (Degrees),
      Next Solstice/Equinox (R.D.), Dawn in Paris (Standard Time),
      Midday in Tehran (Standard Time), Sunset in Jerusalem (Standard Time)
  761 Lunar Position at 00:00:00 U.T.{Longitude,Latitude,Altitude (Degrees)},
      Next New Moon (R.D.), In Mecca{Moonrise,Moonset (Standard Time)}

Standard-time cells are shown as the book does: "<fraction> = HH:MM:SS"
('---' = none that day). Values come from the Ultimate-Edition pycalcal.

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
PARIS_DAWN_ALPHA = p.angle(18, 0, 0)


def sample_dates():
    with open(os.path.join(ROOT, "dates1.csv")) as fh:
        return [int(r[0]) for r in csv.reader(fh) if r]


# ---- cell renderers --------------------------------------------------------

def dd(v):
    return " ".join("t" if x is True else ("f" if x is False else str(x))
                    for x in v)


def fnum(x):
    return "%.6f" % float(x)


def ftime(moment):
    if moment == p.BOGUS:
        return "---"
    frac = float(p.mod(moment, 1))
    h, m, s = p.clock_from_moment(moment)
    return "%.6f = %02d:%02d:%02d" % (frac, int(h), int(m), int(round(float(s))))


def easter_g(rd, fn):
    return dd(p.gregorian_from_fixed(fn(p.gregorian_year_from_fixed(rd))))


def olympiad_cell(rd):
    """Olympiad [cycle year] of the Julian year of fixed date rd (raw)."""
    return dd(p.olympiad_from_julian_year(p.standard_year(p.julian_from_fixed(rd))))


# ---- panel model -----------------------------------------------------------
# panel = (page-ref, title, [group, ...])
# group = (group-label-or-"", [(header-lines-list, render-fn), ...])
RD = ("", [(["R.D."], str)])


def one(*args):
    """A single (ungrouped) column: one(header_line, [more_lines...], fn).
    The last argument is the render function; the rest are stacked header lines."""
    lines, fn = list(args[:-1]), args[-1]
    return ("", [(lines, fn)])


def grp(label, *cols):
    """A grouped column block; each col is (header-lines-list, fn)."""
    return (label, list(cols))


PANELS = [
    ("p.755", "Day count / Gregorian / Julian / Egyptian / Armenian", [
        RD,
        one("Weekday", lambda rd: WEEKDAYS[p.day_of_week_from_fixed(rd)]),
        one("Julian", "Day", lambda rd: "%.1f" % float(p.jd_from_fixed(rd))),
        one("Modified", "Julian Day", lambda rd: str(p.mjd_from_fixed(rd))),
        one("Unix", lambda rd: str(int(p.unix_from_moment(rd)))),
        one("Gregorian", lambda rd: dd(p.gregorian_from_fixed(rd))),
        grp("Julian",
            (["Date"], lambda rd: dd(p.julian_from_fixed(rd))),
            (["Roman name"], lambda rd: dd(p.roman_from_fixed(rd))),
            (["Olympiad"], olympiad_cell)),
        one("Egyptian", lambda rd: dd(p.egyptian_from_fixed(rd))),
        one("Armenian", lambda rd: dd(p.armenian_from_fixed(rd))),
    ]),
    ("p.756", "Akan / Coptic / Ethiopic / ISO / Icelandic / Islamic / Hebrew", [
        RD,
        one("Akan", lambda rd: dd(p.akan_name_from_fixed(rd))),
        one("Coptic", lambda rd: dd(p.coptic_from_fixed(rd))),
        one("Ethiopic", lambda rd: dd(p.ethiopic_from_fixed(rd))),
        one("ISO", lambda rd: dd(p.iso_from_fixed(rd))),
        one("Icelandic", lambda rd: dd(p.icelandic_from_fixed(rd))),
        grp("Islamic",
            (["Arithmetic"], lambda rd: dd(p.islamic_from_fixed(rd))),
            (["Observational"], lambda rd: dd(p.observational_islamic_from_fixed(rd))),
            (["Umm al-Qura"], lambda rd: dd(p.saudi_islamic_from_fixed(rd)))),
        grp("Hebrew",
            (["Standard"], lambda rd: dd(p.hebrew_from_fixed(rd))),
            (["Observational"], lambda rd: dd(p.observational_hebrew_from_fixed(rd)))),
    ]),
    ("p.757", "Persian / Baha'i / French Revolutionary / Easter", [
        RD,
        grp("Persian",
            (["Astronomical"], lambda rd: dd(p.persian_from_fixed(rd))),
            (["Arithmetic"], lambda rd: dd(p.arithmetic_persian_from_fixed(rd)))),
        grp("Bah\\'a'\\'{\\i}",
            (["Western"], lambda rd: dd(p.bahai_from_fixed(rd))),
            (["Astronomical"], lambda rd: dd(p.astro_bahai_from_fixed(rd)))),
        grp("French Revolutionary",
            (["Original"], lambda rd: dd(p.french_from_fixed(rd))),
            (["Modified"], lambda rd: dd(p.arithmetic_french_from_fixed(rd)))),
        grp("Easter (same year)",
            (["Julian"], lambda rd: easter_g(rd, p.orthodox_easter)),
            (["Gregorian"], lambda rd: easter_g(rd, p.easter)),
            (["Astronomical"], lambda rd: easter_g(rd, p.astronomical_easter))),
    ]),
    ("p.758", "Mayan / Aztec / Balinese / Babylonian / Samaritan", [
        RD,
        grp("Mayan",
            (["Long Count"], lambda rd: dd(p.mayan_long_count_from_fixed(rd))),
            (["Haab"], lambda rd: dd(p.mayan_haab_from_fixed(rd))),
            (["Tzolkin"], lambda rd: dd(p.mayan_tzolkin_from_fixed(rd)))),
        grp("Aztec",
            (["Xihuitl"], lambda rd: dd(p.aztec_xihuitl_from_fixed(rd))),
            (["Tonalp."], lambda rd: dd(p.aztec_tonalpohualli_from_fixed(rd)))),
        one("Balinese Pawukon", lambda rd: dd(p.bali_pawukon_from_fixed(rd))),
        one("Babylonian", lambda rd: dd(p.babylonian_from_fixed(rd))),
        one("Samaritan", lambda rd: dd(p.samaritan_from_fixed(rd))),
    ]),
    ("p.759", "Chinese / Hindu Solar / Hindu Lunisolar / Tibetan", [
        RD,
        grp("Chinese",
            (["Date"], lambda rd: dd(p.chinese_from_fixed(rd))),
            (["Name"], lambda rd: dd(p.chinese_day_name(rd))),
            (["Next Zhongqi"], lambda rd: fnum(p.major_solar_term_on_or_after(rd)))),
        grp("Hindu Solar",
            (["Old"], lambda rd: dd(p.old_hindu_solar_from_fixed(rd))),
            (["Modern"], lambda rd: dd(p.hindu_solar_from_fixed(rd))),
            (["Astronomical"], lambda rd: dd(p.astro_hindu_solar_from_fixed(rd)))),
        grp("Hindu Lunisolar",
            (["Old"], lambda rd: dd(p.old_hindu_lunar_from_fixed(rd))),
            (["Modern"], lambda rd: dd(p.hindu_lunar_from_fixed(rd))),
            (["Astronomical"], lambda rd: dd(p.astro_hindu_lunar_from_fixed(rd)))),
        one("Tibetan", lambda rd: dd(p.tibetan_from_fixed(rd))),
    ]),
    ("p.760", "Solar astronomy and times", [
        RD,
        one("Ephemeris", "Correction",
            lambda rd: fnum(p.ephemeris_correction(rd + 0.5))),
        one("Equation", "of Time", lambda rd: fnum(p.equation_of_time(rd + 0.5))),
        one("Solar Longitude", "at 12:00:00 U.T.", "(Degrees)",
            lambda rd: fnum(p.solar_longitude(rd + 0.5))),
        one("Next", "Solstice/Equinox", "(R.D.)", lambda rd: fnum(min(
            p.solar_longitude_after(p.SPRING, rd),
            p.solar_longitude_after(p.SUMMER, rd),
            p.solar_longitude_after(p.AUTUMN, rd),
            p.solar_longitude_after(p.WINTER, rd)))),
        one("Dawn in Paris", "(Standard Time)",
            lambda rd: ftime(p.dawn(rd, p.PARIS, PARIS_DAWN_ALPHA))),
        one("Midday in Tehran", "(Standard Time)",
            lambda rd: ftime(p.midday(rd, p.TEHRAN))),
        one("Sunset in Jerusalem", "(Standard Time)",
            lambda rd: ftime(p.sunset(rd, p.JERUSALEM))),
    ]),
    ("p.761", "Lunar astronomy", [
        RD,
        grp("Lunar Position at 00:00:00 U.T.",
            (["Longitude", "(Degrees)"], lambda rd: fnum(p.lunar_longitude(rd))),
            (["Latitude", "(Degrees)"], lambda rd: fnum(p.lunar_latitude(rd))),
            (["Altitude", "(Degrees)"], lambda rd: fnum(p.lunar_altitude(rd, p.MECCA)))),
        one("Next New Moon", "(R.D.)", lambda rd: fnum(p.new_moon_at_or_after(rd))),
        grp("In Mecca (21.42\\textdegree\\ N, 39.82\\textdegree\\ E, 298m)",
            (["Moonrise", "(Standard Time)"], lambda rd: ftime(p.moonrise(rd, p.MECCA))),
            (["Moonset", "(Standard Time)"], lambda rd: ftime(p.moonset(rd, p.MECCA)))),
    ]),
]


def tex(s):
    return s.replace("&", "\\&").replace("#", "\\#")


def stack(lines):
    if len(lines) == 1:
        return tex(lines[0])
    return r"\shortstack{" + r" \\ ".join(tex(x) for x in lines) + "}"


def render_latex(dates):
    out = [r"% Generated by tools/gen_appendix_c.py -- do not edit.",
           r"\documentclass[8pt]{extarticle}",
           r"\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}",
           r"\usepackage{textcomp}",
           r"\usepackage[a3paper,landscape,margin=1cm]{geometry}",
           r"\setlength{\tabcolsep}{3pt}\pagestyle{empty}",
           r"\begin{document}",
           r"\begin{center}{\large Calendrical Calculations --- Appendix C "
           r"(reconstruction from pycalcal, Ultimate Edition)}\\[2pt]",
           r"{\footnotesize Panels and headers mirror the printed 4th-ed.\ "
           r"Appendix C pp.\,755--761. 33 sample dates; raw function output, "
           r"negative = B.C.E., leap flags t/f. Standard-time cells: "
           r"`fraction = HH:MM:SS', `---' = none that day.}\end{center}"]
    for ref, title, groups in PANELS:
        cols = [(hl, fn) for _, gcols in groups for (hl, fn) in gcols]
        ncol = len(cols)
        colspec = "r" + "|l" * (ncol - 1)
        out.append(r"\section*{%s \hfill {\normalsize\itshape %s}}"
                   % (tex(title.replace("Baha'i", "Bahá'í")), ref))
        out.append(r"\footnotesize")
        out.append(r"\noindent\begin{tabular}{" + colspec + "}")
        out.append(r"\hline\hline")
        # upper (group-label) row + cline under multi-column groups
        upper, clines, idx = [], [], 1
        for gi, (label, gcols) in enumerate(groups):
            n = len(gcols)
            spec = "c" if gi == 0 else "|c"
            if label:
                upper.append(r"\multicolumn{%d}{%s}{%s}" % (n, spec, label))
                clines.append(r"\cline{%d-%d}" % (idx, idx + n - 1))
            else:
                upper.append(r"\multicolumn{%d}{%s}{}" % (n, spec))
            idx += n
        out.append(" & ".join(upper) + r" \\")
        if clines:
            out.append("".join(clines))
        # lower (column-header) row
        out.append(" & ".join(stack(hl) for hl, _ in cols) + r" \\")
        out.append(r"\hline")
        for rd in dates:
            out.append(" & ".join(tex(fn(rd)) for _, fn in cols) + r" \\")
        out.append(r"\hline\hline")
        out.append(r"\end{tabular}\newpage")
    out.append(r"\end{document}")
    return "\n".join(out) + "\n"


def main():
    dates = sample_dates()
    out_dir = os.path.join(ROOT, "recon")
    os.makedirs(out_dir, exist_ok=True)

    headers = ["R.D."]
    for ref, _, groups in PANELS:
        for label, gcols in groups:
            for hl, _ in gcols:
                if hl == ["R.D."]:
                    continue
                nm = " ".join(hl)
                headers.append("[%s] %s%s" % (ref, (label + " ") if label else "", nm))
    with open(os.path.join(out_dir, "appendixC_full.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(headers)
        for rd in dates:
            row = [rd]
            for _, _, groups in PANELS:
                for label, gcols in groups:
                    for hl, fn in gcols:
                        if hl == ["R.D."]:
                            continue
                        row.append(fn(rd))
            w.writerow(row)

    with open(os.path.join(out_dir, "appendixC_full.tex"), "w") as fh:
        fh.write(render_latex(dates))
    print("Wrote recon/appendixC_full.tex and recon/appendixC_full.csv"
          " (%d dates, %d panels mirroring book pp.755-761)"
          % (len(dates), len(PANELS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
