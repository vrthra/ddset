import Abstract as A
import Infra as I
import random
import os
import json

MAX_LIMIT = 10000

def find_covarying_paths(tree, path):
    name, children, *general_ = tree
    general = A.e_g(general_)
    v = A.tree_to_string(tree).strip()
    if name.startswith('<$'):
        v = name[2:-1]
        i = v.rindex('_')
        oname = "<%s>" % v[:i]
        if oname:
            return [(oname, name, path)]
        else:
            return []
    if not A.is_nt(name): return []
    if A.is_token(name): return []
    if general: return []
    paths = []
    for i,c in enumerate(children):
        p = find_covarying_paths(c, path + [i])
        paths.extend(p)
    return paths

def find_abstract_paths(tree, path):
    name, children, *general_ = tree
    general = A.e_g(general_)
    if not A.is_nt(name): return []
    if general: return [path]
    #if A.is_token(name): return []
    paths = []
    for i,c in enumerate(children):
        p = find_abstract_paths(c, path + [i])
        paths.extend(p)
    return paths

def fuzz_tree(mgrammar, tree):
    start = mgrammar['[start]']
    grammar = mgrammar['[grammar]']
    paths = find_abstract_paths(tree, [])
    cpaths = find_covarying_paths(tree, [])
    if len(paths + cpaths) == 0: return 'No abstract paths'
    print('# abstract paths', len(paths + cpaths))
    gf = A.LimitFuzzer(grammar)
    results = []
    for i in range(MAX_LIMIT):
        abs_path_ = random.choice(paths + cpaths)
        if isinstance(abs_path_, tuple):
            name, fname, abs_path = abs_path_
            #node = A.get_child(tree, abs_path)
            #_, children, *rest = node
            all_paths = [p for n,f,p in cpaths if f == fname]
            e = gf.fuzz(key=name)
            ntree = tree
            for p in all_paths:
                ntree = A.replace_path2(ntree, p, (name, [(e, [])]))
            results.append(A.tree_to_string(ntree))
        else:
            abs_path = abs_path_
            node = A.get_child(tree, abs_path)
            name, children, *rest = node
            e = gf.fuzz(key=name)
            res = A.replace_path2(tree, abs_path, (name, [(e, [])]))
            results.append(A.tree_to_string(res))
    return list(set(results))


def main(gf_fbjson, bug_fn, pred, results_dir='fuzzing', max_checks=A.MAX_CHECKS):
    meta, tree, name = I.load_grammar(gf_fbjson, bug_fn, pred)
    global MY_PREDICATE
    os.system('mkdir -p %s' % results_dir)
    I.LOG_NAME = "./%s/%s.log.json" % (results_dir, name)
    A.NAME = name
    os.system('rm -f %s' % I.LOG_NAME)

    A.KEY = 'test'
    assert I._predicate(A.tree_to_string(tree)) == A.PRes.success
    assert I._predicate('') == A.PRes.failed

    A.KEY = 'fuzz'
    with open('./results/%s.json' % os.path.basename(bug_fn)) as f:
        j = json.load(fp=f)
        min_s = j['min_s']
        abs_s = j['abs_s']
        abs_t = j['abs_t']

    fuzz_vals = fuzz_tree(meta, abs_t)
    FUZZ_LIMIT = 100
    if len(fuzz_vals) > FUZZ_LIMIT:
        fuzz_vals = random.sample(fuzz_vals, FUZZ_LIMIT)
    print(len(fuzz_vals))
    results = []
    for f in fuzz_vals:
        r = I._predicate(f)
        print(r, repr(f))
        results.append(r)

    print('Total:', len(results))
    print('Valid:', len([r for r in  results if r != A.PRes.invalid]))
    print('Success:', len([r for r in  results if r == A.PRes.success]))

