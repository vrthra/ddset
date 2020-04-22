; not worky
(require '[clojure.spec :as s])
(s/conform (s/+ (s/? any?)) [:a])
