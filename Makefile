python=python3

clean: ; rm -rf *.reduce.log *.fuzz.log results fuzzing
clobber: clean; rm -rf .db
results:; mkdir -p results

find_bugs=07b941b1 93623752 c8491c11 dbcb10e9
grep_bugs=3c3bdace 54d55bba 8f08d8e2 9c45c193

closure_bugs=2808 2842 2937 3178 3379 1978
clojure_bugs=2092 2345 2450 2473 2518 2521

lua_bugs=5_3_5__4
rhino_bugs=385 386


find_results_src=$(addsuffix .log,$(addprefix results/reduce_find_,$(find_bugs)))
grep_results_src=$(addsuffix .log,$(addprefix results/reduce_grep_,$(grep_bugs)))

lua_results_src=$(addsuffix .log,$(addprefix results/reduce_lua_,$(lua_bugs)))
rhino_results_src=$(addsuffix .log,$(addprefix results/reduce_rhino_,$(rhino_bugs)))
clojure_results_src=$(addsuffix .log,$(addprefix results/reduce_clojure_,$(clojure_bugs)))
closure_results_src=$(addsuffix .log,$(addprefix results/reduce_closure_,$(closure_bugs)))

fuzz_find_results_src=$(addsuffix .log,$(addprefix results/fuzz_find_,$(find_bugs)))
fuzz_grep_results_src=$(addsuffix .log,$(addprefix results/fuzz_grep_,$(grep_bugs)))

fuzz_lua_results_src=$(addsuffix .log,$(addprefix results/fuzz_lua_,$(lua_bugs)))
fuzz_rhino_results_src=$(addsuffix .log,$(addprefix results/fuzz_rhino_,$(rhino_bugs)))
fuzz_closure_results_src=$(addsuffix .log,$(addprefix results/fuzz_closure_,$(closure_bugs)))
fuzz_clojure_results_src=$(addsuffix .log,$(addprefix results/fuzz_clojure_,$(clojure_bugs)))

start_%:; @echo done
stop_%:; @echo done


stop_find: $(addprefix stop_,$(find_bugs))
	@echo done.

stop_grep: $(addprefix stop_,$(grep_bugs))
	@echo done.

$(addprefix start_,$(grep_bugs)):
	sudo docker stop $(subst start_,,$@)
	sudo docker start $(subst start_,,$@)

$(addprefix stop_,$(grep_bugs)):
	sudo docker stop $(subst stop_,,$@)

$(addprefix start_,$(find_bugs)):
	sudo docker stop $(subst start_,,$@)
	sudo docker start $(subst start_,,$@)

$(addprefix stop_,$(find_bugs)):
	sudo docker stop $(subst stop_,,$@)

unbuffer= #unbuffer -p

results/reduce_%.log: src/%.py | results
	@- $(MAKE) start_$(subst find_,,$*)
	@- $(MAKE) start_$(subst grep_,,$*)
	time $(python) $< 2>&1 | $(unbuffer) tee $@_
	@- $(MAKE) stop_$(subst find_,,$*)
	@- $(MAKE) stop_$(subst grep_,,$*)
	mv $@_ $@

results/fuzz_%.log: src/fuzz_%.py results/reduce_%.log
	@- $(MAKE) start_$(subst find_,,$*)
	@- $(MAKE) start_$(subst grep_,,$*)
	time $(python) $< 2>&1 | $(unbuffer) tee $@_
	@- $(MAKE) stop_$(subst find_,,$*)
	@- $(MAKE) stop_$(subst grep_,,$*)
	mv $@_ $@

reduce_find: $(find_results_src); @echo done
reduce_grep: $(grep_results_src); @echo done

reduce_lua: $(lua_results_src); @echo done
reduce_rhino: $(rhino_results_src); @echo done
reduce_clojure: $(clojure_results_src); @echo done
reduce_closure: $(closure_results_src); @echo done

fuzz_find: $(fuzz_find_results_src); @echo done
fuzz_grep: $(fuzz_grep_results_src); @echo done

fuzz_lua: $(fuzz_lua_results_src); @echo done
fuzz_rhino: $(fuzz_rhino_results_src); @echo done
fuzz_clojure: $(fuzz_clojure_results_src); @echo done
fuzz_closure: $(fuzz_closure_results_src); @echo done


all_find: fuzz_find
	tar -cf find.tar results .db
	@echo find done

all_grep: fuzz_grep
	tar -cf grep.tar results .db
	@echo grep done

all_lua: fuzz_lua
	tar -cf lua.tar results .db
	@echo lua done

all_rhino: fuzz_rhino
	tar -cf rhino.tar results .db
	@echo rhino done

all_clojure: fuzz_clojure
	tar -cf clojure.tar results .db
	@echo clojure done

all_closure: fuzz_closure
	tar -cf closure.tar results .db
	@echo closure done

all: all_lua all_rhino all_clojure all_closure all_find all_grep
	@echo done

dbgbench-init: .dbgbench init-find init-grep
	@echo done

.dbgbench:
	git clone https://github.com/vrthra-forks/dbgbench.github.io.git
	touch $@

dbgbench-clobber:
	-$(MAKE) rm-find
	-$(MAKE) rm-grep
	rm -rf dbgbench.github.io .dbgbench

init-find: .dbgbench;
	for i in $(find_bugs); do \
		$(MAKE) -C dbgbench.github.io/docker initfind-$$i; \
		sudo docker stop $$i; \
		done
init-grep: .dbgbench;
	for i in $(grep_bugs); do \
		$(MAKE) -C dbgbench.github.io/docker initgrep-$$i; \
		sudo docker stop $$i; \
		done

rm-find:; $(MAKE) -C dbgbench.github.io/docker rm-find
rm-grep:; $(MAKE) -C dbgbench.github.io/docker rm-grep

prune-find:; sudo docker system prune --filter ancestor=ddset/find || echo
prune-grep:; sudo docker system prune --filter ancestor=ddset/grep || echo

ls-find:; @sudo docker ps -a --filter ancestor=ddset/find --format 'table {{.Image}} {{.ID}} {{.Names}} {{.Status}}'
ls-grep:; @sudo docker ps -a --filter ancestor=ddset/grep --format 'table {{.Image}} {{.ID}} {{.Names}} {{.Status}}'

artifact.tar.gz: Vagrantfile Makefile
	rm -rf artifact && mkdir -p artifact/ddset
	cp README.md artifact/README.txt
	cp -r README.md lang src dbgbench.github.io .dbgbench Makefile Vagrantfile artifact/ddset
	cp -r Vagrantfile artifact/
	tar -cf artifact.tar artifact
	gzip artifact.tar



# PACKAGING
box-up: artifact.tar.gz
	cd artifact && vagrant up
	cd artifact && vagrant ssh -c 'cd /vagrant; tar -cpf ~/ddset.tar ddset ; cd ~/; tar -xpf ~/ddset.tar'
	cd artifact && vagrant ssh -c 'cd ~/ddset && make dbgbench-init'
	cd artifact && vagrant package --output ../ddset.box --vagrantfile ../Vagrantfile.new

box-add:
	rm -rf vtest && mkdir -p vtest
	cd vtest && vagrant box add ddset ../ddset.box
	cd vtest && vagrant init ddset
	cd vtest && vagrant up

box-remove:
	- vagrant destroy $$(vagrant global-status | grep ddset | sed -e 's# .*##g')
	vagrant box remove ddset

show-ports:
	 sudo netstat -ln --program | grep 8888
