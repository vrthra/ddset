import Fuzz as F
import rhino_385 as Main

import sys
if __name__ == '__main__':
    F.main('./lang/js/grammar/javascript.fbjson', './lang/js/bugs/rhino.385.js', Main.my_predicate)
