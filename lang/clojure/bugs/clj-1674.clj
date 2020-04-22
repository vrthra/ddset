(defn ^boolean foo-bar?
  [node]
  (= node "foo-bar"))

(defn ^boolean bar-foo?
  [node]
  (= node "bar-foo"))

(defn ^boolean interesting?
  [node]
  (or (foo-bar? node) (bar-foo? node)))

(println "Foo-Bar?" (foo-bar? "baz"))
