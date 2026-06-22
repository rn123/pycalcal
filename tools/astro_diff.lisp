;;;; Isolate which astronomy primitives changed in BEHAVIOR between 3.0 and the
;;;; Ultimate Edition. Loads 3.0 (CC3) and the repaired Ultimate (CCU), calls each
;;;; single-moment astronomy function on several moments, reports value diffs.
;;;;
;;;; Run: sbcl --non-interactive --load tools/astro_diff.lisp

(defpackage "CC3" (:use "COMMON-LISP"))
(defpackage "CCU" (:use "COMMON-LISP"))
(handler-bind ((warning #'muffle-warning))
  (load "calendrica-3.0.cl")
  (in-package "CCU")
  (load "ultimate_calendrica.lisp")
  (in-package "CL-USER"))

(defparameter *moments* '(-214193.0d0 0.0d0 500000.0d0 730000.5d0 764652.0d0))
(defparameter *fns*
  '("EPHEMERIS-CORRECTION" "DYNAMICAL-FROM-UNIVERSAL" "JULIAN-CENTURIES"
    "EQUATION-OF-TIME" "OBLIQUITY" "ABERRATION" "NUTATION" "SOLAR-LONGITUDE"
    "LUNAR-LONGITUDE" "LUNAR-PHASE" "LUNAR-LATITUDE" "LUNAR-DISTANCE"
    "MEAN-LUNAR-LONGITUDE" "SOLAR-LONGITUDE-AFTER" "APPARENT-FROM-UNIVERSAL"))

(defun callf (pkg name arg)
  (let ((s (find-symbol name pkg)))
    (when (and s (fboundp s))
      (handler-case (values (funcall (symbol-function s) arg) t)
        (error () (values nil nil))))))

(format t "~%======= astronomy 3.0 vs Ultimate (by value) =======~%")
(dolist (name *fns*)
  (let ((maxdiff 0) (tested 0) (sample nil) (present-both t))
    (dolist (m *moments*)
      (multiple-value-bind (a oka) (callf "CC3" name m)
        (multiple-value-bind (b okb) (callf "CCU" name m)
          (cond ((not (and (find-symbol name "CC3") (find-symbol name "CCU")))
                 (setf present-both nil))
                ((and oka okb (numberp a) (numberp b))
                 (incf tested)
                 (let ((d (abs (- a b))))
                   (when (> d maxdiff) (setf maxdiff d sample (list m a b)))))))))
    (cond ((not present-both) (format t "  ~a : (not in both)~%" name))
          ((zerop tested) (format t "  ~a : (no numeric result)~%" name))
          ((zerop maxdiff) (format t "  ~30a SAME~%" name))
          (t (format t "  ~30a DIFFER maxabs=~,3e  e.g. m=~a 3.0=~a ULT=~a~%"
                     name maxdiff (first sample) (second sample) (third sample))))))
