# Porting pycalcal to the Ultimate Edition — prioritized plan

All edits go in `pycalcal.nw` (the literate source), then `make code` re-tangles and syncs
the package; add tests to the relevant `*UnitTest` chunk and run `pycalcaltests.py`.

## Verified gap (not the raw name-diff)

The earlier name-diff (`docs/ultimate-edition-diff.md`) over-counted: pycalcal already has
`moonrise`, `refraction`, `lunar-node`, `sidereal-lunar-longitude`, `observed-lunar-altitude`,
`sin-degrees`, `phasis-on-or-before`, `lunar-phase`, `visible-crescent`, `sunset/sunrise`.
Checking the "added" list against the actual source leaves **31 genuinely missing functions**.
The astronomy infrastructure is largely present, so the crescent-visibility calendars are
closer than they looked.

Reproduction status (`docs/ultimate-reproduction-check.md`): pycalcal already reproduces the
Ultimate integer calendar columns for every calendar it implements; the only divergence is
panel-5 floating-point astronomy.

## Tier 0 — Alignment / quick wins (hours, ~zero risk)

1. **Bahá'í astronomical rename.** Add `astro-bahai-from-fixed` / `fixed-from-astro-bahai`
   (+ `astro-bahai-new-year-on-or-before`) as the canonical names; keep `future-bahai-*` as
   deprecated aliases. The algorithm **already reproduces** the Ultimate "Astronomical"
   Bahá'í column (verified), so this is pure terminology. *Highest value-to-effort.*
2. **Trig name consistency.** Add `cos-degrees`/`tan-degrees` aliases (pycalcal has
   `cosine-degrees`/`tangent-degrees` and `sin-degrees`); add `sine-degrees` alias.
3. **Unix time.** `moment-from-unix`, `unix-from-moment` (constant offset from the Unix
   epoch). Trivial arithmetic.

Tests: round-trip identity + the panel-2 Bahá'í values already captured.

## Tier 1 — Self-contained calendars (arithmetic, no new astronomy)

4. **Akan day-names** (`akan-name`, `-prefix`, `-stem`, `-name-from-fixed`,
   `-day-name`, `-name-difference`, `akan-day-name-epoch`). Trivial cyclical calendar.
5. **Icelandic calendar** (`icelandic-from-fixed`, `fixed-from-icelandic`, `-date/-month/
   -year/-season/-summer/-winter/-week/-weekday`, `icelandic-leap-year?`, `icelandic-epoch`).
   Depends only on Gregorian + `day-of-week-from-fixed`.
6. **Roman additions** (`olympiad`/`-from-julian-year`/`julian-year-from-olympiad`/`-cycle`/
   `-year`, `auc-year-from-julian`, `julian-year-from-auc`, `italian-from-local`,
   `local-from-italian`, the `*-season-in-gregorian` helpers). Arithmetic; Italian hours need
   `sunset` (present).

Tests: round-trip identity; spot-check against any VLM-read Ultimate cells.

## Tier 2 — Holidays (small, depend only on existing calendars)

7. `hanukkah`, `nowruz`, `mawlid` (rename of `mawlid-an-nabi` if present), `birth-of-the-bab`
   (needs Tier 0 Bahá'í), `unlucky-fridays`, `hebrew-in-gregorian`.

## Tier 3 — Astronomy helpers (prerequisites for Tier 4)

8. `moonset`, `moonlag`, `solar-altitude`, `apparent-from-universal`,
   `universal-from-apparent`. Incremental given existing `moonrise`/`refraction`/
   `lunar-altitude`.
9. Crescent-visibility criteria: `arc-of-light`, `arc-of-vision`, `yallop-criterion`,
   `shaukat-criterion`, `saudi-criterion`, `babylonian-criterion`, `bruin-best-view`,
   `simple-best-view`.

## Tier 4 — Astronomy-dependent new calendars (highest effort; need Tier 3)

10. **Babylonian** (`babylonian-from-fixed` + cluster; needs `babylonian-criterion`,
    `lunar-phase`+`sunset` which exist).
11. **Samaritan** (`samaritan-from-fixed` + cluster; needs `samaritan-noon`/`-new-moon`,
    solar/lunar, which exist).
12. **Saudi / Umm al-Qura Islamic** (`saudi-islamic-from-fixed` + cluster; needs
    `saudi-criterion`).

## Cross-cutting (low priority / optional)

- **Panel-5 astronomy revision.** Updating the revised solar/lunar algorithms so the
  floating-point columns match the Ultimate values. Deprioritized: integer dates already
  reproduce, the divergence is ~1.5×10⁻³°, and it can't be regression-tested without the
  gated Cambridge sample data.

## Testing constraint

There is no public machine-readable Ultimate sample data (Cambridge instructor-locked). So
new calendars are validated by (a) round-trip identity, (b) the Lisp in Appendix D as the
spec, and (c) the handful of Ultimate cells captured by VLM. Full Appendix C oracle tests for
the new columns wait on the Cambridge data.

## Suggested execution order

Tier 0 → 1 → 2 deliver most of the user-visible gap (new calendars + holidays + correct
Bahá'í naming) with little astronomy risk. Tier 3 → 4 is one coherent astronomy push that
unlocks the three crescent-based calendars together.
