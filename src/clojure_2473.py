import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('clojure', 'java -jar lang/clojure/compilers/clojure.jar', src)
    if o.returncode == 0: return PRes.failed
    out = o.stdout
    if 'Syntax error macroexpanding clojure.core/let' in out and \
        "simple-symbol? at: [:bindings :form :map-destructure :map-binding 0 :local-symbol] spec: :clojure.core.specs.alpha/local-name" in out and \
        ":user/keys - failed: simple-symbol? at: [:bindings :form :map-destructure :map-binding 0 :local-symbol] spec: :clojure.core.specs.alpha/local-name" in out:
        return PRes.success
    elif 'Syntax error compiling' in out:
        return PRes.invalid
    elif 'Syntax error reading source' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.invalid
    return PRes.failed

import sys
if __name__ == '__main__':
    I.main('./lang/clojure/grammar/clojure.fbjson', './lang/clojure/bugs/clj-2473.clj', my_predicate)
