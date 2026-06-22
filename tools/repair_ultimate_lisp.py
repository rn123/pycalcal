#!/usr/bin/env python3
"""Repair the OCR'd Appendix D (Ultimate Edition Lisp) into loadable Common Lisp.

Input : ultimate_extract/appD_lisp_impl.txt  (text extracted from the PDF)
Output: ultimate_calendrica.lisp             (loadable in SBCL via the CC3 prelude)

The OCR has a regular structure we exploit:
  * page banners  "====..."  and  "PAGE nnn"   -> drop
  * each *source* line is prefixed with a per-definition counter "1 ", "2 ", ...
  * a PDF line-wrap appears as a physical line WITHOUT that counter prefix; it is a
    continuation of the previous source line. If the previous line ended with "-"
    the split was mid-token (e.g. "mean-synodic-" + "month") -> join with no space;
    otherwise join with a space.
  * each definition ends with a book equation tag like " (18.8)" -> strip.
  * prose (the appendix intro, section headers) sits between definitions at paren
    depth 0; we keep a line only when we are inside a form, or it starts one with "(".

Comments (";"...) are stripped to keep paren-counting honest and the output lean.
This is a best-effort mechanical pass; the load is then iterated until SBCL is happy.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "ultimate_extract", "appD_lisp_impl.txt")
OUT = os.path.join(ROOT, "ultimate_calendrica.lisp")

BANNER = re.compile(r"^=+\s*$")
PAGE = re.compile(r"^PAGE\s+\d+\s*$")
NUMPREFIX = re.compile(r"^(\d+)\s+(.*)$")          # "12 (foo ...)"  -> "(foo ...)"
EQTAG = re.compile(r"\s*\((?:Table\s+)?\d+\.\d+[a-z]?\)\s*$")  # trailing " (18.8)"
FORMSTART = re.compile(r"^\(\s*(def\w+|in-package|eval-when|declaim|proclaim)\b")


def strip_comment(s):
    """Remove a ';' comment to end of line, respecting #\\; char literals and strings."""
    out = []
    i, n, instr = 0, len(s), False
    while i < n:
        c = s[i]
        if instr:
            out.append(c)
            if c == '"' and (i == 0 or s[i - 1] != "\\"):
                instr = False
            i += 1
            continue
        if c == '"':
            instr = True
            out.append(c)
            i += 1
            continue
        if c == "#" and i + 1 < n and s[i + 1] == "\\":
            out.append(s[i:i + 3])      # char literal e.g. #\;  #\(
            i += 3
            continue
        if c == ";":
            break
        out.append(c)
        i += 1
    return "".join(out)


def paren_delta(s):
    """Net unescaped paren depth change of a (comment-stripped) line."""
    code = strip_comment(s)
    depth = 0
    i, n, instr = 0, len(code), False
    while i < n:
        c = code[i]
        if instr:
            if c == '"' and code[i - 1] != "\\":
                instr = False
            i += 1
            continue
        if c == '"':
            instr = True
        elif c == "#" and i + 1 < n and code[i + 1] == "\\":
            i += 3
            continue
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        i += 1
    return depth


def _extract_top_forms(blob, keep_heads):
    """Return the source text of each balanced top-level (HEAD ...) form whose HEAD
    is in keep_heads. Skips prose and any non-matching top-level forms."""
    forms = []
    i, n = 0, len(blob)
    instr = False
    while i < n:
        c = blob[i]
        if c != "(":
            i += 1
            continue
        # candidate form start at i; scan to its matching close, tracking strings
        depth, j, instr = 0, i, False
        while j < n:
            cj = blob[j]
            if instr:
                if cj == '"' and blob[j - 1] != "\\":
                    instr = False
            elif cj == '"':
                instr = True
            elif cj == "#" and j + 1 < n and blob[j + 1] == "\\":
                j += 3
                continue
            elif cj == "(":
                depth += 1
            elif cj == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            break  # unbalanced tail; stop
        form = blob[i:j + 1]
        head = re.match(r"\(\s*([A-Za-z0-9*+/<>=!?._-]+)", form)
        if head and head.group(1).lower() in keep_heads and "..." not in form:
            forms.append(re.sub(r"[ \t]+", " ", form).strip())
        i = j + 1
    return forms


