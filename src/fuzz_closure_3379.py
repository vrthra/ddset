import Fuzz as F
import closure_3379 as Main

if __name__ == '__main__':
    F.main('./lang/js/grammar/javascript.fbjson', './lang/js/bugs/closure.3379.js', Main.my_predicate)

