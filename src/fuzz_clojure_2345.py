import Fuzz as F
import clojure_2345 as Main

import sys
if __name__ == '__main__':
    F.main('./lang/clojure/grammar/clojure.fbjson', './lang/clojure/bugs/clj-2345.clj', Main.my_predicate)