def main():
    with open(SRC, encoding="utf-8") as fh:
        raw = fh.readlines()
    # OCR rendered Lisp punctuation as Unicode: backquote -> U+2018, quote/double
    # quotes -> U+2019/U+201C/U+201D. Normalize to ASCII reader syntax.
    raw = [ln.replace("‘", "`").replace("’", "'")
             .replace("“", '"').replace("”", '"') for ln in raw]

    # Pass 1: drop banners/PAGE, strip number prefixes, classify continuations,
    # rejoin wraps into logical source lines.
    logical = []  # list of source-line strings (no leading counter)
    for line in raw:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if BANNER.match(line) or PAGE.match(line):
            continue
        m = NUMPREFIX.match(line)
        if m:
            logical.append(m.group(2))
        else:
            # continuation (PDF wrap) OR prose. Attach to previous logical line if
            # we are mid-form; prose handling happens in pass 2.
            if logical:
                prev = logical[-1]
                if prev.endswith("-"):
                    logical[-1] = prev + line.strip()
                else:
                    logical[-1] = prev + " " + line.strip()
            else:
                logical.append(line)

    # Pass 2: join into one blob, strip comments + equation tags everywhere, then
    # extract only *balanced top-level def-forms*. This drops all prose (incl. the
    # inline prose and fake syntax examples on the intro pages) and the book's
    # "(1.59)"-style tags, keeping only real definitions.
    blob = "\n".join(strip_comment(s) for s in logical)
    blob = re.sub(r"\((?:Table\s+)?\d+\.\d+[a-z]?\)", " ", blob)  # equation tags

    KEEP_HEADS = {
        "defun", "defconstant", "defmacro", "defparameter", "defvar",
        "defstruct", "defgeneric", "defmethod", "declaim",
    }
    forms = _extract_top_forms(blob, KEEP_HEADS)

    # Reorder for self-contained load: macros first (needed at compile time of any
    # function that uses them), then functions, then constants/params (whose
    # load-time values may call any function). Relative order preserved within each
    # group. Function *bodies* referencing constants resolve at call time, so this
    # is safe; it only fixes the OCR's scrambled intro ordering.
    def head_of(f):
        m = re.match(r"\(\s*([A-Za-z0-9*+/<>=!?._-]+)", f)
        return m.group(1).lower() if m else ""
    macros = [f for f in forms if head_of(f) == "defmacro"]
    funcs = [f for f in forms if head_of(f) in ("defun", "defgeneric", "defmethod")]
    rest = [f for f in forms if head_of(f) not in
            ("defmacro", "defun", "defgeneric", "defmethod")]
    out_lines = macros + funcs + rest

    header = (
        ";;;; AUTO-REPAIRED from ultimate_extract/appD_lisp_impl.txt by\n"
        ";;;; tools/repair_ultimate_lisp.py -- do not edit by hand.\n"
        ";;;; Package-neutral: the caller sets *package* (CL-USER for a standalone\n"
        ";;;; oracle, or CCU for side-by-side cross-validation against CC3/3.0).\n\n"
    )
    with open(OUT, "w") as fh:
        fh.write(header)
        fh.write("\n".join(out_lines))
        fh.write("\n")

    ndef = sum(1 for f in out_lines if f[:5].lower().startswith("(defu"))
    nconst = sum(1 for f in out_lines if f.lower().startswith("(defconstant"))
    print("Wrote %s" % OUT)
    print("  logical source lines: %d" % len(logical))
    print("  top-level forms kept: %d  (defun=%d defconstant=%d)"
          % (len(out_lines), ndef, nconst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
