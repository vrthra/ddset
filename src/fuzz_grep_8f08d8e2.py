import Fuzz as F
import grep_8f08d8e2 as Main

if __name__ == '__main__':
    F.main('./lang/grep/grammar/grammar.json', './lang/grep/bugs/grep.8f08d8e2', Main.my_predicate)
