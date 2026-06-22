# Ultimate-Edition verification — check report

Status of "fully check current pycalcal against the Ultimate Edition" (see the plan in
`.claude/plans/`). Verification uses the repaired Ultimate Lisp (`tools/repair_ultimate_lisp.py`
→ `ultimate_calendrica.lisp`) as an SBCL oracle, validated against the clean `calendrica-3.0.cl`.

## Phase 0 — repaired Ultimate Lisp (DONE)

`ultimate_calendrica.lisp` loads cleanly in SBCL: **554 defun, 116 defconstant**. All new
calendars bind and execute (Babylonian, Icelandic, Akan, Samaritan, Saudi/Umm-al-Qura,
astro-Bahá'í). `gregorian-from-fixed` matches pycalcal exactly on sample dates.

## Phase 1 — oracle fidelity vs clean 3.0 (DONE)

`tools/lisp_self_check.lisp` loads 3.0 into package CC3 and the repaired Ultimate into CCU and
compares every shared 1-arg `*-from-fixed` function over the 33 sample dates + a modern range.

**Result: 52 of 53 shared `*-from-fixed` functions agree exactly.** This validates the OCR
repair — function bodies are faithful, not corrupted. Astronomical date-level conversions
(Persian, Chinese, Hindu-astro, observational Hebrew/Islamic) agree, consistent with the
finding that integer dates are robust to the inter-edition astronomy revision (the float-level
divergence lives in `solar-longitude`/moment functions, audited separately).

### Genuine edition change found (date layer)

- **`mayan-year-bearer-from-fixed`** — 3.0 uses `(+ date 364)`, Ultimate uses `date`:
  ```
  3.0 : (mayan-haab-on-or-before (mayan-haab-date 1 0) (+ date 364))
  ULT : (mayan-haab-on-or-before (mayan-haab-date 1 0) date)
  ```
  Confirmed against the OCR raw (not an extraction artifact). → pycalcal's
  `mayan_year_bearer_from_fixed` must be updated in the port.

### Ultimate-only `*-from-fixed` (new calendars / variants)

`akan-name-from-fixed`, `icelandic-from-fixed`, `babylonian-from-fixed`, `samaritan-from-fixed`,
`saudi-islamic-from-fixed`, `astro-bahai-from-fixed`, `alt-observational-hebrew-from-fixed`,
`alt-observational-islamic-from-fixed`.

### Coverage caveat

Phase 1 compared the `*-from-fixed` (integer date) layer only. Still to compare: `fixed-from-*`
inverses, holiday functions, and the float-level astronomy (`solar-longitude`, moment, rise/set)
where the edition divergence is expected. These are covered by the Phase 2 differential harness
(pycalcal vs Ultimate Lisp) and round-trip checks.

## Next

- Phase 2: SBCL differential harness (`tools/diff_oracle.lisp` + `tools/diff_check.py`) —
  pycalcal vs Ultimate Lisp over many random + boundary dates, integers exact / floats by
  tolerance, including `fixed-from-*` round-trips and the float astronomy.
- Phase 3: complete this report with the full pycalcal-vs-Ultimate matrix.
- Phase 4: port (Tiers 0–4) + the `mayan-year-bearer` fix; each increment differential-tested.
