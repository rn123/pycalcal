# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

PyCalCal is a Python port of *CALENDRICA 3.0*, the Common Lisp implementation accompanying Dershowitz & Reingold's *Calendrical Calculations* (3rd ed.). It converts dates among ~31 calendars and computes astronomical events (equinoxes, solstices, sunrise/sunset, holidays). A few astronomy routines come from Meeus, *Astronomical Algorithms*.

## Literate programming — the source of truth is `pycalcal.nw`

This is the single most important thing to understand before editing:

- **`pycalcal.nw`** (noweb) is the canonical source. It contains the library code, the unit tests, the LaTeX documentation, and even the `Makefile` itself — all as tangled chunks.
- **`pycalcal/pycalcal.py`** is *generated* output (header: "ANY CHANGES WILL BE OVERWRITTEN"). It is committed for convenience (the repo was packaged so the file ships ready-to-import), but hand-edits to it are not the real fix. To change behavior correctly, edit the corresponding chunk in `pycalcal.nw` and re-tangle. In practice the committed `.py` and `.nw` can drift; if asked for a quick patch, you may edit the `.py` directly but call out that the `.nw` source should be updated to match.
- **`calendrica-3.0.cl`** (+ `calendrica-3.0.errata.cl`) is the original Common Lisp, included for reference only. Nearly every Python function carries a `# see lines NNN-MMM in calendrica-3.0.cl` comment — use these to cross-check translations against the original.

## Build / test commands

The build pipeline requires `noweb` (`notangle`/`noweave`), `make`, `sh`, and (for docs) a LaTeX distribution with asymptote/metapost. `mpmath` is the one runtime dependency (declared in `setup.py`, imported by the generated code).

```sh
./makemake.sh          # bootstrap: tangles the Makefile out of pycalcal.nw
make pycalcal.py       # tangle the library
make check             # tangle pycalcaltests.py and run the full unittest suite
make test              # build test data + per-calendar UnitTest .py files
make pycalcal.pdf      # weave the documentation (needs LaTeX); `make figures` first
```

There is no pytest/lint config. Tests use the stdlib `unittest`. `make check` tangles `pycalcaltests.py` and runs `python pycalcaltests.py`. To run a single calendar's tests, build that file and invoke it directly, e.g.:

```sh
make gregorianCalendarUnitTest.py
python -m unittest gregorianCalendarUnitTest
```

Tests validate against worked examples in the book and Appendix C tables; reference date data is tangled from `dates[1-5].tex` into CSVs (see `docs/test-data.md` for provenance).

### Running the tests from a clean clone

Nothing runnable is committed — the Makefile, tangled `*UnitTest.py`, `pycalcaltests.py`, and `dates*.csv` are all build artifacts (gitignored). The whole suite (92 tests: the Appendix C oracle + per-calendar smoke tests) does pass under Python 3 once bootstrapped:

```sh
brew install noweb                                   # provides notangle/noweave/cpif
python3 -m venv .venv && .venv/bin/pip install mpmath
./makemake.sh && make pycalcal.py testdata
make $(grep -oE '[a-zA-Z]+UnitTest\.py' pycalcal.nw | sort -u | grep -v xyzzy) pycalcaltests.py
make package                                         # sync the tangle into the package (see below)
.venv/bin/python pycalcaltests.py                    # -> Ran 92 tests ... OK
```

One gotcha the bootstrap papers over, worth knowing before editing:

- **`pycalcal/__init__.py` must re-export** (`from pycalcal.pycalcal import *`); when empty, `from pycalcal import *` — used by every test and any pip consumer — silently imports nothing.

`make pycalcal.py` writes the tangle to the repo root, but the importable package ships `pycalcal/pycalcal.py`. The `package` target (a dependency of `code`) copies the tangle across when it is newer, so a normal `make code` keeps them in sync; run `make package` explicitly after a bare `make pycalcal.py`.

## Conventions that matter when reading the code

- **`rd` / "fixed" dates** are the universal pivot: every calendar converts via `fixed_from_X` / `X_from_fixed`, with fixed-date 0 = R.D. epoch. New conversions should route through fixed dates, not calendar-to-calendar directly.
- Lisp semantics are reproduced deliberately: `quotient`, `ifloor`, `iround` are redefined so they always return integers (matching CL `floor`/`round`), unlike Python's `//`. Don't "simplify" these to plain `//`.
- `mp.prec = 50` (mpmath) is set to match CL's `L0` ≥50-bit precision postfix. Angles are kept in `[0, 360)` — a subtlety that caused real test failures historically (see `STATUS`).
- Dates are plain lists, e.g. `gregorian_date(2006, 2, 5)` → `[2006, 2, 5]`.

## Python version note

`Install.md` predates the Python 3 port and says "≥2.5 and <3.0" — that is stale. `setup.py` requires `python_requires='>=3.6'`, and the code uses `builtins` and `from __future__ import division`. Treat this as a Python 3 project.

## License

This port is MIT (Enrico Spinielli). The underlying CALENDRICA 3.0 is copyright Reingold & Dershowitz — see `COPYRIGHT_DERSHOWITZ_REINGOLD`.
