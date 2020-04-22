; Clojure 1.11.0-master-SNAPSHOT
(try
  (loop [] 
    (try "string and number literals blow this up" 
      (catch Throwable e)))
  "remove this second try call and it works")



