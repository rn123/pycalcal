# Reconstructing Appendix C (Roegel-style)

A prototype that **recomputes** the *Calendrical Calculations* Appendix C sample
data with `pycalcal` and typesets it as LaTeX, instead of OCR'ing the printed
(raster) tables. This follows Denis Roegel's LOCOMAT method: *a table you can
compute should never be transcribed.*

## Why

The Ultimate Edition's Appendix C sample-data pages are vector/raster images with
no text layer; OCR of the dense numeric grids produces garbage (verified — see the
session that produced `docs/test-data.md`). But every value in Appendix C is, by
construction, the output of the book's own functions — and `pycalcal` implements
those functions. So the reconstruction route is exact, not approximate.

## The pipeline (mirrors Roegel)

1. **Recompute** every cell from the implementation (`pycalcal`), never the page.
2. **Cross-check** against an independent source — the author-supplied
   `dates1.tex` (delivered as `dates1.csv`; see `docs/test-data.md`). Agreement of
   two independent sources is Roegel's confidence check and his errata-detection
   step. The prototype reports any discrepancy; currently **all 33 dates × 10
   calendars agree**.
3. **Emit LaTeX** reproducing the *structure* of the book's panel — one row per
   R.D. date — with a footer naming the `pycalcal` function behind each column.
   (The book prints each column's equation number and page; we print column
   provenance the same way.)

## Run it

```sh
make testdata                                   # produces dates1.csv (the cross-check source)
.venv/bin/python tools/recompute_appendix_c.py  # -> recon/appendixC_panel1.tex  (+ cross-check report)
cd recon && pdflatex appendixC_panel1.tex       # -> appendixC_panel1.pdf (1 page, A3 landscape)
```

`--check` validates against the book data without writing output (usable as a CI gate).

## Scope

This covers **panel 1** — the 10 calendars `pycalcal` implements from CALENDRICA
3.0: weekday, Julian Day, Modified JD, Gregorian, ISO, Julian, Roman name,
Egyptian, Armenian, Coptic.

The Ultimate Edition's later panels add Babylonian, Icelandic, Samaritan, Akan and
Saudi-Islamic columns (and the astronomical Bahá'í revision) that `pycalcal` does
not yet provide — see `docs/ultimate-edition-diff.md`. Extending the reconstruction
to those panels requires porting those calendars first; the generator
(`tools/recompute_appendix_c.py`) is structured so new columns are one entry each
in its `COLUMNS` table.

## Caveat (epistemic)

Roegel reconstructs deterministic closed-form functions (logs, trig) where the
recomputation is ground truth. Calendrical sample data is an *implementation
oracle* — the book states the values are "as computed by our functions and hence
may not represent historical reality." So a `pycalcal`-vs-book agreement validates
*consistency between two implementations of CALENDRICA*, not historical
correctness. Same mechanic as LOCOMAT, weaker epistemic claim.
