;;;; Dump every Appendix C quantity from the Ultimate Lisp for the 33 sample
;;;; dates, so tools/appc_compare.py can diff them against pycalcal's computed
;;;; values cell-by-cell (the complete computed-vs-book-code comparison).
;;;;
;;;; Emits lines:  <rd> <colkey> <value-sexpr>
;;;; Run: sbcl --non-interactive --load tools/appc_full_oracle.lisp

(handler-bind ((warning #'muffle-warning))
  (load "ultimate_calendrica.lisp"))

(defparameter *dates*
  '(-214193 -61387 25469 49217 171307 210155 253427 369740 400085 434355
    452605 470160 473837 507850 524156 544676 567118 569477 601716 613424
    626596 645554 664224 671401 694799 704424 708842 709409 709580 727274
    728714 744313 764652))

(defparameter *paris-dawn* (angle 18 0 0))

(defun emit (rd key val) (format t "~a ~a ~s~%" rd key val))

(dolist (rd *dates*)
  (flet ((e (key form) (let ((v (ignore-errors form))) (when v (emit rd key v)))))
    ;; p.755
    (e "WEEKDAY" (day-of-week-from-fixed rd))
    (e "JD" (jd-from-fixed rd))
    (e "MJD" (mjd-from-fixed rd))
    (e "UNIX" (round (unix-from-moment rd)))
    (e "GREGORIAN" (gregorian-from-fixed rd))
    (e "JULIAN" (julian-from-fixed rd))
    (e "ROMAN" (roman-from-fixed rd))
    (e "OLYMPIAD" (olympiad-from-julian-year (standard-year (julian-from-fixed rd))))
    (e "EGYPTIAN" (egyptian-from-fixed rd))
    (e "ARMENIAN" (armenian-from-fixed rd))
    ;; p.756
    (e "AKAN" (akan-name-from-fixed rd))
    (e "COPTIC" (coptic-from-fixed rd))
    (e "ETHIOPIC" (ethiopic-from-fixed rd))
    (e "ISO" (iso-from-fixed rd))
    (e "ICELANDIC" (icelandic-from-fixed rd))
    (e "ISLAMIC" (islamic-from-fixed rd))
    (e "OBS-ISLAMIC" (observational-islamic-from-fixed rd))
    (e "UMM-AL-QURA" (saudi-islamic-from-fixed rd))
    (e "HEBREW" (hebrew-from-fixed rd))
    (e "OBS-HEBREW" (observational-hebrew-from-fixed rd))
    ;; p.757
    (e "PERSIAN" (persian-from-fixed rd))
    (e "ARITH-PERSIAN" (arithmetic-persian-from-fixed rd))
    (e "BAHAI" (bahai-from-fixed rd))
    (e "ASTRO-BAHAI" (astro-bahai-from-fixed rd))
    (e "FRENCH" (french-from-fixed rd))
    (e "ARITH-FRENCH" (arithmetic-french-from-fixed rd))
    (e "EASTER-JUL" (gregorian-from-fixed (orthodox-easter (gregorian-year-from-fixed rd))))
    (e "EASTER-GREG" (gregorian-from-fixed (easter (gregorian-year-from-fixed rd))))
    (e "EASTER-ASTRO" (gregorian-from-fixed (astronomical-easter (gregorian-year-from-fixed rd))))
    ;; p.758
    (e "MAYAN-LC" (mayan-long-count-from-fixed rd))
    (e "MAYAN-HAAB" (mayan-haab-from-fixed rd))
    (e "MAYAN-TZOLKIN" (mayan-tzolkin-from-fixed rd))
    (e "AZTEC-XIHUITL" (aztec-xihuitl-from-fixed rd))
    (e "AZTEC-TONAL" (aztec-tonalpohualli-from-fixed rd))
    (e "BALINESE" (bali-pawukon-from-fixed rd))
    (e "BABYLONIAN" (babylonian-from-fixed rd))
    (e "SAMARITAN" (samaritan-from-fixed rd))
    ;; p.759
    (e "CHINESE" (chinese-from-fixed rd))
    (e "CHINESE-NAME" (chinese-day-name rd))
    (e "ZHONGQI" (major-solar-term-on-or-after rd))
    (e "OLD-HINDU-SOLAR" (old-hindu-solar-from-fixed rd))
    (e "HINDU-SOLAR" (hindu-solar-from-fixed rd))
    (e "ASTRO-HINDU-SOLAR" (astro-hindu-solar-from-fixed rd))
    (e "OLD-HINDU-LUNAR" (old-hindu-lunar-from-fixed rd))
    (e "HINDU-LUNAR" (hindu-lunar-from-fixed rd))
    (e "ASTRO-HINDU-LUNAR" (astro-hindu-lunar-from-fixed rd))
    (e "TIBETAN" (tibetan-from-fixed rd))
    ;; p.760
    (e "EPHEMERIS" (ephemeris-correction (+ rd 0.5d0)))
    (e "EQ-TIME" (equation-of-time (+ rd 0.5d0)))
    (e "SOLAR-LONG" (solar-longitude (+ rd 0.5d0)))
    (e "NEXT-SEASON" (min (solar-longitude-after spring rd)
                          (solar-longitude-after summer rd)
                          (solar-longitude-after autumn rd)
                          (solar-longitude-after winter rd)))
    (e "DAWN-PARIS" (dawn rd paris *paris-dawn*))
    (e "MIDDAY-TEHRAN" (midday rd tehran))
    (e "SUNSET-JERU" (sunset rd jerusalem))
    ;; p.761
    (e "LUNAR-LONG" (lunar-longitude rd))
    (e "LUNAR-LAT" (lunar-latitude rd))
    (e "LUNAR-ALT" (lunar-altitude rd mecca))
    (e "NEW-MOON" (new-moon-at-or-after rd))
    (e "MOONRISE-MECCA" (moonrise rd mecca))
    (e "MOONSET-MECCA" (moonset rd mecca))))
