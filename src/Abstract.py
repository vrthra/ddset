USE_NT_NAME = True
TIMEOUT=60
LOOK_DEEPER_IN_ISOLATED = True

SKIP_IS_SPECIAL = True
SKIP_IS_CONCRETE = True

# The idea here is either try MAX_LIMIT number of tries
# for a counter example, or give up after `MAX_CHECKS`
# valid reproductions.
MAX_CHECKS=100
MAX_LIMIT=1000
FIND_COUNTER_EXAMPLE = True
MIN_EXAMPLES = 1

import re, copy
from enum import Enum
import sys
sys.setrecursionlimit(9000)
LOG = True
KEY = '()'
NAME = None
# Here is our failing test:
class PRes(str, Enum):
    success = 'SUCCESS'
    failed = 'FAILED'
    invalid = 'INVALID'
    timeout = 'TIMEOUT'

class St(Enum):
    unchecked = 1
    unverified = -1
    verified = 0



from Parser import EarleyParser as Parser

# ### Editable nodes
#
# We are going to want to replace a node by another. So, we want make sure that a node can be edited.

def make_editable_tree(node):
    name, children, *rest = node
    return [name, [make_editable_tree(c) for c in children]] + rest


# A helper to check if a symbol is `nonterminal`

def is_nt(symbol):
     return symbol and (symbol[0], symbol[-1]) == ('<', '>')


# Next, we define `tree_to_string()` that can convert our tree to a string.
# This string can also provide a bracketed notation for the derivation tree. A more useful feature is the `depth` parameter which essentially indicates the depth at which the `tree_to_string()` stops converting.

def tree_to_string(tree, wrap=lambda ntree, depth, name, string: string, depth=0):
    name, children, *rest = tree
    if not is_nt(name):
        return name
    else:
        return wrap(tree, depth, name, ''.join([tree_to_string(c, wrap, depth-1) for c in children]))


def general_str(tree):
    name, children, *general_ = tree
    if not is_nt(name): return name
    v = tree_to_string(tree)
    if not v.strip(): return v
    general = e_g(general_)
    if general:
        if is_nt(name):
            if name == '<>': return v
            return name
        else:
            assert not children
            return name
    res = []
    for c in children:
        x = general_str(c)
        res.append(x)
    return ''.join(res)

# ### `nt_group` groups the existing nodes in the tree in a dictionary

def nt_group(tree, all_nodes=None):
    if all_nodes is None: all_nodes = {}
    name, children, *_ = tree
    if not is_nt(name): return
    all_nodes.setdefault(name, []).append(tree)
    for c in children:
        nt_group(c, all_nodes)
    return all_nodes


# ### Count tokens in a tree

# We need a to count how many leaf nodes are there in a tree.

def count_leaves(node):
    name, children, *_ = node
    if not children:
        return 1
    return sum(count_leaves(i) for i in children)


def count_nodes(node):
    name, children, *_ = node
    if not children:
        return 0
    return sum(count_nodes(i) for i in children) + 1


# ### Fuzzer

import random

# +
class Fuzzer:
    def __init__(self, grammar):
        self.grammar = grammar

    def fuzz(self, key='<start>', max_num=None, max_depth=None):
        raise NotImplemented()

COST = None

class LimitFuzzer(Fuzzer):
    def symbol_cost(self, grammar, symbol, seen):
        if symbol in self.key_cost: return self.key_cost[symbol]
        if symbol in seen:
            self.key_cost[symbol] = float('inf')
            return float('inf')
        v = min((self.expansion_cost(grammar, rule, seen | {symbol})
                    for rule in grammar.get(symbol, [])), default=0)
        self.key_cost[symbol] = v
        return v

    def expansion_cost(self, grammar, tokens, seen):
        return max((self.symbol_cost(grammar, token, seen)
                    for token in tokens if token in grammar), default=0) + 1

    def gen_key(self, key, depth, max_depth):
        if key not in self.grammar: return key
        if depth > max_depth:
            clst = sorted([(self.cost[key][str(rule)], rule) for rule in self.grammar[key]])
            rules = [r for c,r in clst if c == clst[0][0]]
        else:
            rules = self.grammar[key]
        return self.gen_rule(random.choice(rules), depth+1, max_depth)

    def gen_rule(self, rule, depth, max_depth):
        return ''.join(self.gen_key(token, depth, max_depth) for token in rule)

    def fuzz(self, key='<start>', max_depth=10):
        return self.gen_key(key=key, depth=0, max_depth=max_depth)

    def __init__(self, grammar):
        global COST
        super().__init__(grammar)
        self.key_cost = {}
        if COST is not None:
            self.cost = COST
        else:
            COST = self.compute_cost(grammar)
            self.cost = COST

    def compute_cost(self, grammar):
        cost = {}
        for k in grammar:
            cost[k] = {}
            for rule in grammar[k]:
                cost[k][str(rule)] = self.expansion_cost(grammar, rule, set())
        return cost


