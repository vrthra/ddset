import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('clojure', 'java -jar lang/clojure/compilers/clojure.jar', src)
    if o.returncode == 0: return PRes.failed
    out = o.stdout
    if 'Syntax error (VerifyError)' in out and 'Catch type is not a subclass of Throwable in exception handler 6' in out:
        return PRes.success
    elif 'Syntax error compiling' in out:
        return PRes.invalid
    #elif 'Syntax error (ClassNotFoundException)' in out:
    #    return PRes.invalid
    elif 'Illegal field name' in out:
        return PRes.invalid
    elif 'Invalid number' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.invalid
    return PRes.failed

import sys
if __name__ == '__main__':
    I.main('./lang/clojure/grammar/clojure.fbjson', './lang/clojure/bugs/clj-2345.clj', my_predicate)
