# S004 reproduction and trust

Run from repository root with Python 3.12.10, networkx 3.5,
python-sat 1.9.dev15, numpy 2.5.4. Exact commands, source/binary/artifact
hashes and outcomes are in ../S004_MANIFEST.json. The CAM-0005 registration
and amendments fix the finite domains. No UNKNOWN result means UNSAT.

The 271 bag DRAT proofs in chi10/ are checked refutations of the deterministic
bag CNFs from tools/blowup_chi_cnf.py. Each result row gives graph6/weights,
CNF and uncompressed proof hash, two actual checker verdicts and explicit
10-colouring. Decompress to scratch and regenerate the bag CNF with
bag_cnf(g6,w,9); write LF DIMACS exactly as tools/s004_certify.py does;
verify the two hashes, then run drat-trim CNF PROOF. Vertex refutations were
also checked this session but are stored in ignored scratch; regenerate
with vertex_cnf and the pinned standalone solver. The archived bag proof
alone plus the upper colouring suffices for the finite chromatic claim.

Face-oracle UNSAT artifacts in search/ contain compressed CNF and DRAT,
cut metadata, generator options, checker logs and source-labelled inputs
in targets/. Decompress the pair into ignored scratch; run
tools/triangulation_cover.py check EDGEFILE PREFIX (cut metadata must sit
beside PREFIX.cnf), then drat-trim PREFIX.cnf PREFIX.drat. The archived
K9-control has the same layout. SAT splits, if any, need
tools/check_layers.py EDGEFILE PREFIX.split.json. Generator regeneration
is byte comparison, not independent formalisation of the generator.

For the full 22-vertex obstruction, use the compressed CNF in search/ and
the separately archived full-obstruction-core.drat.gz. Decompress the
proof, verify raw SHA-256 from full_obstruction_compact_proof.json, and
check it against the full regenerated CNF. The compact proof was rechecked
after extraction with drat-trim -l. Original two solver proofs remain in
scratch with permanent hashes/actual checker logs and reproducible commands.
The separate independent incidence challenge found a non-planar relaxed
SAT model; it is not a second independent certification of the exclusion.

The apex pool audit is separately reproducible from SRC-0017 commit
5cb2ca9f7d4d6d195617c09f7348841636b646f6 using tools/audit_apex_pool.py;
four explicit K9 sets are retained, so those exclusions do not depend on
the new face encoder. Source labels are relabelled bijectively, without
adding missing integer labels as vertices. Entire corpus chromatic values
are not assumed in this exclusion claim.

The double-wheel lock stores all V/E1/E2/colourings/pair gadgets. Its lower
chi=4 proof is the contained odd C5 wheel, given in the research dossier.
The census samples each cover exactly one fixed 8-vertex base through all
8^8 weights, with an independent MIS-cover colouring search and a main-tool
rerun. They do not certify the full order-8 census.

## Native builds

Upstream CaDiCaL c60730422e758ef1cebe7aeddf2dda31c996bf04 (3.0.1) and
drat-trim 2e3b2dc0ecf938addbd779d42877b6ed69d9a985 cloned in scratch.
Windows compiler llvm-mingw 20261006 ucrt-x86_64 release. Compile kitten.c
with clang -O2 -DNDEBUG -D__USE_MINGW_ANSI_STDIO=1 -c; compile every CaDiCaL
src/*.cpp except mobical.cpp with clang++ -O2 -DNDEBUG -DNBUILD -DNUNLOCKED
-D__USE_MINGW_ANSI_STDIO=1, link kitten.o and -lpsapi. Put compiler runtime
libc++.dll/libunwind.dll/libwinpthread-1.dll beside the solver, or on PATH.
Compile drat-trim.c with clang -O2 -Dgetc_unlocked=getc. Native Linux
configure/make builds of the same pins should also reproduce the proofs.
No nauty binary was needed for the two fixed-base samples; no k=9 census
or whole-base enumeration was run. This deviation from the S004 tooling
suggestion is explicit, not a claim that those tools were rebuilt.
