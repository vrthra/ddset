import Abstract as A
import os
import json
import tempfile
import hashlib
g_predicate = {}
LOG_NAME = None
MY_PREDICATE = None
SAVE_EXEC = False

DOCKER = None
def docker():
    return DOCKER
    # `docker ps --filter  name=c8491c11  -q`

def extract(o):
    s = o.stdout.strip()
    return "./" +  s.split('/')[1]

def find():
    o = A.do(('sudo docker exec -it %s bash -c'% docker()).split(' ') + ['find . | grep %s' % docker()])
    return extract(o)

def grep():
    o = A.do(('sudo docker exec -it %s bash -c' % docker()).split(' ') + ['find . | grep %s' % docker()])
    return extract(o)

def do(prefix, cmd, src, as_string=False):
    o = None
    if as_string:
        o = A.do(cmd.split(' ') + [src])
    else:
        with tempfile.NamedTemporaryFile(prefix=prefix) as tmp:
            tname = tmp.name
            tmp.write(src.encode('UTF-8'))
            tmp.flush()
            o = A.do(cmd.split(' ') + [tname])
    hname = hashlib.sha1(src.encode('UTF-8')).hexdigest()
    if SAVE_EXEC:
        with open('.db/exec.%s' % hname, 'w+') as f:
            print(json.dumps( {'cmd': cmd,
                'src': src,
                'return': o.returncode,
                'stdout': o.stdout,
                'stderr': o.stderr} ), file=f)
    return o

def _predicate(src):
    if src in g_predicate: return A.PRes(g_predicate[src])
    res = MY_PREDICATE(src)
    g_predicate[src] = res.value
    with open(LOG_NAME, 'a+') as f:
        print(json.dumps({'res': str(res), 'key':A.KEY, 'src':src}), file=f)
    return res


def load_grammar(gf_fbjson, bug_fn, pred):
    global MY_PREDICATE
    MY_PREDICATE = pred
    grammar_fn = gf_fbjson
    meta, tree = A.load_parsed_bug(bug_fn, grammar_fn)
    name = os.path.basename(bug_fn)

    return meta, tree, name

def try_load(name):
    fname = ".db/%s" % name
    if not os.path.exists(fname): return
    with open(fname) as f:
        g_predicate.update(**json.load(fp=f))

def save(name):
    fname = ".db/%s" % name
    with open(fname, 'w+') as f:
        json.dump(g_predicate, fp=f)

def main(gf_fbjson, bug_fn, pred, results_dir='results', max_checks=A.MAX_CHECKS):
    global DOCKER
    DOCKER = bug_fn.split('.')[-1]
    os.system('mkdir -p .db/')
    meta, tree, name = load_grammar(gf_fbjson, bug_fn, pred)
    global LOG_NAME, MY_PREDICATE
    os.system('mkdir -p %s' % results_dir)
    LOG_NAME = "./%s/%s.log.json" % (results_dir, name)
    A.NAME = name
    os.system('rm -f %s' % LOG_NAME)

    try_load(name)

    assert _predicate(A.tree_to_string(tree)) == A.PRes.success
    #assert _predicate('') == A.PRes.failed

    min_s, abs_s, a_mintree = A.get_abstraction(meta,
                               A.tree_to_string(tree),
                               _predicate,
                               max_checks)
    print("min:", repr(min_s))
    print("abs:", repr(abs_s))
    save(name)

    with open('./%s/%s.json' % (results_dir, A.NAME), 'w+') as f:
        print(json.dumps({'min_s': min_s, 'abs_s': abs_s, 'abs_t': a_mintree}, indent=4), file=f)
