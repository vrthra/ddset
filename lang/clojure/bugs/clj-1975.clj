; not worky
(require '[clojure.spec :as s])
(defrecord Box [a])
(s/conform
        (s/cat :boxes (s/* #(instance? Box %))
               :name (s/coll-of integer?))
        [(Box. 0) [5]])
