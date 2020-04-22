import Fuzz as F
import lua_5_3_5__4 as Main

import sys
if __name__ == '__main__':
    F.main('./lang/lua/grammar/lua.fbjson', './lang/lua/bugs/4.lua', Main.my_predicate)
