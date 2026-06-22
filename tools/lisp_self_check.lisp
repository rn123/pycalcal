;;;; Phase 1: validate the repaired Ultimate Lisp against the clean 3.0 Lisp.
;;;;
;;;; Loads calendrica-3.0.cl into package CC3 and ultimate_calendrica.lisp into
;;;; CCU, then compares every 1-arg *-FROM-FIXED function present in BOTH over a
;;;; set of fixed dates. Unchanged calendars MUST agree exactly; any disagreement
;;;; is either a genuine edition change (expected: astronomical/observational,
;;;; astro-bahai) or an OCR-repair bug to fix. New Ultimate-only functions are
;;;; reported separately.
;;;;
;;;; Run: sbcl --non-interactive --load tools/lisp_self_check.lisp

(defpackage "CC3" (:use "COMMON-LISP"))
(defpackage "CCU" (:use "COMMON-LISP"))

(handler-bind ((warning #'muffle-warning))
  (load "calendrica-3.0.cl")
  (in-package "CCU")
  (load "ultimate_calendrica.lisp")
  (in-package "CL-USER"))

;; Test dates: the 33 Appendix C sample R.D. dates plus a dense modern range.
(defparameter *dates*
  (append
   '(-214193 -61387 25469 49217 171307 210155 253427 369740 400085 434355
     452605 470160 473837 507850 524156 544676 567118 569477 601716 613424
     626596 645554 664224 671401 694799 704424 708842 709409 709580 727274
     728714 744313 764652)
   (loop for rd from 730000 to 730120 collect rd)))

(defun shared-from-fixed-names ()
  "Names (strings) of *-FROM-FIXED symbols fbound in both CC3 and CCU."
  (let ((names '()))
    (do-symbols (s (find-package "CC3"))
      (let ((n (symbol-name s)))
        (when (and (search "-FROM-FIXED" n)
                   (fboundp s)
                   (let ((u (find-symbol n "CCU"))) (and u (fboundp u))))
          (pushnew n names :test #'string=))))
    (sort names #'string<)))

(defun call1 (pkg name rd)
  "Call (PKG::NAME rd), returning (values result ok). ok=nil on error/arity."
  (let ((fn (find-symbol name pkg)))
    (handler-case (values (funcall (symbol-function fn) rd) t)
      (error () (values nil nil)))))

(let ((shared (shared-from-fixed-names))
      (agree '()) (differ '()) (skipped '()))
  (dolist (name shared)
    (let ((mism 0) (tested 0) (sample nil))
      (dolist (rd *dates*)
        (multiple-value-bind (a oka) (call1 "CC3" name rd)
          (multiple-value-bind (b okb) (call1 "CCU" name rd)
            (when (and oka okb)
              (incf tested)
              (unless (equalp a b)
                (incf mism)
                (unless sample (setf sample (list rd a b))))))))
      (cond ((zerop tested) (push name skipped))
            ((zerop mism) (push name agree))
            (t (push (list name mism tested sample) differ)))))
  (format t "~%================ PHASE 1: 3.0 vs Ultimate ================~%")
  (format t "shared *-from-fixed functions: ~a~%" (length shared))
  (format t "~%AGREE exactly (~a):~%  ~{~a ~}~%" (length agree) (sort agree #'string<))
  (format t "~%DIFFER (~a):~%" (length differ))
  (dolist (d (sort (copy-list differ) #'string< :key #'first))
    (destructuring-bind (name mism tested sample) d
      (format t "  ~a  (~a/~a dates differ)  e.g. rd=~a 3.0=~a ULT=~a~%"
              name mism tested (first sample) (second sample) (third sample))))
  (when skipped
    (format t "~%SKIPPED (arity/error, ~a):~%  ~{~a ~}~%" (length skipped)
            (sort skipped #'string<)))
  ;; Also list Ultimate-only *-from-fixed (new calendars).
  (let ((newonly '()))
    (do-symbols (s (find-package "CCU"))
      (let ((n (symbol-name s)))
        (when (and (search "-FROM-FIXED" n) (fboundp s)
                   (let ((c (find-symbol n "CC3"))) (or (null c) (not (fboundp c)))))
          (pushnew n newonly :test #'string=))))
    (format t "~%ULTIMATE-ONLY *-from-fixed (~a):~%  ~{~a ~}~%"
            (length newonly) (sort newonly #'string<))))
