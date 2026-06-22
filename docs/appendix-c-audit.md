# Audit: instructions in Appendix C (Ultimate Edition)

Scope: the *instructional prose* on pp. 752–755 of *Calendrical Calculations: The
Ultimate Edition* — what the appendix tells an implementer to do and expect. The
numeric tables on pp. 756–773 are raster images with no text layer, so this audits
the **instructions**, not the table cells. Numeric fragments that were typeset as
math/vector and initially lost in text extraction were recovered by a Vision pass
over the rendered pp. 752–753 (see "Recovered fragments" below).

## A. What the appendix instructs

1. **Purpose** — "To aid the reader interested in implementing our functions" → the
   tables are test vectors. Two sets: (i) 33 sample dates (years **−1000 to 2100**)
   with all-calendar equivalents + astronomy; (ii) Gregorian dates of holidays/events
   2000–2103.
2. **Per-date columns** — all calendars, plus Easter (Orthodox/Gregorian/astronomical),
   ephemeris correction, equation of time, **solar longitude at 12:00:00 UT**, next
   solstice/equinox, dawn (Paris), midday (Tehran), sunset (Jerusalem), lunar
   longitude/latitude/altitude at **00:00:00 UT**, next new moon, moonrise/moonset
   (Mecca).
3. **Column provenance** — "At the bottom of each column…is the equation number and
   corresponding page of the function used to compute that column."
4. **Version note** — hardware/software changes since the 3rd ed. caused "minor changes
   in some sample values"; the future→**astronomical Bahá'í** revision caused
   "significant changes."
5. **Oracle caveat** — values are "as computed by our functions and hence may not
   represent historical reality"; "some dates are not meaningful for all calendars";
   negative Julian/Roman years are "raw output from the Lisp functions" (BCE).
6. **Precision caveats** — times reported to the second but the algorithms "do not
   promise such accuracy"; and (§1.16) floating-point results "differ depending on
   language, implementation, and platform," demonstrated with a worked example.

## B. Findings

### B1 — Noon-vs-midnight: the table column and the reproducibility example use different times (verified)
The column (A2) is solar longitude **at noon, 12:00:00 UT**. The p.753 example computes
`solar-longitude(−214193)` — an **integer R.D., i.e. midnight UT**, explicitly labelled
"at midnight." They are different quantities:

| Quantity | pycalcal | Reference |
|---|---|---|
| solar longitude @ **noon** (rd+0.5) | `119.47497460` | dates5 column = `119.474975` ✓ |
| solar longitude @ **midnight** (rd+0.0) | `118.99065570` | book example = `118.98911336…` |

The example is internally consistent (it says "midnight"), but the value it makes famous,
`118.989…°`, does **not** appear in the table — the table's solar-longitude cell for the
first date is the noon value `≈119.47°`. An implementer validating against the example
while reading the noon column will see a ~0.49° mismatch. The two are never reconciled in
the text.

### B2 — Cross-edition drift ≫ the platform jitter the caveat foregrounds (verified)
The caveat (A6) quantifies the platform spread as **≈1×10⁻¹⁰ of arc (≈8×10⁻⁸ s of time)**
and concludes such differences are "highly unlikely to affect the computations of dates."
True *within an edition*. But pycalcal's midnight value (`118.9907`, 3rd-ed algorithms)
differs from the Ultimate example (`118.9891`) by **~1.5×10⁻³ °** — about **7 orders of
magnitude larger** than that jitter. That gap is the inter-edition astronomy revision (A4),
not floating-point noise; the reassurance does not cover it.

### B3 — pycalcal (3rd ed.) cannot reproduce Ultimate-Edition values for revised subsystems
Per A4 + `docs/ultimate-edition-diff.md`: pycalcal implements 3rd-ed `future-bahai`, so its
**Bahá'í** sample values differ *significantly* from the Ultimate Edition's `astro-bahai`.
Any reconstruction must declare its target edition. The repo's reconstruction targets the
3rd-ed data (`dates*.tex`) and matches that, **not** the Ultimate tables.

### B4 — The Ultimate panel is richer than the shipped test data
A2 lists ephemeris correction, equation of time, lunar latitude/altitude, Tehran midday and
Mecca moonrise/moonset — columns **absent** from the 3rd-ed `dates5.tex` in the repo.
Extending the reconstruction to panel 5 needs both the new astronomy ported and the Ultimate
reference values (the printed ones are un-OCR-able).

### B5 — Float columns require tolerance, not equality (instruction sound; prototype honors it)
A6 implies exact equality is wrong for astronomy columns. pycalcal's `mp.prec=50` and
`assertAlmostEqual` tests conform. Note the reference values were computed in **hardware
double precision** (Intel Xeon, ~208 s) while pycalcal uses **arbitrary-precision mpmath** —
different arithmetic, so panel-5 floats won't match to all digits even within an edition.
(This is why `dates5.errata.csv` exists.) The panel-1 prototype is immune: its columns are
exact integers or exact JD.

### B6 — Oracle / raw-output instructions are internally consistent and honored
A5's "raw Lisp output / negative = BCE" matches what the prototype emits (e.g. Julian
`−587.7.30`, Roman year `−587`) without cosmetic correction — faithful to the instruction.

## C. Recovered fragments (Vision pass over pp. 752–753)
Four numeric/inline-math items were lost in text extraction and recovered from the rendered
pages; all are now reflected above:

| Fragment | Recovered value |
|---|---|
| date-range start year | **−1000** ("from the years −1000 to 2100") |
| R.D. in the p.753 example | **−214193** |
| the displayed expression | **`solar-longitude(−214193)`** (midnight; confirms B1) |
| platform-spread magnitude | **≈1×10⁻¹⁰ of arc, ≈8×10⁻⁸ s of time** |

## Bottom line
The instructions are largely sound, and the repo's reconstruction conforms to the auditable
ones (provenance footer, raw-output rendering, exactness on panel 1). The one real trap is
**B1** — the noon table column vs. the midnight reproducibility example, never reconciled,
which will mislead anyone validating against the famous `118.989°` figure. The most
under-weighted point is **B2/B3**: cross-edition differences dwarf the platform jitter the
caveat foregrounds, so 3rd-ed code (pycalcal) will not reproduce Ultimate values — Bahá'í
most of all.
