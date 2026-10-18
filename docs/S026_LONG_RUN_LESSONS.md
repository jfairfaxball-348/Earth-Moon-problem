# Davenport S110 long-run lessons applied to Earth–Moon

Owner request during S026,2026-10-18: inspect yesterday's8+hour Davenport run and
copy useful operational lessons. Read-only inspection of C:/Davenport-Counterexample-Hunt;
no Davenport execution or modification. The chat was **Explain S110 Computation**.
Live Davenport local mainda61638 contains S110 completed, plus later governance.

## Observed evidence

- sessions/S110/activation_utc.txt:2026-10-17T14:23:30Z through
  2026-10-18T00:49:43Z (10h26m13s wall). Closeout records approximately146CPU-h,
  versus72 estimated. These are different cost measures.
- run_campaigns.sh fixes56 jobs:14 shards per algorithm for two campaigns,
  at most14 simultaneous workers,43200s external cap per shard, exit/start/end
  receipts in job_exits.txt.
- support5_a.py and support5_b.py flush JSONL progress every20000 evaluated
  objects, immediately log threshold hits, and finish with an `end` record.
- aggregate_results.py requires every shard's exit0, final output, `end` marker
  and exact registered coverage total. It cross-checks two distinct algorithms,
  maxima, attained optimum-value sets and zero threshold hits. Log hashes are
  committed. It does NOT compare equal per-value histogram multiplicities,
  because the two representative systems are different.
- REVIEW.md explicitly retains shared reduction/trust assumptions, same-executor
  review and absentCI. Coverage is only support<=5 atn15/20, not Davenport's
  universal question. No scientific conclusion is imported into Earth–Moon.

## Copy here

Use stable, small work-unit IDs (weight profile; graph; search; regeneration;
proof solve; proof check). Keep source/input/native hashes and exact command
before activation. Write flushed start/heartbeat/end journal records; atomically
replace summary JSON. Keep the ordered queue and externally enforce wall/RSS caps
over the process tree. Distinguish process completion from checked mathematics.

`tools/s026_supervision.py` supplies the serial supervisor and durable writes.
It is introduced AFTER WIPfe92ca8 was launched: that immutable run did not use this
later helper. Its source pin and observed supervision limitations remain recorded.
Use the helper for a registered continuation/next session, with its own source pin
and full same-job smoke. Do not rewrite the history of a running experiment.

Resume only a verified finished work unit or an explicitly saved solver checkpoint.
Davenport's JSONL progress records were NOT automatic mid-shard resumption: neither
algorithm reads the progress log to restart at the recorded index. Earth–Moon must
save CEGAR clause/lemma sets, generated CNFs, proof logs and solver inputs; a count
alone cannot resume a SAT state. Already completed certificates must be skipped
only after their full input/source/proof byte chain is validated.

Do NOT copy14 simultaneous workers: one heavy<=12GiB worker remains binding here.
For bounded graph/class queues, completed/total counts are meaningful. For a capped
heuristic or an unbounded SAT call, elapsed time and clause counts are telemetry,
never a completion percentage or proof progress. A green job/exit0 is insufficient:
only full explicit split checks or clause justification+byte regeneration+checked
native DRAT permits a graph verdict. Missing end/checkpoint/proof means UNKNOWN.

The Windows stay_awake.ps1 was a process-scoped inhibitor restored on exit, not a
permanent power setting. GitHub-hosted runners do not need this local helper.
Budget overruns using measured per-unit timings and retain an honest cap/queue;
do not silently replace expected coverage with the amount that happened to finish.
