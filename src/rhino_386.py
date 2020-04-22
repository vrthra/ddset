import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('rhino', 'java -jar lang/js/compilers/rhino-1.7.7.2.jar', src)
    if o.returncode == 0: return PRes.failed
    if o.returncode == -11: return PRes.success
    out = o.stdout
    if 'java.lang.NullPointerException' in out:
        return PRes.success
    elif 'ERROR - Parse error' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.invalid
    return PRes.failed


import sys
if __name__ == '__main__':
    I.main('./lang/js/grammar/javascript.fbjson', './lang/js/bugs/rhino.386.js', my_predicate)
