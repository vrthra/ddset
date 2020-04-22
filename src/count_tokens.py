import sys
import json
import Abstract as A

def general_str(tree):
    name, children, *general_ = tree
    if not A.is_nt(name): return name
    v = A.tree_to_string(tree)
    if not v.strip(): return v
    general = A.e_g(general_)
    if general:
        if A.is_nt(name):
            if name == '<>': return v
            return name
        else:
            assert not children
            return name
    if A.is_token(name): return v
        # we should not go below a token that is concrete 
    res = []
    for c in children:
        x = general_str(c)
        res.append(x)
    return ''.join(res)

def general_count(tree):
    name, children, *general_ = tree
    if not A.is_nt(name): return len(name)
    v = A.tree_to_string(tree)
    if not v.strip(): return len(v)
    general = A.e_g(general_)
    # if general, if a terminal, count the chars
    if general:
        if A.is_nt(name):
            if name == '<>': return 0
            return 1
        else:
            assert not children
            return len(name)
    if A.is_token(name): return len(v)
    res = 0
    for c in children:
        x = general_count(c)
        res += x
    return res


def general_count_x(tree): # return (#tokens, #chars)
    name, children, *general_ = tree
    if not A.is_nt(name): return (0, len(name))
    v = A.tree_to_string(tree)
    if not v.strip(): return (0, len(v))
    general = A.e_g(general_)
    # if general, if a terminal, count the chars
    if general:
        if A.is_nt(name):
            if name == '<>': return (0, 0)
            return (1, 0)
        else:
            assert not children
            return (0, len(name))
    if A.is_token(name): return (0, len(v))
    ts = 0
    res = 0
    for c in children:
        t, x = general_count_x(c)
        res += x
        ts += t
    return (ts, res)

def main(jfile):
    with open(jfile) as f:
        jh = json.load(fp=f)
    print('char count:', len(jh['min_s']), repr(jh['min_s']))
    # print(jh['abs_s'])
    print('char count:', general_count_x(jh['abs_t']), repr(general_str(jh['abs_t'])))


if __name__ == '__main__':
    main(*sys.argv[1:])
