import Fuzz as F
import grep_3c3bdace as Main

if __name__ == '__main__':
    F.main('./lang/grep/grammar/grammar.json', './lang/grep/bugs/grep.3c3bdace', Main.my_predicate)
