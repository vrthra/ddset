# Copyright (c) 2015 Jonathan M. Lange <jml@mumak.net>
# LICENSE: http://www.apache.org/licenses/LICENSE-2.0
# Modified to suite my needs.

import itertools


class Colors:

    CBLACK  = '\33[30m'
    CRED    = '\33[31m'
    CGREEN  = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE   = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE  = '\33[36m'
    CWHITE  = '\33[37m'

    CBLACKBG  = '\33[40m'
    CREDBG    = '\33[41m'
    CGREENBG  = '\33[42m'
    CYELLOWBG = '\33[43m'
    CBLUEBG   = '\33[44m'
    CVIOLETBG = '\33[45m'
    CBEIGEBG  = '\33[46m'
    CWHITEBG  = '\33[47m'

    CGREY    = '\33[90m'
    CRED2    = '\33[91m'
    CGREEN2  = '\33[92m'
    CYELLOW2 = '\33[93m'
    CBLUE2   = '\33[94m'
    CVIOLET2 = '\33[95m'
    CBEIGE2  = '\33[96m'
    CWHITE2  = '\33[97m'

    CGREYBG    = '\33[100m'
    CREDBG2    = '\33[101m'
    CGREENBG2  = '\33[102m'
    CYELLOWBG2 = '\33[103m'
    CBLUEBG2   = '\33[104m'
    CVIOLETBG2 = '\33[105m'
    CBEIGEBG2  = '\33[106m'
    CWHITEBG2  = '\33[107m'

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

class O:
    def __init__(self, **keys): self.__dict__.update(keys)
    def __repr__(self): return str(self.__dict__)

GRAPHIC_OPTIONS = O(F=u'\u251c', L=u'\u2514', V=u'\u2502', H=u'\u2500', NL=u'\u23ce')
ASCII_OPTIONS   = O(F=u'|', L=u'+', V=u'|', H=u'-', NL=u'\n')

def _format_newlines(prefix, formatted_node, options):
    replacement = u''.join([options.NL, u'\n', prefix])
    return formatted_node.replace(u'\n', replacement)

def _format_tree(node, format_node, get_children, options, prefix=u''):
    children = list(get_children(node))
    next_prefix = u''.join([prefix, options.V, u'   '])
    for child in children[:-1]:
        fml = _format_newlines(next_prefix, format_node(child), options)
        yield u''.join([prefix, options.F, options.H, options.H, u' ', fml])
        tree = _format_tree(child, format_node, get_children, options, next_prefix)
        for result in tree:
            yield result
    if children:
        last_prefix = u''.join([prefix, u'    '])
        fml = _format_newlines(last_prefix, format_node(children[-1]), options)
        yield u''.join([prefix, options.L, options.H, options.H, u' ', fml])
        tree = _format_tree(children[-1], format_node, get_children, options, last_prefix)
        for result in tree:
            yield result

def format_tree(node, format_node, get_children, options=GRAPHIC_OPTIONS, special=None):
    lines = itertools.chain( [format_node(node)], _format_tree(node, format_node, get_children, options), [u''],)
    if special is not None:
        lines = [special(l) for l in lines]
    return u'\n'.join(lines)

if __name__ == '__main__':
    import sys
    import json
    jsonfn = sys.argv[1]
    with open(jsonfn) as f:
        jsont = json.load(f)
    trees = range(len(jsont))
    if len(sys.argv) > 2:
        trees = [int(v) for v in sys.argv[2:]]
    for tree in trees:
        print(format_tree(jsont[tree]['tree'], format_node=lambda x: repr(x[0]), get_children=lambda x: x[1]))
