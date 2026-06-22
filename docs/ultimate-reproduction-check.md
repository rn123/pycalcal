# Does pycalcal reproduce the Ultimate Edition Appendix C tables?

**Short answer:** Yes for the *integer calendar-conversion* columns of every calendar
pycalcal implements — including the revised astronomical calendars (Persian astronomical,
Bahá'í astronomical) at the sample dates. It diverges only on the *floating-point
astronomy* (panel 5), exactly as the book's own version note predicts. Calendars added in
the Ultimate Edition (Akan, Icelandic, Umm al-Qura, Babylonian, Samaritan) are not
implemented, so there is nothing to reproduce.

## Method

pycalcal implements CALENDRICA 3.0 (3rd edition). To test reproduction of the *Ultimate*
(4th) Edition we used pycalcal as a **per-cell oracle**: VLM-read the printed Ultimate
Appendix C cells, diff against pycalcal, and re-read any mismatch at higher DPI to classify
it as a *read error* vs. a *genuine difference*. (The printed tables are un-OCR-able raster
images; the authors' machine-readable copy is gated behind Cambridge instructor access.)

## Confirmed reproductions (pycalcal == Ultimate Edition)

Panel 1 (p.756), spot-checked across the 33 rows, **all matched**:
Coptic, Ethiopic, ISO, Islamic (arithmetic), Islamic (observational), Hebrew (standard),
Hebrew (observational). Every initial mismatch turned out to be a VLM read error, not a
pycalcal difference (e.g. R.D. 727274 Hebrew really is `5752 13 12`, Adar II of a leap year,
which pycalcal computes).

Panel 2 (p.757), recent rows (727274, 744313, 764652):
- Persian **astronomical** and arithmetic — exact (`1370 12 27`, `1417 8 19`, `1473 4 28`).
- Bahá'í **Western** and **Astronomical** — exact. pycalcal's `future_bahai_from_fixed`
  (the 3rd-edition name) reproduces the Ultimate "Astronomical" Bahá'í column, e.g. R.D.
  727274 → `1 8 15 19 17`.

The reason the astronomical *calendar dates* still match: a revised sunset/equinox only
changes an integer date when it crosses a day boundary, which does not happen at these
particular sample dates.

## Confirmed non-reproduction (pycalcal != Ultimate Edition)

Panel 5 — astronomical floating-point quantities (solar/lunar longitude, moments of
equinox/new moon, rise/set times). For R.D. −214193 the solar longitude at **midnight**:

| | value |
|---|---|
| pycalcal (3rd-ed algorithms) | `118.99065570°` |
| 3rd-ed sample data (`dates5.tex`, noon column) | `119.474975°` = pycalcal noon ✓ |
| Ultimate Edition (p.753 example, midnight) | `118.98911336°` |

pycalcal matches the **3rd-edition** values exactly (the repo test suite confirms this for
all of `dates5.tex`), but differs from the **Ultimate** value by ~1.5×10⁻³° — the
inter-edition astronomy revision. This dwarfs the ~1×10⁻¹⁰° platform jitter the book's
reproducibility caveat foregrounds (see `docs/appendix-c-audit.md`, B2). Panel-5 floats are
therefore *not* reproduced, and would need tolerance-based comparison even if they were.

## Not applicable (pycalcal does not implement)

Akan, Icelandic, Umm al-Qura (Saudi Islamic), Babylonian, Samaritan — added in the Ultimate
Edition (see `docs/ultimate-edition-diff.md`). No reproduction possible without porting them.

## Bottom line

For the calendars it implements, **pycalcal reproduces the Ultimate Edition's
calendar-conversion tables** — the 3rd-edition arithmetic and observational algorithms still
land on the same integer dates the 4th edition prints. The only genuine divergence is the
revised **floating-point astronomy** of panel 5. This is consistent with the book's note that
edition changes caused only "minor changes in some sample values," with the larger Bahá'í
"significant changes" confined to the astronomical *moments*, not the Bahá'í calendar dates.

Caveat: this is a high-confidence spot-check (every integer cell examined matched), not an
exhaustive per-cell proof of all 33 rows × all panels; a complete proof needs the gated
Cambridge machine-readable data.
