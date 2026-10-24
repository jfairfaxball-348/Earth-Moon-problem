# S036 adversarial review

- No result is claimed: 247 encoded closures are inherited certificates, not a stratum
  proof; nine regions UNKNOWN; 9<=chi2<=12; no witness. Re-audited cuts are valid
  planarity lemmas (Kuratowski subdivisions), not region exclusions.
- Clause counts are occurrences across blocks, not globally unique clauses.
- Private CDCL was lost twice (S035 contexts at app closure; S036 processes at recycle
  and closeout); nothing claims it was retained or serialised.
- Diagnostics compared throughput screens on equal inputs only; they do not show any
  arm is better at closing regions. The adoption rule was registered before results and
  its memory criterion amended (1.5 -> 1.9 GiB) before any non-baseline arm counted.
- Operational defects found and fixed in-session (all recorded): GIL-starved lease
  expiry, cold-slot memory thrash, unequal diagnostic inputs, double-counted memory
  gate, region drop on interrupted relaunch, CRLF hash mismatch caught by CI.
- Not established: whether the nine regions are SAT or UNSAT; whether the current
  CDCL+planarity method can close them on this hardware; any ETA.
