import heapq
import re
from enum import Enum
from Parser import EarleyParser as Parser
from Fuzzer import LimitFuzzer as LimitFuzzer
import random
random.seed(0)
MAX_TRIES_FOR_ABSTRACTION = 100

class PRes(str, Enum):
    success = 'SUCCESS'
    failed = 'FAILED'
    invalid = 'INVALID'
    timeout = 'TIMEOUT'

def is_nt(symbol):
    return symbol and (symbol[0], symbol[-1]) == ('<', '>')

def tree_to_str(tree):
    expanded = []
    to_expand = [tree]
    while to_expand:
        (key, children, *rest), *to_expand = to_expand
        if is_nt(key):
            #assert children # not necessary
            to_expand = list(children) + list(to_expand)
        else:
            assert not children
            expanded.append(key)
    return ''.join(expanded)

def get_child(tree, path):
    if not path: return tree
    cur, *path = path
    return get_child(tree[1][cur], path)

def replace_tree_node(node, path, newnode):
    if not path:
        assert node[0] == newnode[0], ("%s != %s") % (node[0], newnode[0])
        return newnode
    name, children, *rest = node
    hd, *subpath = path
    assert hd < len(children)
    new_children = []
    for i,c in enumerate(children):
        if i == hd:
            c_ = replace_tree_node(c, subpath, newnode)
        else:
            c_ = c
        new_children.append(c_)
    return (name, new_children, *rest)

def count_leaves(node):
    name, children, *_ = node
    if not children:
        return 1
    return sum(count_leaves(i) for i in children)

#=======================REDUCER=================================================

ECOUNT = 0
def add_to_pq(tup, q):
    global ECOUNT
    dtree, F_path = tup
    stree = get_child(dtree, F_path)
    n =  count_leaves(dtree)
    m =  count_leaves(stree)
    # heap smallest first
    heapq.heappush(q, (n, m, -ECOUNT, tup))
    ECOUNT += 1

def nt_group(tree, all_nodes=None):
    if all_nodes is None: all_nodes = {}
    name, children, *_ = tree
    if not is_nt(name): return
    all_nodes.setdefault(name, []).append(tree)
    for c in children:
        nt_group(c, all_nodes)
    return all_nodes

def compatible_nodes(tree, grammar):
    key, children, *_ = tree
    # Here is the first choice. Do we restrict ourselves to only children of the tree
    # or do we allow all nodes in the original tree? given in all_nodes?
    lst = nt_group(tree)
    node_lst = [(i, n) for i,n in enumerate(lst[key])]

    # insert empty if the grammar allows it as the first element
    if [] in grammar[key]: node_lst.insert(0, (-1, (key, [])))
    return node_lst

def is_token(val):
    assert val != '<>'
    assert (val[0], val[-1]) == ('<', '>')
    if val[1].isupper(): return True
    #if val[1] == '_': return val[2].isupper() # token derived.
    return False

def reduction(tree, grammar, predicate):
    first_tuple = (tree, [])
    p_q = []
    add_to_pq(first_tuple, p_q)

    ostr = tree_to_str(tree)
    assert predicate(ostr) == PRes.success
    failed_set = {ostr: True}

    min_tree, min_tree_size = tree, count_leaves(tree)
    while p_q:
        # extract the tuple
        _n, _m, _ec, (dtree, F_path) = heapq.heappop(p_q)
        stree = get_child(dtree, F_path)
        skey, schildren = stree
        found = False
        # we now want to replace stree with alternate nodes.
        for i, node in compatible_nodes(stree, grammar):
            # replace with current (copy).
            ctree = replace_tree_node(dtree, F_path, node)
            if ctree is None: continue # same node
            v = tree_to_str(ctree)
            if v in failed_set: continue
            failed_set[v] = predicate(v) # we ignore PRes.invalid results
            if failed_set[v] == PRes.success:
                found = True
                ctree_size = count_leaves(ctree)
                if ctree_size < min_tree_size: min_tree, min_tree_size = ctree, ctree_size

                if v not in failed_set:
                    print(v)
                t = (ctree, F_path)
                assert get_child(ctree, F_path) is not None
                add_to_pq(t, p_q)

        # The CHOICE here is that we explore the children if and only if we fail
        # to find a node that can replace the current
        if found: continue
        if is_token(skey): continue # do not follow children TOKEN optimization
        for i, child in enumerate(schildren):
            if not is_nt(child[0]): continue
            assert get_child(tree=dtree, path=F_path + [i]) is not None
            t = (dtree, F_path + [i])
            add_to_pq(t, p_q)
    return min_tree

#=======================GENERALIZER=============================================

