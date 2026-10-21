# Read-only S032 progress analysis

Owner requested a separate progress analyser on 2026-10-21 because indefinite
runtime is impractical and preserving the live search is important.

Preregistered scope: read existing JSON/log prefixes and query process CPU times
with query-only Windows handles. No solver launch, source/runtime modification,
signal, debugger, suspension, termination, parameter change or checkpoint reload.
Keep one existing heavy worker. Output a diagnostic report, not a scientific
claim, coverage percentage, completion probability or estimated finish date.

Stream only the journal prefix present at entry; ignore an incomplete last line.
Separate intervals <=90 seconds from longer unobserved gaps. Such gaps alone
do not prove sleep; Windows power events independently established the overnight
battery sleep. Report observed-interval throughput and zero-new-rule stretches,
CPU activity over a short sample, private memory/disk, checkpoint age, final
result presence and live source hashes. Geometric counters are not all logical
search activity. They can stay flat while CaDiCaL works internally. Internal
conflict/decision/learned-clause counts are not exposed by this running build.

Use scripts/analyse_s032_progress.py; default output is under gitignored
artifacts/tmp/S032/analysis. Freeze a timestamped report under validation/S032
for WIP backup. No automatic stop or pause follows a diagnostic threshold.
Future instrumentation/partitioning/re-encoding would be a separate proposed
change, not something to inject into this healthy live solver.

First execution 2026-10-21T06:33Z: same registered native process consumed5 CPU
seconds in a5-second sample.14,289,002 partial checks,2,369,267 campaign geometric
rules, zero complete model checks. Recent3577s of observed intervals added777390
checks and121993 rules. Longest observed no-new-geometric-rule stretch9912s;
latest quiet stretch152s. The30854s overnight log gap was excluded. All frozen
source/runtime/native/input hashes matched. Synthetic quiet/burst/gap and
incomplete-journal-tail checks passed. No mathematical result or ETA follows.
