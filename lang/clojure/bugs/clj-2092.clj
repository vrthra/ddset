(deftype T [^:unsynchronized-mutable t])
(T. :t)
(eval (T. :t))
