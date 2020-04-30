#!/usr/bin/env python3
import ftree as T
import Abstract as A

import json
import sys
import os


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
        if x[-1]['abstract']:
            if x[0][0:2] == '<$':
                if x[-1]['sensitive']:
                    return (T.Colors.CRED2 + repr(x[0]) + T.Colors.ENDC)
                else:
                    return (T.Colors.CBLUE2 + repr(x[0]) + T.Colors.ENDC)
            else:
                return (T.Colors.CGREEN2 + repr(x[0]) + T.Colors.ENDC)
        else:
            return repr(x[0])
    else:
        return repr(x[0])

SPECIAL = '(*)'
def format_node(x):
    if len(x)== 3:
        return (SPECIAL + repr(x[0])) if x[-1]['abstract'] else repr(x[0])
    else:
        return repr(x[0])

def context(tree, check=True):
    name, children, *rest = tree
    if not A.is_nt(name): return tree
    if name[0:2] == '<$':
        rest[-1]['sensitive'] = check
        return (name, [context(n, False) for n in children], *rest)
    else:
        return (name, [context(n, True) for n in children], *rest)

def markup(line):
    if SPECIAL in line:
        return '>' + line[1:]
    else:
        return line

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        res = json.load(fp=f)
        abs_t = context(coalesce(res['abs_t']))
        #xt = os.getenv('TERM')
        #if 'xterm' in xt:
        #    opt = T.GRAPHIC_OPTIONS
        #else:
        #    opt = T.ASCII_OPTIONS

        if len(sys.argv) > 2:
            if sys.argv[2] == '-tree':

                print('min:', repr(res['min_s']))
                print('abs:', repr(res['abs_s']))
                print()
                print(T.format_tree(abs_t,format_node=color_format_node, get_children=lambda x: x[1], options=T.GRAPHIC_OPTIONS))
            elif sys.argv[2] == '-json':
                print(json.dumps(abs_t, indent=4))
            elif sys.argv[2] == '-minstring':
                print('Min String:', repr(res['min_s']))
                print('Chars in Min String:', len(res['min_s']))
                print('Abstracted:', repr(res['abs_s']))
        else:
            print(T.format_tree(abs_t,format_node=format_node, get_children=lambda x: x[1], options=T.ASCII_OPTIONS, special=markup))

