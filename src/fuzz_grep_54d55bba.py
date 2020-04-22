import Fuzz as F
import grep_54d55bba as Main

if __name__ == '__main__':
    F.main('./lang/grep/grammar/grammar.json', './lang/grep/bugs/grep.54d55bba', Main.my_predicate)
