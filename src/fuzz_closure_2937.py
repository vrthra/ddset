import Fuzz as F
import closure_2937 as Main

if __name__ == '__main__':
    F.main('./lang/js/grammar/javascript.fbjson', './lang/js/bugs/closure.2937.js', Main.my_predicate)