def generalize(tree, path, known_paths, grammar, predicate):
    node = get_child(tree, path)
    if not is_nt(node[0]): return known_paths
    if can_abstract(tree, path, known_paths, grammar, predicate):
        known_paths.append(path)
        return known_paths
    for i,child in enumerate(node[1]):
        ps = generalize(tree, path + [i], known_paths, grammar, predicate)
    return known_paths

def can_abstract(tree, path, known_paths, grammar, predicate):
    i = 0
    while (i < MAX_TRIES_FOR_ABSTRACTION):
        t = replace_all_paths_with_generated_values(tree, known_paths + [path], grammar)
        s = tree_to_str(t)
        if predicate(s) == PRes.failed:
            return False
        elif predicate(s) == PRes.invalid:
            continue
        i += 1
    return True

def replace_all_paths_with_generated_values(tree, paths, grammar):
    my_tree = tree
    for p in paths:
        my_tree = replace_path_with_generated_value(my_tree, p, grammar)
    return my_tree

def replace_path_with_generated_value(tree, path, grammar):
    node = get_child(tree, path)
    s, gnode = generate_random_value(grammar, node[0])
    t = replace_tree_node(tree, path, gnode)
    return t

# Given a key, generate a random value for that key using the grammar. 
def generate_random_value(grammar, key):
    fuzzer = LimitFuzzer(grammar)
    s = fuzzer.fuzz(key)
    return (s, fuzzer._s)


def tree_to_str_a(tree):
    name, children, *general_ = tree
    if not is_nt(name): return name
    if is_node_abstract(tree):
        return name
    return ''.join([tree_to_str_a(c) for c in children])


def mark_concrete_r(tree):
    name, children, *abstract_a = tree
    abstract = {'abstract': False} if not abstract_a else abstract_a[0]
    return (name, [mark_concrete_r(c) for c in children], abstract)


def mark_path_abstract(tree, path):
    name, children = get_child(tree, path)
    new_tree = replace_tree_node(tree, path, (name, children, {'abstract': True}))
    return new_tree

def get_abstract_tree(tree, paths):
    for path in paths:
        tree = mark_path_abstract(tree, path)
    return mark_concrete_r(tree)

def is_node_abstract(node):
    name, children, *abstract_a = node
    if not abstract_a:
        return True
    else:
        return abstract_a[0]['abstract']

#=======================GENERATOR===============================================

def abstract_to_concrete(abstract_tree, grammar):
    if is_node_abstract(abstract_tree):
        s, t = generate_random_value(grammar, abstract_tree[0])
        return t
    res = []
    for child in abstract_tree[1]:
        t = abstract_to_concrete(child, grammar)
        res.append(t)
    return (abstract_tree[0], res)

def generate_testcase(abstract_tree, grammar):
    tv = abstract_to_concrete(abstract_tree, grammar)
    s = tree_to_str(tv)
    return s

#=======================DRIVER===============================================

EXPR_GRAMMAR = {'<start>': [['<expr>']],
 '<expr>': [['<term>', ' + ', '<expr>'],
  ['<term>', ' - ', '<expr>'],
  ['<term>']],
 '<term>': [['<factor>', ' * ', '<term>'],
  ['<factor>', ' / ', '<term>'],
  ['<factor>']],
 '<factor>': [['+', '<factor>'],
  ['-', '<factor>'],
  ['(', '<expr>', ')'],
  ['<integer>', '.', '<integer>'],
  ['<integer>']],
 '<integer>': [['<digit>', '<integer>'], ['<digit>']],
 '<digit>': [['0'], ['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7'], ['8'], ['9']]}

def expr_double_paren(inp):
    if re.match(r'.*[(][(].*[)][)].*', inp):
        return PRes.success
    return PRes.failed


my_input = '1 + ((2 * 3 / 4))'
expr_parser = Parser(EXPR_GRAMMAR, start_symbol='<start>', canonical=True)
parsed_expr = list(expr_parser.parse(my_input))[0]
er = reduction(parsed_expr, EXPR_GRAMMAR, expr_double_paren)


vals = generalize(er, [], [], EXPR_GRAMMAR, expr_double_paren)
ta = get_abstract_tree(er, vals)
s = tree_to_str_a(ta)
print(s)
for i in range(10):
    v = generate_testcase(ta, EXPR_GRAMMAR)
    print(v)
print()
print()
def expr_multiply(inp):
    if re.match(r'.*[*].*', inp):
        return PRes.success
    return PRes.failed

er = reduction(parsed_expr, EXPR_GRAMMAR, expr_multiply)

vals = generalize(er, [], [], EXPR_GRAMMAR, expr_multiply)
ta = get_abstract_tree(er, vals)
s = tree_to_str_a(ta)
print(s)
for i in range(10):
    v = generate_testcase(ta, EXPR_GRAMMAR)
    print(v)

