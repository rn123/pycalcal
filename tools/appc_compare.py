#!/usr/bin/env python3
"""Complete Appendix C comparison: every column, all 33 sample dates, pycalcal vs
the Ultimate Lisp (the book's own Appendix-C-generating code).

Runs tools/appc_full_oracle.lisp, then computes the same quantities in pycalcal
and diffs cell-by-cell. Integers/date-lists compared exactly; floats/times by
tolerance. This is the rigorous "compare all entries with our computed data".

Run from repo root: .venv/bin/python tools/appc_compare.py
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pycalcal as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 1e-6
PARIS_DAWN = p.angle(18, 0, 0)


def gy(rd):
    return p.gregorian_year_from_fixed(rd)


# colkey -> (pycalcal value fn, kind)   kind: 'i'=int/list exact, 'f'=float tol
PY = {
    "WEEKDAY": (lambda rd: p.day_of_week_from_fixed(rd), 'i'),
    "JD": (lambda rd: p.jd_from_fixed(rd), 'f'),
    "MJD": (lambda rd: p.mjd_from_fixed(rd), 'i'),
    "UNIX": (lambda rd: int(p.unix_from_moment(rd)), 'i'),
    "GREGORIAN": (lambda rd: p.gregorian_from_fixed(rd), 'i'),
    "JULIAN": (lambda rd: p.julian_from_fixed(rd), 'i'),
    "ROMAN": (lambda rd: p.roman_from_fixed(rd), 'i'),
    "OLYMPIAD": (lambda rd: p.olympiad_from_julian_year(
        p.standard_year(p.julian_from_fixed(rd))), 'i'),
    "EGYPTIAN": (lambda rd: p.egyptian_from_fixed(rd), 'i'),
    "ARMENIAN": (lambda rd: p.armenian_from_fixed(rd), 'i'),
    "AKAN": (lambda rd: p.akan_name_from_fixed(rd), 'i'),
    "COPTIC": (lambda rd: p.coptic_from_fixed(rd), 'i'),
    "ETHIOPIC": (lambda rd: p.ethiopic_from_fixed(rd), 'i'),
    "ISO": (lambda rd: p.iso_from_fixed(rd), 'i'),
    "ICELANDIC": (lambda rd: p.icelandic_from_fixed(rd), 'i'),
    "ISLAMIC": (lambda rd: p.islamic_from_fixed(rd), 'i'),
    "OBS-ISLAMIC": (lambda rd: p.observational_islamic_from_fixed(rd), 'i'),
    "UMM-AL-QURA": (lambda rd: p.saudi_islamic_from_fixed(rd), 'i'),
    "HEBREW": (lambda rd: p.hebrew_from_fixed(rd), 'i'),
    "OBS-HEBREW": (lambda rd: p.observational_hebrew_from_fixed(rd), 'i'),
    "PERSIAN": (lambda rd: p.persian_from_fixed(rd), 'i'),
    "ARITH-PERSIAN": (lambda rd: p.arithmetic_persian_from_fixed(rd), 'i'),
    "BAHAI": (lambda rd: p.bahai_from_fixed(rd), 'i'),
    "ASTRO-BAHAI": (lambda rd: p.astro_bahai_from_fixed(rd), 'i'),
    "FRENCH": (lambda rd: p.french_from_fixed(rd), 'i'),
    "ARITH-FRENCH": (lambda rd: p.arithmetic_french_from_fixed(rd), 'i'),
    "EASTER-JUL": (lambda rd: p.gregorian_from_fixed(p.orthodox_easter(gy(rd))), 'i'),
    "EASTER-GREG": (lambda rd: p.gregorian_from_fixed(p.easter(gy(rd))), 'i'),
    "EASTER-ASTRO": (lambda rd: p.gregorian_from_fixed(p.astronomical_easter(gy(rd))), 'i'),
    "MAYAN-LC": (lambda rd: p.mayan_long_count_from_fixed(rd), 'i'),
    "MAYAN-HAAB": (lambda rd: p.mayan_haab_from_fixed(rd), 'i'),
    "MAYAN-TZOLKIN": (lambda rd: p.mayan_tzolkin_from_fixed(rd), 'i'),
    "AZTEC-XIHUITL": (lambda rd: p.aztec_xihuitl_from_fixed(rd), 'i'),
    "AZTEC-TONAL": (lambda rd: p.aztec_tonalpohualli_from_fixed(rd), 'i'),
    "BALINESE": (lambda rd: p.bali_pawukon_from_fixed(rd), 'i'),
    "BABYLONIAN": (lambda rd: p.babylonian_from_fixed(rd), 'i'),
    "SAMARITAN": (lambda rd: p.samaritan_from_fixed(rd), 'i'),
    "CHINESE": (lambda rd: p.chinese_from_fixed(rd), 'i'),
    "CHINESE-NAME": (lambda rd: p.chinese_day_name(rd), 'i'),
    "ZHONGQI": (lambda rd: p.major_solar_term_on_or_after(rd), 'f'),
    "OLD-HINDU-SOLAR": (lambda rd: p.old_hindu_solar_from_fixed(rd), 'i'),
    "HINDU-SOLAR": (lambda rd: p.hindu_solar_from_fixed(rd), 'i'),
    "ASTRO-HINDU-SOLAR": (lambda rd: p.astro_hindu_solar_from_fixed(rd), 'i'),
    "OLD-HINDU-LUNAR": (lambda rd: p.old_hindu_lunar_from_fixed(rd), 'i'),
    "HINDU-LUNAR": (lambda rd: p.hindu_lunar_from_fixed(rd), 'i'),
    "ASTRO-HINDU-LUNAR": (lambda rd: p.astro_hindu_lunar_from_fixed(rd), 'i'),
    "TIBETAN": (lambda rd: p.tibetan_from_fixed(rd), 'i'),
    "EPHEMERIS": (lambda rd: p.ephemeris_correction(rd + 0.5), 'f'),
    "EQ-TIME": (lambda rd: p.equation_of_time(rd + 0.5), 'f'),
    "SOLAR-LONG": (lambda rd: p.solar_longitude(rd + 0.5), 'f'),
    "NEXT-SEASON": (lambda rd: min(p.solar_longitude_after(p.SPRING, rd),
                                   p.solar_longitude_after(p.SUMMER, rd),
                                   p.solar_longitude_after(p.AUTUMN, rd),
                                   p.solar_longitude_after(p.WINTER, rd)), 'f'),
    "DAWN-PARIS": (lambda rd: p.dawn(rd, p.PARIS, PARIS_DAWN), 'f'),
    "MIDDAY-TEHRAN": (lambda rd: p.midday(rd, p.TEHRAN), 'f'),
    "SUNSET-JERU": (lambda rd: p.sunset(rd, p.JERUSALEM), 'f'),
    "LUNAR-LONG": (lambda rd: p.lunar_longitude(rd), 'f'),
    "LUNAR-LAT": (lambda rd: p.lunar_latitude(rd), 'f'),
    "LUNAR-ALT": (lambda rd: p.lunar_altitude(rd, p.MECCA), 'f'),
    "NEW-MOON": (lambda rd: p.new_moon_at_or_after(rd), 'f'),
    "MOONRISE-MECCA": (lambda rd: p.moonrise(rd, p.MECCA), 'f'),
    "MOONSET-MECCA": (lambda rd: p.moonset(rd, p.MECCA), 'f'),
}


def parse(tok):
    if tok.upper() == "NIL":
        return False
    if tok.upper() == "T":
        return True
    if tok.lower() == '"bogus"' or tok.lower() == "bogus":
        return p.BOGUS
    t = tok.replace('d', 'e').replace('D', 'e').replace('L', 'e').strip('"')
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        return float(t)
    except ValueError:
        return tok


def parse_sexpr(s):
    s = s.strip()
    if s.startswith("("):
        return [parse(x) for x in s[1:-1].split()]
    return parse(s)


def norm(v):
    if isinstance(v, list):
        return [norm(x) for x in v]
    return v


def main():
    out = subprocess.run(["sbcl", "--non-interactive", "--load",
                          "tools/appc_full_oracle.lisp"],
                         cwd=ROOT, capture_output=True, text=True, timeout=1200).stdout
    by_col = {}
    total = match = 0
    mismatches = []
    for line in out.splitlines():
        parts = line.split(" ", 2)
        if len(parts) != 3 or not parts[0].lstrip("-").isdigit():
            continue
        rd, key, raw = int(parts[0]), parts[1], parts[2]
        if key not in PY:
            continue
        fn, kind = PY[key]
        try:
            pv = fn(rd)
        except Exception as ex:
            mismatches.append((key, rd, "PYERR:%s" % ex, raw)); continue
        lv = parse_sexpr(raw)
        total += 1
        st = by_col.setdefault(key, [0, 0])
        st[0] += 1
        if kind == 'i':
            ok = norm(pv) == norm(lv)
        else:
            pvf = float(pv) if pv != p.BOGUS else None
            lvf = float(lv) if lv != p.BOGUS else None
            ok = (pvf is None and lvf is None) or (
                pvf is not None and lvf is not None and abs(pvf - lvf) <= TOL)
        if ok:
            match += 1; st[1] += 1
        else:
            mismatches.append((key, rd, pv, lv))

    print("==== Appendix C: pycalcal vs Ultimate Lisp, 33 dates x %d columns ====" % len(by_col))
    print("cells compared: %d   exact/within-tol: %d   mismatches: %d"
          % (total, match, total - match))
    cols_ok = [k for k, s in by_col.items() if s[0] == s[1]]
    print("\ncolumns fully matching (%d/%d)." % (len(cols_ok), len(by_col)))
    if mismatches:
        print("\nMISMATCHES:")
        for key, rd, pv, lv in mismatches:
            print("  %-18s rd=%-8d py=%r  lisp=%r" % (key, rd, pv, lv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
