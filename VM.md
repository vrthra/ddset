# Replication package for _Abstracting Failure Inducing Inputs_

Our submission is a tool that implements the algorithm given in the paper
_Abstracting Failure Inducing Inputs_.

We provide the virtual machine [ddset](https://drive.google.com/open?id=1qFw3DCM7qTqpo00FycGyYIW0pQ2l5-QC)
(hosted on google drive) which contains the complete artifacts necessary to
reproduce our findings. We describe the process of invoking the virtual machine
below.

We also note that if you are unable to download the vagrant box (it is 7.3 GB),
you can also take a look at a complete worked out example as a Jupyter notebook
given [here](https://github.com/vrthra/ddset/blob/master/src/DDSet.ipynb) (hosted on Github).

## Using the VM.

### Software

We used [vagrant 2.2.7](https://www.vagrantup.com/), and VirtualBox 5.2.18.

### RAM

All experiments done on a host system with **15 GB RAM**, and the VM was allocated **8 GB RAM**.

### Setup

First, please make sure that the port 8888 is not in use. Our VM forward its
local port 8888 to the host machine.

#### Download

Next, download the vagrant box from the following link:

https://drive.google.com/open?id=1qFw3DCM7qTqpo00FycGyYIW0pQ2l5-QC

Unfortunately, due to the way google drive works, you need to navigate to that
link using a browser, and click on the file. There is no fail-safe command-line.

This produces a file called `ddset.box` which is 7.3 GB in size, and should have
the following _md5_ checksum. (The commands in the host system are indicated by
leading `$` and the other lines indicate the expected output).

```bash
$ du -ksh ddset.box
7,4G  ddset.box

$ md5sum ddset.box
13f342863834e48b5cf679dd04199a34 ddset.box
```

#### Importing the box

The vagrant box can be imported as follows:

```bash
$ vagrant box add ddset ./ddset.box
==> box: Box file was not detected as metadata. Adding it directly...
==> box: Adding box 'ddset' (v0) for provider: 
    box: Unpacking necessary files from: file:///path/to/ddset/ddset.box
==> box: Successfully added box 'ddset' (v0) for 'virtualbox'!

$ vagrant init ddset
A `Vagrantfile` has been placed in this directory. You are now
ready to `vagrant up` your first virtual environment! Please read
the comments in the Vagrantfile as well as documentation on
`vagrantup.com` for more information on using Vagrant.

$ vagrant up
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'ddset'...
==> default: Matching MAC address for NAT networking...
==> default: Setting the name of the VM: ddset_default_1587934454463_17567
==> default: Clearing any previously set network interfaces...
==> default: Preparing network interfaces based on configuration...
    default: Adapter 1: nat
==> default: Forwarding ports...
    default: 8888 (guest) => 8888 (host) (adapter 1)
    default: 22 (guest) => 2222 (host) (adapter 1)
==> default: Running 'pre-boot' VM customizations...
==> default: Booting VM...
==> default: Waiting for machine to boot. This may take a few minutes...
    default: SSH address: 127.0.0.1:2222
    default: SSH username: vagrant
    default: SSH auth method: private key
==> default: Machine booted and ready!
==> default: Checking for guest additions in VM...
==> default: Mounting shared folders...
    default: /vagrant => /path/to/ddset
```

#### Verify Box Import

The commands inside the guest system are indicated by a `vm$ ` prefix.

```bash
$ vagrant ssh

vm$ free -g
              total        used        free      shared  buff/cache   available
Mem:              7           0           7           0           0           7
Swap:             1           0           1

```

## A complete example

```bash
vm$ ls
ddset  ddset.tar  startjupyter.sh
```

The main experiments are in `ddset` directory in the VM,
which contains the code to reproduce our results. The same directory contains
[src/DDSet.ipynb](https://github.com/vrthra/ddset/blob/master/src/DDSet.ipynb) which contains the
complete algorithm explained and worked out in one simple and one complex
example in a [Jupyter notebook](https://jupyter.org/). It can be viewed through
either the virtual box as explained below, or can be directly viewed using any
of the Jupyter notebook viewers including VSCode, or github ([from this link](https://github.com/vrthra/ddset/blob/master/src/DDSet.ipynb)).

### Viewing the Jupyter notebook

To view the Jupyter notebook, connect to the vagrant image if you haven't
already connected.

```bash
$ vagrant ssh
```

and inside the virtual machine, execute this command

```bash
vm$ ./startjupyter.sh
...
     or http://127.0.0.1:8888/?token=b7c576c237db3c7aec4e9ac30b69ef1ed6a4fb32b623c93a
```

Copy and paste the last line in your host browser. The port `8888` is forwarded
to the host. Click the [src](http://127.0.0.1:8888/tree/src) link from the
opened file system browser, and within that folder, click the
[DDSet.ipynb](http://127.0.0.1:8888/notebooks/src/DDSet.ipynb) link. This will
let you see the complete example already executed. You can restart execution by
clicking on `Kernel>Restart & Run All` or simply clear output
and run one box at a time.

## Experiments

First login to the virtual machine if you have not yet done so.

```bash
$ vagrant ssh
```

Next, change directory to `ddset`

```bash
vm$ cd ddset
vm$ pwd
/home/vagrant/ddset
```

### Starting the experiments

There are two sets of subjects -- the language interpreters including
`Lua`, `Clojure`, `Closure` (JS), and `Rhino` (JS), and the UNIX utilities
`grep` and `find`. Their evaluations are slightly different. Hence, we provide
the ability to either run all experiments at once, or one by one.

All experiments can be started with the following command:

```bash
vm$ make all
```

If needed, individual experiments can be done with:

### Only language interpreters

```bash
vm$ make all_closure
vm$ make all_clojure
vm$ make all_lua
vm$ make all_rhino
```

### Only UNIX utilities (using docker)

First ensure that the docker images are present. Note that the
`NAMES` column corresponds to the particular bug id.

```
vm$ make ls-grep
IMAGE      CONTAINER ID NAMES    STATUS
ddset/grep 0ecf7398c596 9c45c193 Exited (137) 3 hours ago
ddset/grep c4781f208603 8f08d8e2 Exited (137) 3 hours ago
ddset/grep 4162569a88d4 54d55bba Exited (137) 3 hours ago
ddset/grep 68c4b8dcade6 3c3bdace Exited (137) 3 hours ago

vm$ make ls-find
IMAGE      CONTAINER ID NAMES    STATUS
ddset/find f915a31ac622 dbcb10e9 Exited (137) 3 hours ago
ddset/find 1b7612452d7e c8491c11 Exited (137) 3 hours ago
ddset/find 93fc570cbc53 93623752 Exited (137) 3 hours ago
ddset/find fe331cf7f805 07b941b1 Exited (137) 3 hours ago
```

Next, we can start the UNIX utilities experiments as below.

```bash
vm$ make all_find
vm$ make all_grep
```

## Result analysis

### Table 1

If all experiments have finished, the Table 1 can be created with the
following command:

```bash
vm$ ./src/table1.py
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
vm$ ./src/show_tree.py  results/4.lua.json -json
```

You can also see the string representation, along with an ASCII
Tree representation using the following command. The abstract nodes
are colored green, and context sensitive abstract nodes are colored
red.

```bash
vm$ python3 src/show_tree.py  results/4.lua.json -tree | less -r
```

If your terminal does not support colors, the tree can be drawn using
simple ASCII too.

```bash
vm$ python3 src/show_tree.py  results/4.lua.json
```

The `table1.py` command can be used to inspect a single file as below:

```bash
vm$ ./src/table1.py results/4.lua.json

                  Chars in MinString    Visible  Invisible    Context Sensitive  Remaining Executions
          4.lua                   83         12         54                    5         28      19377
```

### Table 2

For each bug, the execution details are captured under the directory `fuzzing`.
The Table 2 can be created with the following command:

```bash
vm$ ./src/table2.py
                       Valid%      FAIL%
bugid …
```

As in Table 1, the ordering may differ from the paper. Please use the first
column to identify the bug id.

#### Individual bug evaluation

Similar to `table1.py`, this command also accepts a single file.

```bash
vm$ ./src/table2.py fuzzing/4.lua.log.json
                       Valid%      FAIL%
   4.lua               100.00      98.04
```

## How is the algorithm organized

The Jupyter notebook provided has one to one correspondence with the
procedure names in the paper. Each method is thoroughly documented,
and executions of methods can be performed to verify their behavior.

## How to interpret the results

The main question being asked is, whether we can abstract any nonterminals.
Using the `src/table1.py`, The `Visible` column specifies the number of visible
nonterminals found, the `Invisible` column specifies the number of invisible
nonterminals such as spaces, the `Context Sensitive` specifies how many context
sensitive covarying nonterminals could be found. The `Remaining` column
specifies the number of characters left over after abstraction. Finally the
`Executions` show the number of executions that was used to produce the result.

The fact that for most of the subjects, we have non-zero values for Visible,
and Context Sensitive columns suggests that our tool works. The `Remaining`
column specifies the remaining characters that could not be abstracted, and
hence found integral to reproduce the faults.

The `src/table2.py` produces two columns -- `Valid` and `FAIL`. Valid indicates
the percentage of semantically valid (all produced are syntactically valid)
values produced. Of these, the `FAIL` percentage indicates the percentage of 
inputs that successfully reproduced the failure. Our algorithm is validated by
the nearly 100% FAIL for all subjects.

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

