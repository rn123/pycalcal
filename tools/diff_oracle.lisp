;;;; Phase 2 oracle dumper: load the repaired Ultimate Lisp and, for each fixed
;;;; date in diff_dates.txt, print every 1-arg *-FROM-FIXED value as:
;;;;     <rd> <lisp-name> <value-sexpr>
;;;; plus selected float astronomy quantities. Consumed by tools/diff_check.py.
;;;;
;;;; Run: sbcl --non-interactive --load tools/diff_oracle.lisp

(handler-bind ((warning #'muffle-warning))
  (load "ultimate_calendrica.lisp"))

(defun read-dates (path)
  (with-open-file (s path)
    (loop for line = (read-line s nil) while line
          for trimmed = (string-trim " 	" line)
          when (plusp (length trimmed)) collect (parse-integer trimmed))))

(defun from-fixed-names ()
  (let ((names '()))
    (do-symbols (s *package*)
      (let ((n (symbol-name s)))
        (when (and (search "-FROM-FIXED" n) (fboundp s))
          (pushnew n names :test #'string=))))
    (sort names #'string<)))

(let* ((dates (read-dates "diff_dates.txt"))
       (names (from-fixed-names))
       (*read-default-float-format* 'double-float))
  ;; integer/date-structured calendar conversions
  (dolist (rd dates)
    (dolist (name names)
      (let ((fn (find-symbol name)))
        (multiple-value-bind (val ok)
            (ignore-errors (values (funcall (symbol-function fn) rd) t))
          (when ok
            (format t "~a ~a ~s~%" rd name val))))))
  ;; selected float astronomy (compared with tolerance on the Python side)
  (dolist (rd dates)
    (flet ((emit (label form) (let ((v (ignore-errors form)))
                                (when v (format t "~a ~a ~s~%" rd label v)))))
      (emit "SOLAR-LONGITUDE-NOON" (solar-longitude (+ rd 0.5d0)))
      (emit "LUNAR-LONGITUDE-MID" (lunar-longitude (coerce rd 'double-float)))
      (emit "LUNAR-PHASE-MID" (lunar-phase (coerce rd 'double-float))))))
