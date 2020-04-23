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

unbuffer= #unbuffer -p

results/reduce_%.log: src/%.py | results
	time $(python) $< 2>&1 | $(unbuffer) tee $@_
	mv $@_ $@

results/fuzz_%.log: src/fuzz_%.py results/reduce_%.log
	time $(python) $< 2>&1 | $(unbuffer) tee $@_
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

init-find: .dbgbench; $(MAKE) -C dbgbench.github.io/docker init-find find_bugs="$(find_bugs)"
init-grep: .dbgbench; $(MAKE) -C dbgbench.github.io/docker init-grep grep_bugs="$(grep_bugs)"

rm-find:; $(MAKE) -C dbgbench.github.io/docker rm-find
rm-grep:; $(MAKE) -C dbgbench.github.io/docker rm-grep

prune-find:; sudo docker system prune --filter ancestor=ddset/find || echo
prune-grep:; sudo docker system prune --filter ancestor=ddset/grep || echo

ls-find:; @sudo docker ps --filter ancestor=ddset/find --format 'table {{.Image}} {{.ID}} {{.Names}}'
ls-grep:; @sudo docker ps --filter ancestor=ddset/grep --format 'table {{.Image}} {{.ID}} {{.Names}}'
