# S044 decision audit — 24 October 2026

Recommendation: **PAUSE** the current construction campaign pending an owner
decision and a new mechanism. This is a recommendation, not an owner-approved
programme pause. The computation remains stopped. D042 and 9<=chi_2<=12 are
unchanged; no certified chi>=10 witness exists in the programme records.

The accompanying EVIDENCE_TABLE.md is the requested single comparison of
S037–S043, with machine-readable rows in validation/S044/EVIDENCE.json.
Historical timings are reported on their original bases, not as matched
benchmarks. S042 includes an estimated 900-second abandoned generation run
and discloses another failed start without a separate CPU meter. The sum of
reported values is not an exact total campaign cost or a success-rate estimate.

There was a real local-search improvement in S039: 91/123 became 82/79
independent four-sets at 156/155 edges. Every saved pair was still explicitly
at most nine-colourable. S040 then tested its proposed compatibility mechanism
and failed every registered progress arm. No later session supplied a live
construction source that passed its own gate. The finite order-13 alpha<=3
slice is excluded; its biplanar-pair class itself contains 3,510 valid pairs.
The order-3 class remains entirely UNKNOWN after a cut cap. Its 10,000 models
and 20,000 cuts are activity records, not a projection count or a measured
probability of finding a witness. Zero planar layers in those models is not
a claim that the class has no planar layers.

S042's 97 individual negatives and the 45-type table remain intact, with 30
non-Ore windows unresolved. SCOPE_CORRECTION.md narrows the implication from
these negatives to iterated compositions: later joins can remove additional
edges of an earlier leaf. All-tested-leaf trees remain excluded by the written
deletion-count argument; one tested leaf anywhere in an arbitrary mixed tree
is insufficient for the recorded containment proof. No global counterexample
to that broader conclusion is claimed. This correction adds an open boundary,
not a positive construction or a reason to restart the same census.

## Decision comparison

| Choice | What would justify it | Current assessment |
|---|---|---|
| CONTINUE | Explicit new inputs, a different construction mechanism that avoids a diagnosed barrier, a checkable certificate path and a fixed progress gate | No supplied source or surviving example meets all of these requirements. Open involutions or another Z3 cap alone do not. |
| PAUSE | Preserve useful results and UNKNOWNs while stopping default repetition | Best supported. Local optimisation is parked, the resolved apex source failed its gate, and the next symmetric slice capped without a planar pair. |
| CHANGE_TARGET | Owner selects a different objective after reviewing its benefit and cost | A proposal only. No target change is adopted; upper-bound or formalisation work is not started. |

The recommendation rests on the lack of a selected mechanism with positive
evidence, not an exhaustion of available CPU or a proof the target is impossible.
More computation could settle an UNKNOWN slice. Such a negative would be
learning under the registered gates, and no reliable duration or success
probability is established. F9 (chi_f<=9 for biplanar graphs) remains a
conjectural risk: an order-28 alpha<=3 witness would have chi_f>=28/3>9.
We neither assume F9 nor investigate a universal upper bound.

## Open cases and concrete re-entry requirements

| Opening | Current boundary | Required evidence before proposing a new run |
|---|---|---|
| Non-Ore critical leaves | Thirty S042 windows; no complete generator or positive leaf | A specified critical graph or finite independently justified generator, an edge/apex choice, and a reason it avoids the known K9-minor obstruction. |
| Mixed Hajós trees | A single tested leaf may be modified repeatedly; broad implication unproved | A concrete tree and surviving-subgraph maps, or a valid replacement proof. A logical gap alone is not positive evidence. |
| Order-2 symmetry | Layer-preserving and layer-swapping cases unexecuted here | Justified orbit/face cases, sound normaliser reduction and controls; no transfer of odd-prime arguments to involutions. |
| Order-3 symmetry | Entire S043 existence question UNKNOWN; semantic cuts retained | A materially different propagation/encoding idea with a bounded diagnostic and explicit progress criterion, not an automatic longer cap. |
| S11 sorted cells | 0,1,3,7,15,31,63,127,255 remain UNKNOWN | A changed encoding or proved reduction, fresh Windows acceptance and a practical explicit resource plan; never reuse stopped S036 controls. |

RECOVERY_MAP.md identifies the permanent evidence and the precise distinction
between reading, replaying and starting a new experiment. S045 is only the
owner-decision/re-entry gate. A generic invocation does not select a new
target, accept a speculative mechanism or restart a solver.
