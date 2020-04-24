#!/usr/bin/env python
import json
import sys

def load_lines(fname):
    assert fname[len(fname)-len('.json'):] == '.json'
    b = fname[0:(len(fname) - len('.json'))]
    basename = b.split('/')[-1]
    arr = []
    with open(fname) as f:
        lines = f.readlines()
    for l in lines:
        arr.append(json.loads(l))
    return arr, basename


def table2_row(fname):
    arr, basename = load_lines(fname)
    len_total = len(arr)
    valid = [a for a in arr if a['res'] != 'PRes.invalid']
    fail = [a for a in valid if a['res'] == 'PRes.success']
    return (basename[0:-len('.log')], len(valid)*100.0/len_total, len(fail)*100.0/len(valid))

def table2(args):
    rows = []
    for a in args:
        r = table2_row(a)
        rows.append(r)
    return rows

if __name__ == '__main__':
    import sys
    print('{0:>20} {1:>20} {2:>10}'.format('', 'Valid%','FAIL%') )
    rows = table2(sys.argv[1:])
    for r in rows:
        print('{0:>20} {1:>20.2f} {2:>10.2f}'.format(*r))
