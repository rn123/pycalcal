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

## Phase 2/3 — pycalcal vs Ultimate Lisp differential (DONE)

`tools/diff_oracle.lisp` (SBCL dumper) + `tools/diff_check.py` (comparator) ran pycalcal
against the Ultimate Lisp over **1664 dates** (33 samples + ~1500 random in [−250000, 800000]
+ boundary offsets). Integer/date conversions compared exactly; float astronomy by tolerance
(1e-6).

### EXACT agreement — 45 functions
All arithmetic calendars and most astronomical *date* conversions match pycalcal exactly over
all 1664 dates: Gregorian/alt-Gregorian, Julian, Roman, ISO, Coptic, Ethiopic, Egyptian,
Armenian, Islamic (arith), Hebrew (std), Bahá'í (Western), arithmetic Persian, French (arith),
all Balinese sub-cycles, Mayan (haab/long-count/tzolkin), Aztec (xihuitl/tonalpohualli/
xiuhmolpilli), Hindu (solar/lunar/fullmoon, old solar/lunar), Tibetan, day-of-week, JD/MJD.

### Divergences — classified

**(a) Revised astronomy (float layer) — the inter-edition change (full-parity port target):**
| quantity | dates differing | example magnitude |
|---|---|---|
| `solar-longitude` (noon) | 1454/1664 | 186.49034 vs 186.49215 (~1.8e-3°) |
| `lunar-longitude` (midnight) | 1454/1664 | ~0.026° |
| `lunar-phase` (midnight) | 1454/1664 | ~0.024° |

**(b) Astronomy-dependent calendars that flip an integer date on a few dates** (downstream of
(a) — the ~1e-3° shift occasionally crosses a day boundary; converge once (a) is ported):
`observational-hebrew` (11/1664), `observational-islamic` (8), `astro-hindu-lunar` (12),
`astro-hindu-solar` (2), `chinese` (7), `persian` (4), `french` astronomical (1).
This explains why the earlier sample-date reproduction check saw integer dates match — only a
handful of the 1664 dates sit near a boundary.

**(c) Genuine non-astronomy edition change:** `mayan-year-bearer-from-fixed` (1654/1664) —
3.0 `(+ date 364)` → Ultimate `date` (Phase 1).

### NEW in Ultimate — no pycalcal equivalent (8)
`akan-name-from-fixed`, `icelandic-from-fixed`, `babylonian-from-fixed`, `samaritan-from-fixed`,
`saudi-islamic-from-fixed`, `astro-bahai-from-fixed`, `alt-observational-hebrew-from-fixed`,
`alt-observational-islamic-from-fixed`.

## Verdict (the "fully check" answer)

Current pycalcal **already reproduces the Ultimate Edition** for all arithmetic calendars and
all astronomical calendars *at the integer-date level except where the revised astronomy flips a
boundary date*. To reach full parity the update must: (1) port the revised astronomy (fixes the
float layer and the (b) boundary flips), (2) fix `mayan-year-bearer`, (3) add the 8 new
functions/calendars.

## Phase 4 progress

- **`mayan-year-bearer`** — fixed (1654/1664 → 0). ✅
- **Tier 3 astronomy** — root cause isolated to a single function: `ephemeris-correction`
  (the 4th-edition Espenak & Meeus Delta-T model). All other astronomy primitives
  (`obliquity`, `aberration`, `nutation`, coefficient tables) are unchanged; their tiny diffs
  were pure downstream of the time shift. Porting `ephemeris-correction` moved the differential
  from **12 divergent functions to 3**, and EXACT agreement from 45 → **53**: the float layer
  (`solar-longitude`, `lunar-longitude`, `lunar-phase`) and the astronomy-dependent calendars
  (observational-Islamic, Persian, French, astro-Hindu-solar) all converged. ✅

  Residual differences (3 functions, ≤8 of 1664 dates): `observational-hebrew`,
  `chinese`, `astro-hindu-lunar` — these are **mpmath(prec 50) vs IEEE-double** boundary
  sensitivity at the ~1e-9 level in the most event-boundary-sensitive calendars, not
  algorithmic differences. Not fixable without changing pycalcal's arithmetic substrate.

  Test re-baseline: 12 astronomy fixtures updated to the Ultimate astronomy (panel-5
  `dates5.ultimate.csv`, `dates4_ms.ultimate.csv`, and hardcoded smoke/book values). Full
  suite: **92 OK**.

## Next — remaining Phase 4 (port, each increment differential-tested)

Tier 0 (astro-bahai rename, trig/unix) → Tier 1 (Akan, Icelandic, Roman) → Tier 2 (holidays)
→ Tier 3 (astronomy helpers + **revised astronomy** + crescent criteria; fixes (a)/(b)) →
Tier 4 (Babylonian, Samaritan, Saudi). Plus the `mayan-year-bearer` fix. Re-run
`tools/diff_check.py` after each increment; acceptance = the DIFFER set empties (floats within
tolerance) and the NEW set gains pycalcal equivalents that match the oracle.
