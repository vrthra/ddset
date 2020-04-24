import os
import Infra as I
import Abstract as A
from Abstract import PRes

def my_predicate(src):
    o = A.do(('sudo docker exec -it %s bash -c' % I.docker()).split(' ')  + ["echo foo foo bar > foofoobar"])
    o = I.do('grep', 'sudo docker exec -it %s bash -c' % I.docker(), "./grep13/grep/src/%s" % src, True)
    os.system("stty sane")
    out = o.stdout
    if out.strip() == 'foo foo':
        return PRes.success
    if 'Invalid back reference' in out: return PRes.invalid
    return PRes.failed

if __name__ == '__main__':
    I.main('./lang/grep/grammar/grammar.json', './lang/grep/bugs/grep.8f08d8e2', my_predicate)

