#! /usr/bin/env python3
# Chars in Mini String
# Visible Nonterminals
# Invisible Nonterminals
# Context Sensitive
# Remaining Chars
# Executions
import json
import sys
import json
import Abstract as A


def context_sensitive(tree, check=True):
    name, children, *rest = tree
    if not A.is_nt(name): return tree
    if name[0:2] == '<$':
        abs_a = rest[-1]
        assert 'sensitive' in abs_a
        abs_a['sensitive'] = check
        return (name, [context_sensitive(n, False) for n in children], *rest)
    else:
        return (name, [context_sensitive(n, True) for n in children], *rest)

def coalesce_tokens(tree):
    name, children, *rest = tree
    if not A.is_nt(name):
        return (name, children, *rest)
    elif is_token(name):
        v = A.tree_to_string(tree)
        return (name, [(v, [])], *rest)
    else:
        return (name, [coalesce_tokens(n) for n in children], *rest)


def e_sensitive(abstract_a):
    if not abstract_a:
        return True
    else:
        return abstract_a[0]['sensitive']


def is_token(val):
    assert val != '<>'
    assert (val[0], val[-1]) == ('<', '>')
    if val[1].isupper(): return True
    if val[1] == '$': return val[2].isupper() # token derived.
    return False

def top_nt(tree):
    res = []
    name, children, *general_ = tree
    if not A.is_nt(name): return [('', name)]
    v = A.tree_to_string(tree)
    if not v.strip(): return [('<>', v)] # invisible
    general = A.e_g(general_)
    if general:
        assert A.is_nt(name)
        # could be abstract
        assert name != '<>'
        #if name == '<>': return ('<>', name) # skip
        return [(name, v)]
    if A.is_token(name): return [(v, v)]
    for c in children:
        res_ = top_nt(c)
        res.extend(res_)
    return res


def chars_in_mini_string(j):
    return len(j['min_s']), j['min_s']

def nt(j):
    tree = j['abs_t']
    ctree = coalesce_tokens(tree)
    cstree = context_sensitive(ctree)
    res = top_nt(cstree)
    return res

def exec_count(fname):
    assert fname[len(fname)-len('.json'):] == '.json'
    b = fname[0:(len(fname) - len('.json'))]
    basename = b.split('/')[-1]
    a = (b + '.log.json')
    with open(a) as f:
        lines = f.readlines()
    return len(lines), basename


def table1_row(j, fname):

    e_count, basename = exec_count(fname)

    c,_s = chars_in_mini_string(j)
    v = nt(j)
    sarr = [s for name, s in v]
    s_ = ''.join(sarr)
    assert _s == s_

    all_nt = [(name,s) for name, s in v if name and A.is_nt(name)]
    visible_nt = [name for name, s in all_nt if len(name) != 2 and len(s.strip()) != 0 and name[1] != '_']
    len_visible_nt = len(visible_nt)

    context_sensitive_nt = [name for name, s in all_nt if len(name) != 2 and len(s.strip()) != 0 and name[1] == '$']
    cs_keys = set(context_sensitive_nt)
    cs_sep = {}
    for k in cs_keys:
        cs_sep[k] = len([kk for kk in context_sensitive_nt if k == kk])

    len_context_sensitive_nt = '+'.join([str(v) for k,v in cs_sep.items()]) + "=" + str(len(context_sensitive_nt))

    len_invisible = len(all_nt) - len_visible_nt

    all_t = ''.join([s for name, s in v if not name])
    len_t = len(all_t)

    return (basename, c, len_visible_nt, len_invisible, len_context_sensitive_nt, len_t, e_count)

from os import listdir
from os.path import isfile, join

def table1(args):
    rows = []
    mypath = 'results'
    if not args:
        args = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
    args = sorted(args)
    for a in args:
        if '.log.' in a: continue
        if '/fuzz_' in a: continue
        if '/reduce_' in a: continue
        with open(a) as f:
            j = json.load(fp=f)
        r = table1_row(j, a)
        rows.append(r)
    return rows

if __name__ == '__main__':
    import sys

    print('{0:>15} {1:>20} {2:>10} {3:>10} {4:>20} {5:>10} {6:>10}'.format('', 'Chars in MinString','Visible','Invisible','Context Sensitive','Remaining','Executions') )
    rows = table1(sys.argv[1:])
    for r in rows:
        print('{0:>15} {1:>20} {2:>10} {3:>10} {4:>20} {5:>10} {6:>10}'.format(*r))
        #print(','.join([str(s) for s in r]))
