# S031 research — in progress

Target remains OP1(b), order28 alpha<=3, S11 minimum degree11 and155/156 edges.
No new theorem or certified stratum is claimed at launch. CLM-0114/0115 proofs
are unchanged: necessary filters and root/star/type sorting are inherited with
their exact conditional boundaries.

Implementation change: reuse the SAME live CaDiCaL300 extension instance after
each checked K9/Kuratowski/triangle-free/library clause batch. Conflict/decision
budget slices do not destroy or recreate the instance. Learned clauses persist
inside that live instance; semantic JSON/CNF checkpoints do not pretend to save
its private native search state. Checkpoint recovery revalidates all cuts and
rebuilds the formula, honestly losing the private state on process loss.

The search starts from the exact S030 sorted-root formula and the checked union
of its1084 sorted-run cuts and30 pilot cuts (1114 distinct clauses). No sampled
model blocker is used. Each new SAT model is checked against the literal current
formula and all independent-four-set, degree, partition and sorting conditions.
Every cut is checked independently before adding it. Kuratowski certificates
are reduced to K5/K3,3 subdivisions using the independent suppression checker.

An incremental solver's UNSAT triggers a fresh standalone native DRAT attempt
and drat-trim replay; no whole-stratum result until independent domain/encoding/
cut review. A planar survivor stops for independent witness validation.

Background cap is8h; one heavy process tree <=11GiB private commit. The source,
extension and native hashes, full gate, controls, runtime PIDs and progress are
durable under artifacts/tmp/S031, with unmerged WIP backup for source/records.
Actual outcome and claims remain pending the registered long campaign.
