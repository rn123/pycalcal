# CALENDRICA: Ultimate Edition vs. 3.0 — Function Diff

A function- and constant-level diff of **Appendix D (Lisp Implementation)** in
*Calendrical Calculations: The Ultimate Edition* (Reingold & Dershowitz) against
[`calendrica-3.0.cl`](../calendrica-3.0.cl) — the 3.0 source that this repository's
[`pycalcal`](../pycalcal/pycalcal.py) port implements.

This is a **name-level** comparison. A literal line diff is not meaningful: the Ultimate
Edition source was extracted from the book PDF (carrying page markers and typeset line
wrapping), whereas `calendrica-3.0.cl` is clean source. Function *bodies* were not compared.

**Net change:** 458 → 554 functions (+96); 102 → 117 constants (+15).

> Source of the Ultimate Edition text: Appendix D, pp. 778–948, extracted to
> `ultimate_extract/appD_lisp_impl.txt` (554 `defun`s, 117 `defconstant`s).

---

## 1. New calendars (the headline change)

These calendars exist in the Ultimate Edition but **not** in 3.0 / pycalcal:

| Calendar | New functions |
|---|---|
| **Babylonian** | `babylonian-from-fixed`, `fixed-from-babylonian`, `babylonian-date`, `-day`, `-month`, `-year`, `-leap`, `babylonian-leap-year?`, `babylonian-new-month-on-or-before`, `babylonian-criterion` |
| **Icelandic** | `icelandic-from-fixed`, `fixed-from-icelandic`, `icelandic-date`, `-month`, `-year`, `-season`, `-summer`, `-winter`, `-week`, `-weekday`, `icelandic-leap-year?` |
| **Samaritan** | `samaritan-from-fixed`, `fixed-from-samaritan`, `samaritan-new-moon-after`, `-new-moon-at-or-before`, `-new-year-on-or-before`, `-noon` |
| **Akan** (day-names) | `akan-name`, `akan-name-from-fixed`, `-name-difference`, `akan-day-name`, `-day-name-on-or-before`, `akan-prefix`, `akan-stem` |
| **Saudi / Umm al-Qura Islamic** | `saudi-islamic-from-fixed`, `fixed-from-saudi-islamic`, `saudi-new-month-on-or-before`, `saudi-criterion` |

---

## 2. Bahá'í: "future" → astronomical (renamed subsystem)

The 3.0 "future Bahá'í calendar" was renamed the **astronomical** Bahá'í calendar:

| 3.0 | Ultimate |
|---|---|
| `fixed-from-future-bahai` | `fixed-from-astro-bahai` |
| `future-bahai-from-fixed` | `astro-bahai-from-fixed` |
| `future-bahai-new-year-on-or-before` | `astro-bahai-new-year-on-or-before` |

Plus new `bahai-sunset`; constant `haifa` → `bahai-location`. Per Appendix C's own note, this
rename is the source of the **largest sample-value changes** between editions.

---

## 3. New astronomy / lunar-visibility machinery

- **Moon rise/set:** `moonrise`, `moonset`, `moonlag`, `lunar-semi-diameter`, `lunar-node`,
  `sidereal-lunar-longitude`, `observed-lunar-altitude`, `solar-altitude`, `refraction`
- **Crescent-visibility criteria (new):** `arc-of-light`, `arc-of-vision`, `yallop-criterion`,
  `shaukat-criterion`, `bruin-best-view`, `simple-best-view` (plus the per-calendar
  `*-criterion` functions in §1)
- **Apparent vs. universal time:** `apparent-from-universal`, `universal-from-apparent`
- **Unix / Julian-day time:** `moment-from-unix`, `unix-from-moment`, `moment-from-jd`,
  `jd-from-moment`, `fixed-from-mjd`, `mjd-from-fixed`

---

## 4. Roman calendar additions (Chapter 3 expanded)

`olympiad`, `olympiad-from-julian-year`, `julian-year-from-olympiad`, `olympiad-cycle`,
`olympiad-year`, `auc-year-from-julian`, `julian-year-from-auc`, Italian hours
(`italian-from-local`, `local-from-italian`), and Roman seasons
(`julian-season-in-gregorian`, `samuel-season-in-gregorian`, `adda-season-in-gregorian`,
`season-in-gregorian`, `cycle-in-gregorian`).

---

## 5. New holidays

`hanukkah`, `nowruz`, `mawlid` (was `mawlid-an-nabi`), `birth-of-the-bab`, `unlucky-fridays`,
`alt-birkath-ha-hama`, `hebrew-in-gregorian`.

---

## 6. Genuine renames (not new functionality)

| 3.0 | Ultimate |
|---|---|
| `sine-degrees` / `cosine-degrees` / `tangent-degrees` | `sin-degrees` / `cos-degrees` / `tan-degrees` |
| `chinese-name-of-{day,month,year}` | `chinese-{day,month,year}-name` |
| `observational-hebrew-new-year` | `observational-hebrew-first-of-nisan` |
| `aztec-tonalpohualli-on-or-before` | `aztec-xihuitl-tonalpohualli-on-or-before` |
| `hindu-sundial-time` | `hindu-standard-from-sundial` |
| `mawlid-an-nabi` | `mawlid` |

---

## 7. Constants

- **Locations reworked:** removed `haifa`, `jaffa`; renamed `hindu-locale` → `hindu-location`,
  `islamic-locale` → `islamic-location`; added `acre`, `babylon`, `padua`, `bahai-location`,
  `hebrew-location`, `samaritan-location`.
- **New epochs:** `babylonian-epoch`, `icelandic-epoch`, `samaritan-epoch`, `unix-epoch`,
  `akan-day-name-epoch`, `olympiad-start`.
- **Crescent-visibility categories:** `blind`, `bright`, `double-bright`, `widow` (Yallop classes).

---

## Caveats

- Ignore `function-name` and `constant-name` from the raw extraction — they come from the
  "Lisp Preliminaries" syntax-example template on p.778, not real definitions.
- `mayan-calendar-round-on-or-before` was the one 3.0 name that could not be reconfirmed in the
  (line-wrapped) Ultimate text; it is most likely present but unverified here.
- The following 3.0 names appeared as "removed" only because PDF line-wrapping truncated them in
  extraction — they **are** present in the Ultimate Edition unchanged:
  `approx-moment-of-depression`, `moment-of-depression`, `chinese-solar-longitude-on-or-after`,
  `hindu-true-position`, `mayan-long-count-date`.

---

## Implications for `pycalcal`

`pycalcal` ports the 3.0 set, so the actionable gaps are:

1. **Five new calendars** (§1): Babylonian, Icelandic, Samaritan, Akan, Saudi/Umm al-Qura Islamic.
2. **Rewritten Bahá'í** (§2): the astronomical calendar replacing the "future" one.
3. New astronomy/visibility routines (§3) and Roman additions (§4) if full parity is desired.
