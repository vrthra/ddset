# Replication package for _Abstracting Failure Inducing Inputs_

Our submission is a tool that implements the algorithm given in the paper _Abstracting Failure Inducing Inputs_.
We provide a file `artifact.tar.gz` which contains the code to reproduce our
results. The `artifact.tar.gz` contains [src/DDSet.ipynb](https://github.com/vrthra/ddset/blob/master/src/DDSet.ipynb) which contains the
complete algorithm explained and worked out in one simple and one complex
example in a [Jupyter notebook](https://jupyter.org/). It can be viewed through
either the virtual box as explained below, or can be directly viewed using any
of the Jupyter notebook viewers including VSCode, or github ([from this link](https://github.com/vrthra/ddset/blob/master/src/DDSet.ipynb)).

Our evaluation partially (2 subjects out of 6) depends on the
[DBGBench](https://dbgbench.github.io/) docker images. Since
these are previously published artifacts, we have not included the docker images
in our submission. The docker images are fetched automatically when the target
`make dbgbench-init` is called (see below).

## Prerequisites

### RAM

All experiments done on a base system with 15 GB RAM.

### Software

**IMPORTANT** All executables are compiled and linked in the following vagrant
box, with 8 GB RAM allocated. While it can be done on the base system itself,
it is recommended that the user simply use the vagrant box directly. See the
`Vagrantfile` for configuration.

```bash
$ vagrant up --provision
```

To connect

```
$ vagrant ssh
```

The vagrant box had the following operating system.

```bash
$ uname -rvmpio
4.15.0-70-generic #79-Ubuntu SMP Tue Nov 12 10:36:11 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux

$ lsb_release -d
Description:	Ubuntu 18.04.3 LTS
```

#### Python

The algorithm implementation was evaluated using Python version 3.6.8

```bash
$ python3 --version
Python 3.6.8
```

#### Java

The interpreters except Lua require Java

```
$ java -version
openjdk version "11.0.7" 2020-04-14
OpenJDK Runtime Environment (build 11.0.7+10-post-Ubuntu-2ubuntu218.04)
OpenJDK 64-Bit Server VM (build 11.0.7+10-post-Ubuntu-2ubuntu218.04, mixed mode, sharing)
```

#### Docker

We also need docker for running `debgubench` for `find` and `grep` results. The
docker version we checked is `19.03.8`

```bash
$ docker --version
Docker version 19.03.6, build 369ce74a3c
```

The docker image installations require `sudo`. Please grant necessary
permissions to your user if not using the virtual machine.

## Viewing the Jupyter notebook

To view the Jupyter notebook, connect to the vagrant image

```
$ vagrant ssh
```

and inside the virtual machine, execute this command

```
vm$ ./startjupyter.sh
...
     or http://127.0.0.1:8888/?token=b7c576c237db3c7aec4e9ac30b69ef1ed6a4fb32b623c93a
```

Copy and paste the last line in your host browser. The port `8888` is forwarded
to the host. Click the [src](http://127.0.0.1:8888/tree/src) link, and within
that folder, click the [DDSet.ipynb](http://127.0.0.1:8888/notebooks/src/DDSet.ipynb)
link. This will let you see the complete example already executed. You can
restart execution by clicking on Kernel>Restart&Run All or simply clear output
and run one box at a time.

## Experiments

First login to the virtual machine

```bash
$ vagrant ssh
```

Next, change directory to `ddset`

```bash
vm$ cd ddset
vm$ pwd
/home/vagrant/ddset
```

### Initializing docker images

**Note:** Docker is not required, (and hence initializing docker is not
required) for the language experiments -- `lua`, `rhino`, `clojure` and `closure`.

The following command pulls the docker images, and starts all containers.

```bash
$ make dbgbench-init
```

Expect the following output:

```bash
sudo ./run.sh find c8491c11
Installing image.. This will be done only once and may take up to one hour.
Sending build context to Docker daemon  39.94kB
Step 1/9 : FROM debug/find
latest: Pulling from debug/find
…
```

__WARNING__: depending on your internet speed, this can take a _long_ time. Note
that the docker images are not necessary except for `grep` and `find`.

If correctly installed, the following commands should print all the grep (3) and
find (4) containers.

```bash
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
removed after use with the following command:

```bash
$ make dbgbench-clobber
```

Note also that you can start individual docker instances separately using
`initfind-<bugid>` or `initgrep-<bugid>` and remove them using `rmfind-<bugid>` or `rmgrep-<bugid>` 
An example <bugid> is `54d55bba` for `grep`.

### Starting the experiments

The experiments can be started with the following command:

```bash
$ make all
```

The above command executes _all_ experiments. If needed, individual
experiments can be done with:

### Only language interpreters

```bash
$ make all_closure
$ make all_clojure
$ make all_lua
$ make all_rhino
```

### Only UNIX utilities (using docker)

```bash
$ make all_find
$ make all_grep
```

## Result analysis

### Table 1

If all experiments have finished, the Table 1 can be created with the
following command:

```bash
$ python3 src/table1.py
                  Chars in MinString    Visible  Invisible    Context Sensitive  Remaining Executions
bugid …
```

Note that the ordering may not correspond directly to the paper. Please
verify using the particular bug id (first column).

#### Individual bug evaluation

We use `lua` as an example.

The command `make all_lua` will generate `results/4.lua.json`.

The result file can be inspected by the following command, which
will dump out the JSON representation of the abstract tree.

```bash
$ python3 src/show_tree.py  results/4.lua.json -json
```

You can also see the string representation, along with an ASCII
Tree representation using the following command. The abstract nodes
are colored green, and context sensitive abstract nodes are colored
red.

```bash
$ python3 src/show_tree.py  results/4.lua.json -tree | less -r
```

If your terminal does not support colors, the tree can be drawn using
simple ASCII too.

```bash
$ python3 src/show_tree.py  results/4.lua.json
```

The `table1.py` command can be used to inspect a single file as below:

```bash
$ python3 src/table1.py results/4.lua.json

                  Chars in MinString    Visible  Invisible    Context Sensitive  Remaining Executions
          4.lua                   83         12         54                    5         28      19377
```

### Table 2

For each bug, the execution details are captured under the directory `fuzzing`.
The Table 2 can be created with the following command:

```bash
$ python3 src/table2.py
                       Valid%      FAIL%
bugid …
```

As in Table 1, the ordering may differ from the paper. Please use the first
column to identify the bug id.

#### Individual bug evaluation

Similar to `table1.py`, this command also accepts a single file.

```bash
$ python3 src/table2.py fuzzing/4.lua.log.json
                       Valid%      FAIL%
   4.lua               100.00      98.04
```

## How is the algorithm organized

The Jupyter notebook provided has one to one correspondence with the
procedure names in the paper. Each method is thoroughly documented,
and executions of methods can be performed to verify their behavior.

## How to interpret the results

The main question being asked is, whether we can abstract any nonterminals.
The `Visible` column specifies the number of visible nonterminals found,
and the `Context Sensitive` specifies how many context sensitive covarying
nonterminals could be found. The `Remaining` column specifies the number
of characters left over after abstraction.

## How to add a new subject

To add a new subject (with some bugs to abstract), one needs the following

* The grammar that can parse the subject in the canonical form defined by the
  [Parser in fuzzingbook](https://fuzzingbook.org/html/Parser.html). If you
  have an ANTLR grammar, it can be converted to the fuzzingbook format using 
  [this project](https://github.com/vrthra/antlr2json).

* The bugs you have collected

* The interpreter/compiler/command that accepts some input file. 

Do the following:

* make a directory for your interpreter under `lang`, say `mycmd`
* Under `lang/mycmd`, create three directories:
  * `lang/mycmd/bugs`
  * `lang/mycmd/compilers`
  * `lang/mycmd/grammar`
* Under `grammar`, place the JSON grammar that you have, and call it
  say `lang/mycmd/grammar/mycmd.fbjson`
* Under bugs, one file per bug, place each bugs. Say `lang/mycmd/bugs/cmd_1.cmd`
* Under `compilers` place your compiler/command executable. Say `lang/mycmd/compilers/cmd`
* Under `src` directory, one file per bug, add test cases with the following format

```python
import Infra as I
from Abstract import PRes

def my_predicate(src):
    # this following line defines how the interpreter is invoked. The first
    # string is the label, and second string is the command used to execute.
    # src will have the source
    o = I.do('mycmd', './lang/mycmd/compilers/cmd', src)

    # Now, define the behavior you want. PRes.success means the failure was
    # reproduced, while PRes.invalid means the input was semantically invalid
    # and we will ignore this input. PRes.failure is a semantically valid input
    # that could not reproduce the failure.

    if o.returncode == 0: return PRes.failed
    if o.returncode == -11: return PRes.success
    out = o.stdout
    if 'Segmentation fault (core dumped)' in out:
        return PRes.success
    elif 'stack traceback' in out:
        return PRes.invalid
    elif 'TIMEOUT' in out:
        return PRes.timeout
    return PRes.failed

import sys
if __name__ == '__main__':
    # Here we define the paths
    I.main('./lang/mycmd/grammar/mycmd.fbjson', './lang/mycmd/bugs/cmd_1.cmd', my_predicate)
```
Once this predicate is written to file say as `src/mycmd_1.py`, invoking it,
using `python3 src/mycmd_1.py` will produce the correctly abstracted file under
`result/cmd_1.cmd.json`.

The same predicate can also be used to fuzz by producing a new file `src/fuzz_cmd_1.py` with
the following contents

```python

import Fuzz as F
import mycmd_1 as Main

import sys
if __name__ == '__main__':
    F.main('./lang/mycmd/grammar/mycmd.fbjson', './lang/mycmd/bugs/cmd_1.cmd', Main.my_predicate)
```

Invoking this file using `python3 src/fuzz_mycmd_1.py` will produce the
fuzz output under `fuzzing/fuzz_mycmd_1.json`, which can be inspected for
results.

