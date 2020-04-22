(def rs (range 3))
(def vs (seq (vector-of :int 0 1 2)))
rs
vs
(.equals rs vs)
(.equals vs rs)    ;; expect: true
(.equiv rs vs)
(.equiv vs rs)
(.hashCode rs)
(.hashCode vs)     ;; expect to match (.hashCode rs)
(System/identityHashCode vs)  ;; show that we're just getting Object hashCode
(.hasheq rs)
(.hasheq vs)       ;; expect same as (.hasheq rs) but not implemented at all
