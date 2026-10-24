# S036 research record

Scope: exactly S11 (order 28, alpha<=3, minimum degree 11, 155/156 edges), the nine
UNKNOWN regions 0,1,3,7,15,31,63,127,255 of the registered 256-region partition. An
independently validated SAT model would be a chi>=10 biplanar witness (independent-set
counting); none was found. Native UNSAT never closes a region without fresh standalone
DRAT plus an independent checker; no native UNSAT occurred.

Computation (all UNKNOWN): retained S035 contexts briefly resumed until lost at the
ChatGPT/Codex app closure; fresh residents for 0,7,127,255 from audited semantic state,
later four concurrent with automatic recycling (regions 0 and 7 each recycled once);
registered cold diagnostics (5 regions x 5 CaDiCaL arms x 360 s on frozen equal inputs)
kept the baseline everywhere under the pre-registered rule (no arm >=1.5x baseline
conflicts/CPU-s with adequate cuts); a fair 4-hour cold rotation ran regions 1, 3, 15.
Conflict counts and cut counts are activity measures, not progress toward closure.

Region intuition (not a claim): the nine monotone patterns are the cases of how many
of a fixed eight of vertex 0's neighbours vertex 1 is joined to; the other 247 cells
were quick contradictions, so these nine are essentially the whole stratum split nine
ways. Final per-region data: validation/S036/closeout/REGIONS_FINAL.json.
