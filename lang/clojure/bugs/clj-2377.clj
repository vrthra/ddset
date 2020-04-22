(require '[clojure.spec.alpha :as s])

(s/def ::m (s/keys :req [::coll]))
(s/def ::coll (s/cat :m (s/? ::m)))

(s/conform ::m {::coll []})  ; => #:user{:coll {}}
(s/exercise ::m)  ; => StackOverflowError
