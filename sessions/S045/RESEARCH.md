# S045 research and benchmark

Owner selected 50 vertices and explicitly authorised prepare/test/benchmark/
launch. No target change: chi>=10, thickness at most two. The new domain has
all 1225 optional pairs, no independence/degree/symmetry/density restriction.
Inherited attributed native partial-planarity code is preserved as source in
tools/s045_native.cpp; tools/s045_main.hpp supplies a new incremental protocol.
Python independently checks both rotation systems and every colouring before
feeding back a necessary partition clause. Private solver learning persists
between candidates; only audited semantic rules survive slice recycling.

For any map c:V->{0,...,8}, every graph without a proper nine-colouring must
have an edge uv with c(u)=c(v). Therefore OR over both layer variables of all
such pairs is a sound necessary clause. If the current graph is properly
coloured by c, it falsifies that clause and is excluded. No assumption about
alpha is involved. Colour names may be permuted freely; splitting a class
preserves properness and can shorten/strengthen the clause.

| Arm | Verified candidates | Elapsed seconds | Checked geometric cuts |
|---|---:|---:|---:|
| block | 4814 | 60.094 | 1081 |
| partition | 3842 | 60.391 | 11962 |
| partition-positive | 3365 | 61.891 | 38322 |

Default partition feedback selected under the registered operational gate.
Exact blocking visited more models; no speedup or greater projected coverage
is claimed. Each partition rule excludes all graphs permitting that same
colouring, while exact blocking excludes just one layer assignment. Candidate
counts and geometric clause counts are diagnostics. The benchmark contains
no non-nine-colourable candidate, no domain refutation and no headline advance.

Fresh semantic restart: 995 additional verified candidates in 16.125s.

## Streaming revision and repeated benchmark

38042 candidates and 111073 geometric rule occurrences from the first slice
are preserved. Exact regenerated CNF bytes from all rows match; replay private
memory about 33 MB. Wrong n/k/mode and partial checkpoint rows rejected.
Fresh native acceptance repeated after the streaming change.

| Arm | Candidates | Seconds | Geometric rules |
|---|---:|---:|---:|
| block | 4872 | 60.109 | 1081 |
| partition | 3847 | 60.360 | 11981 |
| partition-positive | 4239 | 61.828 | 39430 |

Selected partition-positive; fresh restart added 806 candidates
in 17.594s. This operational selection does not
establish a statistical speedup. Original source/receipts and both benchmarks
remain archived. Same campaign resumes all saved rules, original ceiling.
