# S035 final nine-region diagnostic

| ID | Recovery state | Last conflicts | Proof/check backlog |
|---:|---|---:|---|
| 0 | Suspended original RAM context | 34269280 | None; UNKNOWN |
| 1 | Cold; semantic recovery | 59121 | None; UNKNOWN |
| 3 | Cold; semantic recovery | 99323 | None; UNKNOWN |
| 7 | Suspended original RAM context | 35376235 | None; UNKNOWN |
| 15 | Cold; semantic recovery | 1255961 | None; UNKNOWN |
| 31 | Cold; semantic recovery | 1365334 | None; UNKNOWN |
| 63 | Cold; semantic recovery | 99606 | None; UNKNOWN |
| 127 | Suspended original RAM context | 35893361 | None; UNKNOWN |
| 255 | Suspended original RAM context | 33083987 | None; UNKNOWN |

Native counters are last logged values, not exact at-stop instruction counts.
Retained contexts completed multiple600s turns without new PID creation. The
resumption stopped operationally at the SAT scanner PermissionError; it did
not demonstrate exhaustion or a mathematical barrier. Cold1/3/63 had historical
V1 memory eviction;15/31 had historical exit1 without adequate attribution.
All five cold regions were unsearched by the sustained four-resident controller.
No unresolved region has pending native UNSAT, proof generation or checker backlog.

Priority: repair watcher sharing/cache, retain the four RAM contexts, audit
geometric additions, measure region-specific changes on identical inputs per
active CPU second, attribute native exits and avoid indefinite cold starvation.
Do not infer SAT from difficulty. No evidence currently justifies eight workers.
