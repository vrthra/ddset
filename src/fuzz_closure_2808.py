import Fuzz as F
import closure_2808 as Main

if __name__ == '__main__':
    F.main('./lang/js/grammar/javascript.fbjson', './lang/js/bugs/closure.2808.js', Main.my_predicate)
