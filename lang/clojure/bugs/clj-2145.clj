;; THIS OOMs
(defn test1 [x]
  (if true
    (do
      (try (doseq [_ x] _))
      1)
    0))

(test1 (take 100000000 (range)))