# ### Path to child

# Given a tree and path to a node, return the node.

def get_child(tree, path):
    if not path: return tree
    cur, *path = path
    return get_child(tree[1][cur], path)


# ### Replace path

# Given a tree, a path to a node, and a new node to replace the node with, return a copy of the tree with the node replaced.

def replace_path2(tree, path, new_node):
    ctree = make_editable_tree(tree)
    node = get_child(ctree, path)
    sn = tree_to_string(node)
    node.clear()
    assert new_node is not None
    nn = copy.deepcopy(new_node)
    node.extend(nn)
    return ctree

def replace_path(tree, path, new_node=None):
    ctree = make_editable_tree(tree)
    node = get_child(ctree, path)
    sn = tree_to_string(node)
    node.clear()
    if new_node is not None:
        snn = tree_to_string(new_node)
        if snn == sn:
            return None
        nn = copy.deepcopy(new_node)
        node.extend(nn)
    return ctree


# We maintain a priority queue of nodes where the queue has a it s top, the node with the most number of tokens.

import heapq

# Next, we need to maintain a priority queue of the `[(tree, path)]`. The essential idea is to prioritize the items first by the number of leaves in the full tree, then next by the number of leaves in the node pointed to by path, and finally, tie break by the insertion order (`ecount`).

ecount = 0
def add_to_pq(tup, q):
    global ecount
    dtree, F_path = tup
    stree = get_child(dtree, F_path)
    n =  count_leaves(dtree)
    m =  count_leaves(stree)
    # heap smallest first
    heapq.heappush(q, (n, m, -ecount, tup))
    ecount += 1


# ### Exploration of patterns

# The exploration of patterns. We have a choice here on how we select compatible nodes. If we choose all compatible nodes of the original tree (`alt_nodes`) for a given node as replacement, even small derivation trees can produce too many alternatives. Here, we restrict ourselves to the children of the current node.

def compatible_nodes(tree, grammar):
    key, children, *_ = tree
    # Here is the first choice. Do we restrict ourselves to only children of the tree
    # or do we allow all nodes in the original tree? given in all_nodes?
    lst = nt_group(tree)
    node_lst = [(i, n) for i,n in enumerate(lst[key])]
    
    # insert empty if the grammar allows it as the first element
    if [] in grammar[key]: node_lst.insert(0, (-1, (key, [])))
    return node_lst

def e_g(abstract_a):
    if not abstract_a:
        return True
    else:
        return abstract_a[0]['abstract']

# #### Replacing an array of nodes
#
# Next, we need the ability to replace a list of nodes together with random values.

def replace_arr_with_random_values(npath_arr, grammar, tree):
    if not npath_arr: return tree
    npath, *npath_arr = npath_arr
    node = get_child(tree, npath)
    gf = LimitFuzzer(grammar)
    e = gf.fuzz(key=node[0])
    ntree = replace_path2(tree, npath, [node[0], [(e, [])]])
    assert ntree is not None
    return replace_arr_with_random_values(npath_arr, grammar, ntree)


# #### Generalize multi fault nodes
import time

