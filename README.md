# DDSet

Replication package for _Abstracting Failure Inducing Inputs_

## Prerequisites

### RAM

All experiments done on a system with 15 GB RAM.

### Software

All executables are compiled and linked in Linux Mint 19.2

```
$ uname -rvmpio
4.15.0-91-generic #92-Ubuntu SMP Fri Feb 28 11:09:48 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux

$ lsb_release -d
No LSB modules are available.
Description:    Linux Mint 19.2 Tina
```

#### Python

```
$ python3 --version
Python 3.6.9
```

Need docker for running `debgubench` for `find` and `grep` results.

```
$ docker --version
Docker version 19.03.8, build afacb8b7f0
```

You will avoid a lot of pain if `sudo` is set to password-less mode.

## Installing docker images

Checkout the custom fork of `dbgbench` as below, and install the images, and
start all containers.

```
$ make dbgbench-init
```

Expect the following output:
```
git clone https://github.com/vrthra-forks/dbgbench.github.io.git
Cloning into 'dbgbench.github.io'...
…
sudo ./run.sh find c8491c11
Installing image.. This will be done only once and may take up to one hour.
Sending build context to Docker daemon  39.94kB
Step 1/9 : FROM debug/find
latest: Pulling from debug/find
…
```

WARNING: depending on your internet speed, this can take a _long_ time.


If correctly installed, the following commands should print all the grep (3) and
find (4) containers.

```
$ make ls-grep
IMAGE CONTAINER ID NAMES
ddset/grep cb153a96dd6a 54d55bba
ddset/grep 1c23c48c8f67 9c45c193
ddset/grep 7511e45fcd38 3c3bdace

$ make ls-find
IMAGE CONTAINER ID NAMES
ddset/find e2f18810b55f 07b941b1
ddset/find db2031fe1f84 93623752
ddset/find 18b27d418cbf dbcb10e9
ddset/find 8032e568a934 c8491c11
```

If necessary (after all the experiments are finished), the docker images can be
removed after use with:

```
$ make dbgbench-clobber
```

## Starting the experiments

The experiments can be done with the following command:

```
$ make all
```

The above command executes _all_ experiments. If needed, individual
experiments can be done with:

### Languages

```
$ make all_closure
$ make all_clojure
$ make all_lua
$ make all_rhino
```

### Unix utilities (using docker)

```
$ make all_find
$ make all_grep
```

## Result analysis

### Table 1

We use `lua` as an example.

The command `make all_lua` will generate `results/4.lua.json`.

The result file can be inspected by the following command, which
will dump out the JSON representation of the abstract tree.

```
$ python3 src/show_tree.py  results/4.lua.json -json
```

You can also see the string representation, along with an ascii
tree representation using the following command. The abstract nodes
are colored green, and context sensitive abstract nodes are colored
red.

```
$ python3 src/show_tree.py  results/4.lua.json -tree | less -r
```


Within this file, execute this command to determine the number of chars in the
minimum input Given in Table 1, (lua-5.3.5.4, # Chars in Min String)

```
$ python3 src/show_tree.py results/4.lua.json -minstring
Min String: 'f=load(function() end)\ninteresting={}\ninteresting[0]="A"\ndebug.upvaluejoin(f,1,f,1)'
Chars in Min String: 83
```


### Table 2

For each bug, the execution details are captured under `fuzzing`. The first two
executions are to be ignored. These are test assertions that verifies that the
fault is reproduced on the original string, and is not reproduced in an empty
string.

```
$ wc -l fuzzing/4.lua.log.json 
102 fuzzing/4.lua.log.json

$ head -2 fuzzing/4.lua.log.json
{"res": "PRes.success", "key": "test", "src": "f=load(function() end)\ninteresting={}\ninteresting[0]=string.rep(\"A\",512)\ndebug.upvaluejoin(f,1,f,1)"}
{"res": "PRes.failed", "key": "test", "src": ""}
```

#### Valid%

To check the number of valid executions, we first look at the number of
executions:

```
$ cat fuzzing/4.lua.log.json  | sed -ne '3,$p' | wc -l
100
```

Then, remove the invalid executions (those that are syntactically valid, but
rejected semantically).

```
$ cat fuzzing/4.lua.log.json  | sed -ne '3,$p' | grep -v PRes.invalid | wc -l
100
```

#### FAIL%

FAIL counts executions that failed (i.e reproduced the condition of failure). We
return `PRes.success` when one can successfully trigger the condition.

```
$ cat fuzzing/4.lua.log.json  | sed -ne '3,$p' | grep -v PRes.invalid | grep PRes.success | wc -l
100
```

