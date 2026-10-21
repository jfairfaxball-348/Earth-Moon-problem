# S032 progress tools — stopped, no automatic restart

The owner stopped the campaign under D070. The original process is gone.
All2579937 saved geometric clauses passed independent subdivision checking;
the lossless archive is validation/S032/stopped/learned.lem.gz, SHA256 of
uncompressed bytes6e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177.
The original input, old executable and source/runtime pins remain archived.
Private CDCL state was not saved. Monitor PAUSED. Do not resume automatically.

## A report you can run without starting any solver

From C:\Earth-Moon-problem:

```powershell
.venv/Scripts/python.exe scripts/s032_coverage.py report
```

This reads the local ledger and verifies archived certificate hashes. It reports
exact combinatorial weights of disjoint graph-presence regions that have been
closed by a checked UNSAT proof, and the remaining unclosed weight. The default
partition uses8 free graph-edge variables, giving256 regions. Their weights
are unequal because the total edge count must be155 or156. Layer assignments
and auxiliary variables are existential, so graphs are not multiply counted
just because they have multiple splits or counter encodings.

The raw count before other restrictions is
C(378,155)+C(378,156), approximately1.3306e110. The denominator used in the
ledger is smaller: graph unit pins in the registered canonical encoder leave
approximately9.6253e101 edge sets before its other requirements. The partition
weights sum exactly to this denominator. This is not the count of feasible
graphs, or all unlabelled graphs. Symmetry pins/sorting can exclude differently
labelled copies without proving those graphs nonbiplanar.

The initial real demonstration checks cell128. It has a standalone checked
UNSAT proof both WITHOUT and WITH the retained campaign rules: its closure is
already implied by baseline constraints. This is an encoding-region closure,
not a new mathematical graph exclusion or a measured benefit from the new
rules. One of256 regions is closed, weighted0.9685672240percent. The other255
are unclosed, not proven feasible. The first augmented proof-check attempt hit
15s and was correctly left UNKNOWN; its later60s replay/check succeeded.

## Explicit bounded proof check, only when you choose to spend CPU

```powershell
.venv/Scripts/python.exe scripts/s032_coverage.py check --cell 0 --seconds 60
```

This is a new bounded standalone proof job, NOT the stopped native campaign.
It checks base+retained rules under that region's graph prefix and then checks
DRAT if UNSAT. Each solve/check phase has the specified ceiling,11GiB aggregate
private-memory cap and10GiB disk reserve. Caps, failed proofs and SAT of this
relaxation do not close a region. The original saved rule file is only read.
The command refuses to run while the campaign ACTIVE.lock exists and uses its
own exclusive ledger lock. It retains failed/capped attempt evidence.

Region work already certified stays in the ledger across interruptions. That
is completed-domain information; private CDCL state within a capped region
is not retained. Small regions are not guaranteed to finish quickly.

## Instrumented native successor

`scripts/build_s032_progress_native.py` builds to the separate directory
artifacts/tmp/S032/native-progress. It does not overwrite the original native
executable. It adds30-second and final CaDiCaL conflicts/decisions/propagations
counters to the existing geometric telemetry, with no formula restriction.
The bounded controls include1024 exhaustive fixed n5 graphs, fixed K33,
positive24 and a2s free-K9 telemetry stress (UNKNOWN, not a negative proof).

For a future owner-invoked campaign, `s032_coverage.py export --cell N` writes
the exact region instance including retained clauses and graph-prefix units,
but starts no solver. A region worker would use the rebuilt executable with
that input and a fresh per-region lemma file. Its new global geometric clauses
can be independently audited and included in a region proof using
`check --cell N --extra-lemmas PATH --seconds SECONDS` AFTER that worker stops.
Native UNSAT alone never closes the region. Native SAT stops for full independent
assignment/planarity/embedding/alpha/colouring/counting witness verification.
This future workflow is not a resumed run or authorisation to start one now.

## What the tools cannot honestly report

A geometric clause forbids a set of edges being together in ONE layer. The
same union graph might still admit another split. Counting graphs excluded
solely by all retained clauses requires projected model counting: count graph
edge sets for which NO compatible split/auxiliary assignment survives. It is
not the sum of clause counts or clause sizes, and generally needs substantial
additional computation. The bounded ledger supplies checkable lower bounds
on closed encoded regions, not that complete projected count.

The base-only ledger is available using
`report --directory artifacts/tmp/S032/coverage-base`. Comparing matching
baseline/augmented regions distinguishes closure already implied by the initial
encoding from possible incremental help by retained rules; only full projected
counts would give an exact incremental excluded-graph count.

Neither internal counters nor a high closed-region percentage gives an ETA.
A witness may occur in any remaining region; the final region might dominate
the runtime. scripts/analyse_s032_progress.py remains an activity diagnostic
for historical journal/CPU observations, not coverage. No long search has been
restarted, and no S033 has been executed.