def identify_concrete_paths_to_nt(gtree, path=None):
    if path is None: path = []
    name, children, *_general = gtree
    general = e_g(_general)

    # we dont care about general non terminals
    if general and is_nt(name): return []
    # we dont care about terminals either
    if not is_nt(name): return []
    if name == '<_SKIP>': return []

    my_paths = [path]
    # for tokens we do not care about things below
    if is_token(name): return my_paths

    for i, c in enumerate(children):
        ps = identify_concrete_paths_to_nt(c, path + [i])
        my_paths.extend(ps)
    return my_paths

# in finding similar nodes, we have to give first preference
# to the paths with maximum *amount* of common elements that can
# be identified on a string in terms of character count. No
# similarity analysis should be allowed on the nodes where a
# previous analysis detected similarity
def find_similar_nodes(gtree, cpaths):
    strings = {}
    for path in cpaths:
        n = get_child(gtree, path)
        s = tree_to_string(n)
        if not len(s): continue
        if USE_NT_NAME:
            key = (n[0], s)
        else:
            key = s
        strings.setdefault(key, []).append(path)
    return {s:strings[s] for s in strings if len(strings[s]) > 1}

def are_these_similar(tkey, paths, grammar, gtree, predicate, max_checks=100):
    name, string = tkey
    if len(paths) < 2: return False
    gf = LimitFuzzer(grammar)
    nchecks = 0
    seen = set()
    global KEY
    KEY = 'similar: ' + name
    for i in range(max_checks):
        v = gf.fuzz(key=name)
        if v in seen: continue
        seen.add(v)
        # now replace it in all paths
        ctree = gtree
        for p in paths:
            ctree = replace_path2(ctree, p, (name, [(v, [])]))
        res = tree_to_string(ctree)
        pr = predicate(res)
        if pr == PRes.failed:
            print(repr(v), repr(res))
            return False
        elif pr == PRes.success:
            continue
        elif pr == PRes.invalid  or pr == PRes.timeout:
            nchecks += 1

    if len(seen) <= 1: # a single
        return False

    # there has been at least one successful replacement
    return nchecks < max_checks

nsym = 0
def markup_paths(tkey, paths, gtree):
    global nsym
    nsym += 1
    name, string = tkey
    newname = '<$%s_%d>' % (name[1:-1], nsym)
    for p in paths:
        cname, children, gen = get_child(gtree, p)
        assert name == cname
        gtree = replace_path2(gtree, p, (newname, children, {'sensitive': True, 'abstract': True})) # now it is generalizable!
    return gtree

def identify_similarities(grammar, predicate, generalized_tree, max_checks=100):
    cpaths = identify_concrete_paths_to_nt(generalized_tree)
    similar_nodes = find_similar_nodes(generalized_tree, cpaths)

    for key in similar_nodes:
        res = are_these_similar(key, similar_nodes[key], grammar, generalized_tree, predicate, max_checks)
        if res and len(similar_nodes[key]) > 1:
            generalized_tree = markup_paths(key, similar_nodes[key], generalized_tree)
        print('Similar?', key, res)
    # from_paths_identify_similar
    # for each similar verify if they can be fuzzed together.
    return generalized_tree

def generate(dtree, grammar, paths):
    res = replace_arr_with_random_values([p[0] for p in paths], grammar, dtree)
    return tree_to_string(res)

def can_generalize(tval, dtree, grammar, predicate, unverified, max_checks, node):
    checks = 0
    limit = 0
    abstract = True
    rstr = None
    checks = set()
    while len(checks) < max_checks:
        limit += 1
        if limit >= MAX_LIMIT:
            # giveup.
            if FIND_COUNTER_EXAMPLE:
                if len(checks) > MIN_EXAMPLES:
                    abstract = True
                else:
                    abstract = False
            else:
                abstract = False

            print('warn: giving up', node[0], 'after', MAX_LIMIT,
                    'and no counterexample found.'
                    'invalid values with', len(checks),
                    'valid values abstract:', abstract)
            break
        rstr = generate(dtree, grammar, [tval] + unverified)
        pres = predicate(rstr)
        if pres == PRes.failed:
            abstract = False
            break
        else:
            if pres == PRes.success:
                checks.add(rstr)
            else:
                continue
    return abstract

