import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('closure', 'java -jar lang/js/compilers/closure-compiler-v20171203.jar', src)
    if o.returncode == 0: return PRes.failed
    out = o.stdout
    if 'java.lang.RuntimeException: INTERNAL COMPILER ERROR.' in out:
        return PRes.success
    elif 'ERROR - Parse error' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.invalid
    return PRes.failed

import sys
if __name__ == '__main__':
    I.main('./lang/js/grammar/javascript.fbjson', './lang/js/bugs/closure.3178.js', my_predicate)
