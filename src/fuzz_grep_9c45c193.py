import Fuzz as F
import grep_9c45c193 as Main

if __name__ == '__main__':
    F.main('./lang/grep/grammar/grammar.json', './lang/grep/bugs/grep.9c45c193', Main.my_predicate)
