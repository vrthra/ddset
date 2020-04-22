import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('lua', './lang/lua/compilers/lua --', src)
    if o.returncode == 0: return PRes.failed
    if o.returncode == -11: return PRes.success
    out = o.stdout
    if 'Segmentation fault (core dumped)' in out:
        return PRes.success
    elif 'stack traceback' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.timeout
    return PRes.failed

import sys
if __name__ == '__main__':
    I.main('./lang/lua/grammar/lua.fbjson', './lang/lua/bugs/4.lua', my_predicate)
