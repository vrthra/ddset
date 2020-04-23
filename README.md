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

Need docker for running `debgubench` for `find` and `grep` results.

```
$ docker --version
Docker version 19.03.8, build afacb8b7f0
```

## Installing docker images

Checkout the custom fork of `dbgbench` as below, and install the images, and
start all containers.

```
$ git clone https://github.com/vrthra-forks/dbgbench.github.io.git
$ cd dbgbench.github.io/docker
$ make init
```

Expect the following output:
```
sudo ./run.sh find c8491c11
Installing image.. This will be done only once and may take up to one hour.
Sending build context to Docker daemon  39.94kB
Step 1/9 : FROM debug/find
latest: Pulling from debug/find
…
```

If correctly installed, the following commands should print all the grep (3) and
find (4) containers.

```
$ ./grep.id 
IMAGE CONTAINER ID NAMES
ddset/grep cb153a96dd6a 54d55bba
ddset/grep 1c23c48c8f67 9c45c193
ddset/grep 7511e45fcd38 3c3bdace

$ ./find.id 
IMAGE CONTAINER ID NAMES
ddset/find e2f18810b55f 07b941b1
ddset/find db2031fe1f84 93623752
ddset/find 18b27d418cbf dbcb10e9
ddset/find 8032e568a934 c8491c11
```

## Starting the experiments


```
$ make all_lua
```

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
