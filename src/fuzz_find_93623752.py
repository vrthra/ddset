import Fuzz as F
import find_93623752 as Main

if __name__ == '__main__':
    F.main('./lang/find/grammar/grammar.json', './lang/find/bugs/find.93623752', Main.my_predicate)