check_counter = 0
def abstraction(tval, dtree, grammar, predicate, unverified, max_checks):
    global check_counter, KEY
    path, status = tval
    node = get_child(dtree, path)
    KEY = "%s:(%s) %s" % (node[0], tree_to_string(node), status)
    if LOG:
        print(check_counter, 'check:', node[0], status)
        check_counter += 1
    key, children, *rest = node
    if not children: return []
    if not is_nt(key): return []

    if key == '<_SKIP>' and SKIP_IS_SPECIAL:
        if SKIP_IS_CONCRETE: return []
        if status == St.unchecked:
            print('abstract: unverified', node[0])
            return [(path, St.unverified)]
        else:
            print('abstract: verified', node[0])
            return [(path, St.verified)]

    abstract = can_generalize(tval, dtree, grammar, predicate, unverified, max_checks, node)
    if abstract:
        if status == St.unchecked:
            print('abstract: unverified', node[0])
            return [(path, St.unverified)]
        else:
            print('abstract: verified', node[0])
            return [(path, St.verified)]
    else:
        if status == St.unverified:
            print('NOT ABSTRACT:', KEY)

        if is_token(key): return []
        paths = []
        # what should we do when an unverified node is found not abstract?
        # do we look at the child nodes? It can be costly, because now we
        # are also dealing with random values in other nodes marked general.
        if status == St.unchecked or LOOK_DEEPER_IN_ISOLATED:
            for i,child in enumerate(children):
                if not is_nt(child[0]): continue
                tval = (path + [i], St.unchecked)
                p = abstraction(tval, dtree, grammar, predicate, unverified, max_checks)
                paths.extend(p)
        return paths


def mark_verified_path(tree, path):
    name, children = get_child(tree, path)
    new_tree = replace_path2(tree, path, (name, children, {'abstract': True}))
    return new_tree

def mark_verified_abstract(tree, verified_paths):
    if not verified_paths: return tree
    path, *rest = verified_paths
    new_tree = mark_verified_path(tree, path)
    return mark_verified_abstract(new_tree, rest)

def mark_concrete(tree): # TODO
    name, children, *abstract_a = tree
    #if not children:
    #    return (name, [], True) # mark nonterminals as abstract
    abstract = {'abstract': False} if not abstract_a else abstract_a[0]
    return (name, [mark_concrete(c) for c in children], abstract)

gen_counter = 0
def isolation(tree, grammar, predicate, max_checks):
    global gen_counter
    unverified = [([], St.unchecked)]
    verified = []
    while unverified:
        v = unverified.pop(0)
        if LOG:
            node = get_child(tree, v[0])
            print(gen_counter, 'isolation:', node[0], v[1])
            gen_counter += 1
        newpaths = abstraction(v, tree, grammar, predicate, unverified, max_checks)
        print('current paths:')
        for p in newpaths:
            node = get_child(tree, p[0])
            print(">\t", p, "%s<%s>" % (node[0], repr(tree_to_string(node))))
        print()

        for p in newpaths:
            if p[1] == St.verified:
                verified.append(p)
            elif p[1] == St.unverified:
                unverified.append(p)
            else:
                assert false
    print('abstract paths:', len(verified))
    new_tree = mark_verified_abstract(tree, [p[0] for p in verified])
    # now change everythign else to False
    return mark_concrete(new_tree)


def get_abstraction(grammar_, my_input, predicate, max_checks=100):
    start = grammar_.get('[start]', '<start>')
    grammar = grammar_['[grammar]']
    assert start in grammar
    assert predicate(my_input) == PRes.success
    d_tree, *_ = Parser(grammar, start_symbol=start, canonical=True).parse(my_input)
    min_tree = reduction(d_tree, grammar, predicate)
    min_s = tree_to_string(min_tree)
    if LOG:
        print('reduction:', count_nodes(min_tree), count_leaves(min_tree), flush=True)
        print('min_tree:', repr(min_s), flush=True)

    dd_tree_ =  isolation(min_tree, grammar, predicate, max_checks)
    dd_tree = identify_similarities(grammar, predicate, dd_tree_, max_checks)
    s = general_str(dd_tree)
    return min_s, s, dd_tree

