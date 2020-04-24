# Replication package for _Abstracting Failure Inducing Inputs_

Our submission is a tool that implements the algorithm given in the paper _Abstracting Failure Inducing Inputs_.
We provide a file `artifact.tar.gz` which contains the code to reproduce our
results. The `artifact.tar.gz` contains `src/DDSet.ipynb` which contains the
complete algorithm explained and worked out in one simple and one complex
example in a [Jupyter notebook](https://jupyter.org/). It can be viewed through
either the virtual box as explained below, or can be directly viewed using any
of the Jupyter notebook viewers including VSCode.

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
Docker version 19.03.8, build afacb8b7f0
```

The docker image installations require `sudo`. Please grant necessary
permissions to your user.

## Initializing docker images

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

## Starting the experiments

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
$ python3 src/table1.py results/*.json
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
$ python3 src/table2.py fuzzing/*.json
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
## How to interpret the results
## How to add a new subject


