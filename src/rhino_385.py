import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('rhino', 'java -jar ./lang/js/compilers/rhino-1.7.7.2.jar', src)
    if o.returncode == 0: return PRes.failed
    out = o.stdout
    if 'java.lang.IllegalStateException' in out:
        return PRes.success
    elif 'syntax error' in out:
        return PRes.invalid
    elif 'syntax errors' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.invalid
    return PRes.failed

import sys
if __name__ == '__main__':
    I.main('./lang/js/grammar/javascript.fbjson', './lang/js/bugs/rhino.385.js', my_predicate)
