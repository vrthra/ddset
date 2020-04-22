import Fuzz as F
import closure_3178 as Main

if __name__ == '__main__':
    F.main('./lang/js/grammar/javascript.fbjson', './lang/js/bugs/closure.3178.js', Main.my_predicate)

