import os
import Infra as I
from Abstract import PRes

def my_predicate(src):
    o = I.do('grep', 'sudo docker exec -it %s bash -c' % I.docker(), I.grep() + "/grep/src/%s" % src, True)
    os.system("stty sane")
    out = o.stdout
    if not out.strip(): return PRes.success
    if 'Invalid back reference' in out: return PRes.invalid
    return PRes.failed

if __name__ == '__main__':
    I.main('./lang/grep/grammar/grammar.json', './lang/grep/bugs/grep.9c45c193', my_predicate)

