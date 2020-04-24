import os
import Infra as I
from Abstract import PRes

def my_predicate(src):
    #sudo docker exec -it 67b83251cecf bash -c "./find7/find/src/find --files-with-matches --recursive --exclude-dir=foo NEEDLE \$HOME "
    o = I.do('find', 'sudo docker exec -it %s bash -c' % I.docker(), I.find() + "/find/find/%s" % src, True)
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
        # timeout should be failed.
        return PRes.failed
    return PRes.failed

if __name__ == '__main__':
    I.main('./lang/find/grammar/grammar.json', './lang/find/bugs/find.93623752', my_predicate)
