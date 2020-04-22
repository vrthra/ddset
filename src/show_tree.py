import ftree as T
import Abstract as A

import json
import sys


def coalesce(tree):
    name, children, *rest = tree
    if not A.is_nt(name):
        return (name, children, *rest)
    elif is_token(name):
        v = A.tree_to_string(tree)
        return (name, [(v, [])], *rest)
    else:
        return (name, [coalesce(n) for n in children], *rest)

def is_token(val):
    assert val != '<>'
    assert (val[0], val[-1]) == ('<', '>')
    if val[1].isupper(): return True
    if val[1] == '$': return val[2].isupper() # token derived.
    return False

def color_format_node(x):
    if len(x)== 3:
        return ((T.Colors.CRED2 + repr(x[0]) + T.Colors.ENDC) if x[-1]['abstract'] else repr(x[0]))
    else:
        return repr(x[0])

def format_node(x):
    if len(x)== 3:
        return ('(*)' + repr(x[0])) if x[-1]['abstract'] else repr(x[0])
    else:
        return repr(x[0])

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        res = json.load(fp=f)
        print(res['min_s'])
        print(res['abs_s'])
        print(A.general_str(res['abs_t']))
        abs_t = coalesce(res['abs_t'])

        if len(sys.argv) > 2:
            if sys.argv[2] == '-c':
                print(T.format_tree(abs_t,format_node=color_format_node, get_children=lambda x: x[1]))
            elif sys.argv[2] == '-t':
                print(json.dumps(coalesce(res['abs_t']), indent=4))
        else:
            print(T.format_tree(abs_t,format_node=format_node, get_children=lambda x: x[1]))