# # Experiments

import json
import os.path


# Coalesce tokens

def is_token(val):
    assert val != '<>'
    assert (val[0], val[-1]) == ('<', '>')
    if val[1].isupper(): return True
    #if val[1] == '_': return val[2].isupper() # token derived.
    return False


def coalesce(tree):
    name, children, *rest = tree
    if not is_nt(name):
        return (name, children, *rest)
    elif is_token(name):
        v = tree_to_string(tree)
        return (name, [(v, [])], *rest)
    else:
        return (name, [coalesce(n) for n in children], *rest)


def load_bug(bug_fn, grammar_meta):
    with open(bug_fn) as f: bug_src = f.read()
    start = grammar_meta['[start]']
    grammar = grammar_meta['[grammar]']
    parser = Parser(grammar, start_symbol=start, canonical=True) # log=True)
    forest = parser.parse(bug_src.strip())
    tree = list(forest)[0]
    return grammar_meta, coalesce(tree)


def load_parsed_bug(bug_fn, grammar_fn):
    bn = os.path.basename(bug_fn)
    parsed_fn = 'js/parsed/%s' % bn
    with open(grammar_fn) as f: grammar_meta = json.loads(f.read())
    if os.path.exists(parsed_fn):
        with open(parsed_fn) as f:
            tree = json.load(fp=f)
            return grammar_meta, coalesce(tree)
    return load_bug(bug_fn, grammar_meta)


# ## Javascript

class LimitFuzzer(LimitFuzzer):
    def fuzz(self, key='<start>', max_depth=10):
        #with open('fuzz.out.js', 'a+') as f:
        #    r = self.gen_key(key=key, depth=0, max_depth=max_depth)
        #    print(json.dumps({'key': key, 'str':r}), file=f)
        #    
        return self.gen_key(key=key, depth=0, max_depth=max_depth)
    
    def gen_key(self, key, depth, max_depth):
        assert key != '<>'
        if key not in self.grammar: return key
        if key == '<_SKIP>': return random.choice(['',' ','\n', '\t'])
        if depth > max_depth:
            clst = sorted([(self.cost[key][str(rule)], rule) for rule in self.grammar[key]])
            rules = [r for c,r in clst if c == clst[0][0]]
        else:
            rules = self.grammar[key]
        return self.gen_rule(random.choice(rules), depth+1, max_depth)


# ### Optimization for tokens

def reduction(tree, grammar, predicate):
    global KEY
    first_tuple = (tree, [])
    p_q = []
    add_to_pq(first_tuple, p_q)
    
    ostr = tree_to_string(tree)
    assert predicate(ostr) == PRes.success
    failed_set = {ostr: True}

    min_tree, min_tree_size = tree, count_leaves(tree)
    while p_q:
        # extract the tuple
        _n, _m, _ec, (dtree, F_path) = heapq.heappop(p_q)
        stree = get_child(dtree, F_path)
        skey, schildren = stree
        KEY = 'reduction:%s' % skey
        found = False
        # we now want to replace stree with alternate nodes.
        for i, node in compatible_nodes(stree, grammar):
            # replace with current (copy).
            ctree = replace_path(dtree, F_path, node)
            if ctree is None: continue # same node
            v = tree_to_string(ctree)
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


import tempfile
import subprocess
import os
import signal
import urllib
import hashlib

class O:
    def __init__(self, **keys): self.__dict__.update(keys)
    def __repr__(self): return str(self.__dict__)

def do(command, env=None, shell=False, log=False, **args):
    result = subprocess.Popen(command,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
    )
    try: 
        stdout, stderr = result.communicate(timeout=TIMEOUT)
        result.kill()
        stderr = '' if stderr is None else stderr.decode('utf-8', 'ignore')
        stdout = '' if stdout is None else stdout.decode('utf-8', 'ignore')
        return O(returncode=result.returncode, stdout=stdout, stderr=stderr)
    except subprocess.TimeoutExpired as e:
        result.kill()
        return O(returncode=255, stdout='TIMEOUT', stderr='')

