# Nine unresolved regions at owner pause

All are UNKNOWN search regions; none has a pending UNSAT proof or checker backlog.
Counters are the final retained process value, or the largest observed historical value for cold regions. They are not comparable solve-speed measures.

| ID | Paused state | Conflicts | Decisions | Propagations | Proof attempts |
|---:|---|---:|---:|---:|---:|
| 0 | NATIVE_SUSPENDED_RAM_RETAINED | 22492009 | 56534525 | 4764188642 | 0 |
| 1 | COLD_QUEUED_SEMANTIC_RECOVERY | 59121 | 349743 | 24493073 | 0 |
| 3 | COLD_QUEUED_SEMANTIC_RECOVERY | 99323 | 431766 | 27593384 | 0 |
| 7 | NATIVE_SUSPENDED_RAM_RETAINED | 24651595 | 58620126 | 5277916706 | 0 |
| 15 | COLD_QUEUED_SEMANTIC_RECOVERY | 1255961 | 4030838 | 267118273 | 0 |
| 31 | COLD_QUEUED_SEMANTIC_RECOVERY | 1365334 | 3586718 | 267172816 | 0 |
| 63 | COLD_QUEUED_SEMANTIC_RECOVERY | 99606 | 389563 | 25152301 | 0 |
| 127 | NATIVE_SUSPENDED_RAM_RETAINED | 24660333 | 58571834 | 5469064448 | 0 |
| 255 | NATIVE_SUSPENDED_RAM_RETAINED | 21207159 | 49763568 | 4743657418 | 0 |

The former flat counters were congruence inprocessing, not evidence of a
mathematical barrier. Equal90s comparison:4216 versus1003623 conflicts with
congruence disabled; both UNKNOWN. Cold restarts lost private CDCL; the resident
V1 pilot also evicted contexts under memory pressure. V2 retained four identities
through repeated turns without eviction/restart churn. Their increasing conflict,
decision and propagation counters demonstrate active search, not eventual success.
The remaining bottleneck is algorithmic search; a mathematical explanation is
unknown. No resource cap or proof verification backlog explains the current nine.

For0,7,127,255 preserve RAM identities before any recovery; compare phase time,
conflict rates per active CPU second and new geometric cuts on equal inputs.
For1,3,15,31,63 restore semantic state only when capacity opens; current V2 did
not execute those cold regions. Their smaller historical counters do not show a
current stall. Test region-specific branching/inprocessing changes under a
registered comparison. Do not infer SAT from difficulty or closure from solver
UNSAT alone. Make cooperative stop and SAT-first handling mandatory first.

Historical stale retained flags on cold rows are recorded in NINE_REGIONS.json.
The old records are preserved; actual context membership determines RAM retention.

Individual operational notes:0,7,127,255 retained their V2 process identities without V2 eviction or restart;1,3,63 experienced a V1 memory eviction and were cold under V2.15 and31 each have a historical V1 native exit1 with no reason, recorded NATIVE_UNKNOWN; preserve these failure records and repair lifecycle exit attribution before reuse. None had a pending proof, proof cap or checker failure.
