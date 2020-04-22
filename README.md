# DDSet

Replication package for _Abstracting Failure Inducing Inputs_

## Usage

Execute this command:

```
$ make all_lua
```

This will generate `results/4.lua.json`. Within this file, execute this command
to determine the number of chars in the minimum input
Given in Table 1, (lua-5.3.5.4, # Chars in Min String)

```
$ cat results/4.lua.json|  python -c 'import sys, json; print(json.load(sys.stdin)["min_s"], end="")' | wc -c
83
```
