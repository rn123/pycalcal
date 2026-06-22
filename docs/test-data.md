# Test Data Provenance

This note documents where the repository's calendar test data comes from and how it is used.

## What it is

The test data is **`dates1.tex` … `dates5.tex`** (33 rows each) plus **`dates5.errata.csv`**.

These are the **LaTeX source of the "Sample Data" tables in Appendix C** of
*Calendrical Calculations*, 3rd Edition (Dershowitz & Reingold, 2008). The book's Appendix C
table is too wide for one page, so it is split into five horizontal panels; each `datesN.tex`
is one panel. All five share an identical first column: the canonical **33 R.D.
(Rata Die / fixed-date) sample dates**, R.D. −214193 → 764652.

| File | Cols | Calendars covered |
|---|---|---|
| `dates1.tex` | 27 | weekday, Julian Day, Modified JD, Gregorian, ISO, Julian, Roman name, Egyptian, Armenian, Coptic |
| `dates2.tex` | 33 | Ethiopic, Islamic (arithmetic + observational), Bahá'í, Future Bahá'í, Mayan (Long Count/Haab/Tzolkin), Aztec (Xihuitl/Tonalpohualli) |
| `dates3.tex` | 38 | Hebrew (standard + observational), Easter (Julian/Gregorian/Astronomical), Balinese Pawukon, Persian (astro + arithmetic), French Revolutionary (original + modified) |
| `dates4.tex` | 37 | Chinese |
| `dates5.tex` | 13 | Astronomical floats: solar longitude, next solstice/equinox, lunar longitude, next new moon, dawn (Paris), sunset (Jerusalem) |

## Where it came from

Per `Readme.md`: *"Files dates[1-5].tex, containing test data, have been kindly provided to me
by Prof. Reingold."* This is **the authors' own LaTeX table source, handed directly to the
pycalcal author (Enrico Spinielli)** — not OCR'd, and not retyped from the printed page. That is
why the repository has clean, authoritative 3rd-edition sample data even though the printed
Appendix C tables are unextractable raster images in the PDF.

The book itself notes these values are *"as computed by our functions and hence may not represent
historical reality."* The data is therefore an **oracle from the reference Lisp implementation**,
not independent ground truth — its purpose is to verify that pycalcal reproduces CALENDRICA 3.0
*exactly*.

## How it is consumed

`trasformLatexDates2Cvs` (a `sed` one-liner tangled from `pycalcal.nw`) strips the LaTeX
(`$` and `\` removed, `&` → `,`) to produce `dates1.csv … dates5.csv`. The
`appendixCUnitTest.py` test classes (`AppendixCTable1–5TestCaseBase`) load those CSVs and assert
that each calendar conversion of the R.D. value matches. The generated `.csv` files are
gitignored (`*.csv`) because they are rebuilt by `make testdata`.

## The errata file

`dates5.errata.csv` is the **one CSV that is committed** — the exception to the `*.csv` gitignore
rule. It contains corrected **"next new moon"** moments (column 4 of `dates5.tex`). The test
explicitly *skips* `dates5.csv`'s own column 4
(`#self.nnm.append(float(row[4])) # read from errata file`) and reads the corrected value from
`dates5.errata.csv` instead.

Provenance: the **authors' post-publication errata** — the same correction stream captured in
`calendrica-3.0.errata.cl` and the `errata2009*–2013*.pdf` documents in the repository. The
original printed new-moon values were wrong; this file patches them without editing the
author-supplied `dates5.tex`.

## Summary chain

> Appendix C, *Calendrical Calculations* 3rd ed. → author-supplied LaTeX (`dates1–5.tex`) →
> `sed` (`trasformLatexDates2Cvs`) → CSV → `unittest` oracle (`appendixCUnitTest.py`), with the
> astronomical new-moon column overridden by author errata (`dates5.errata.csv`).

## Ultimate-Edition re-baseline (4th edition)

The Ultimate Edition revised the **Delta-T model** (`ephemeris-correction`), which shifts
every astronomical quantity by ~1e-3°. When pycalcal's astronomy was updated to the 4th
edition (see `docs/ultimate-port-plan.md` Tier 3), the 3rd-edition panel-5 sample values
(`dates5.tex`) and a few astronomical fixtures no longer matched. They were re-baselined to
the Ultimate astronomy:

- `dates5.ultimate.csv` (committed) — panel-5 columns (solar longitude, next solstice/equinox,
  lunar longitude, next new moon, dawn-in-Paris, sunset-in-Jerusalem) recomputed for the 33
  sample dates; `AppendixCTable5TestCaseBase` now loads it instead of `dates5.csv` +
  `dates5.errata.csv`.
- `dates4_ms.ultimate.csv` (committed) — the astronomical major-solar-term column, recomputed
  (the Chinese *date* and day-name still match 3rd-edition exactly).
- Hardcoded astronomy fixtures (`declinations`, `right_ascensions`, `lunar_altitudes`,
  `urbana_winter`, the year-333 `dynamical_from_universal` example) updated in `pycalcal.nw`.

The independent correctness check is the SBCL differential harness (`tools/diff_check.py`),
which validates pycalcal against the Ultimate Lisp oracle; these re-baselined unittest values
are Ultimate-edition regression snapshots. The integer `dates1`–`dates4` calendar columns are
unchanged and still validate against the author-supplied 3rd-edition data (they are identical
across editions).
