import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('clojure', 'java -jar lang/clojure/compilers/clojure.jar', src)
    if o.returncode == 0: return PRes.failed
    out = o.stdout
    if 'Syntax error (IllegalArgumentException)' in out and 'No matching field found:' in out:
        return PRes.success
    elif 'Syntax error compiling' in out:
        return PRes.invalid
    elif 'Illegal field name' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.invalid
    return PRes.failed

import sys
if __name__ == '__main__':
    I.main('./lang/clojure/grammar/clojure.fbjson', './lang/clojure/bugs/clj-2092.clj', my_predicate)
