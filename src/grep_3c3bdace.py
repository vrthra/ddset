import os
import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('grep', 'sudo docker exec -it %s bash -c' % I.docker(), I.grep() + "/grep/src/%s" % src, True)
    os.system("stty sane")
    out = o.stdout
    if o.returncode == 139: return PRes.success
    if 'Invalid back reference' in out: return PRes.invalid
    return PRes.failed
    if not out.strip():
        return PRes.success
    elif 'ERROR - Parse error' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.timeout
    return PRes.failed

if __name__ == '__main__':
    I.main('./lang/grep/grammar/grammar.json', './lang/grep/bugs/grep.3c3bdace', my_predicate)
