# S047 closeout

S047 CLOSED, decision PIVOT (PAUSE recommended), 29-30 October 2026.
Invoked by the owner in a cloud Claude Code conversation under D079/D047
("Yes, replace with new target, and do run the session now here"); the
previously queued calibration-gated mechanism trial was superseded unexecuted.
Executor: Claude Code on the web, cloud container (Linux x86_64, 4 CPUs).
No witness; 9 <= chi_2 <= 12.

Registration validation/S047/REGISTRATION.json (23:34:52 UTC) preceded every
experiment; post-hoc amendment A1 (23:42:08 UTC) followed E2's stop and
preceded every A1 run. Fresh full 271+K9 smoke PASS (validation/S047/
SMOKE.json). Experimental use 539.1 CPU s / 545.7 wall s of 1800/3600
(validation/S047/BUDGET.json).

Findings:

1. Logic. By compactness any refutation of H ("all biplanar graphs are
   9-colourable") implies a finite witness. Colour-transfer and gadget
   arguments are explicit constructions with human-readable certificates;
   only counting, fractional, probabilistic and topological routes are
   genuinely non-constructive.
2. Obstructions proved and mechanically checked: O1 no biplanarity-
   preserving operation can raise chi for every biplanar graph, so any
   transfer proof is one-shot (CLM-0152); O2 10-critical biplanar window
   ceil((88n-70)/18) <= m <= 6n-12 (CLM-0155); O3 no classical or
   generalised Mycielskian of a graph with chi >= 9 is biplanar (CLM-0154);
   O4 10-chromatic Schrijver graphs (k <= 3) are not biplanar, and the
   zig-zag theorem only forces the biplanar K5,5 (CLM-0156).
3. Seeded extensions of K6 v C5 (the only template test run): no biplanar
   graph with chi >= 10 contains K6 v C5 plus at most five vertices, by a
   short hand proof (vertex-minimality plus Euler counting) with
   drat-trim-verified computations as controls (CLM-0153). Six added
   vertices: A1 CEGAR capped at 240 s after 6189 learned colourings, every
   candidate 9-colourable; UNKNOWN (CLM-0157).
4. Prior art: Szeider (Sept 2026) already closes the alpha <= 2 counting
   route; no source on biplanarity of Mycielski-type graphs or on the
   fractional chromatic number of biplanar graphs was found.

Decision: PIVOT by the registered gate (exclusions only; no template with
calibrated positive evidence, no candidate). Recommendation: PAUSE. S048 is
a FUTURE/UNEXECUTED re-entry gate with an explicit written test for any new
route. The full prompt is byte-identical in authoritative/
NEXT_SESSION_PROMPT.md and sessions/S047/S048_FUTURE_PROMPT.md.

Evidence: sessions/S047/{INPUT,PLAN,RESEARCH,ADVERSARIAL,PRIOR_ART}.md;
validation/S047 (registration, amendment, smoke, controls, seed receipt,
ladders, CNF/DRAT archives, budget, entry context, manifest).
Portable check: python scripts/s047_checks.py (add --native locally to
regenerate the eager CNFs and re-run drat-trim on every archived proof).
Frozen pre-S047 checks replay against exact entry authority bytes via
scripts/s047_replay_history.py.

Integration: harness branch ccr-af80f6d5-2qearo, ordinary non-force commit,
entry main 7fb60e1119fed86d61f44b95390ae5311b5a5344; merging to main is the
owner's decision. Hosted CI runs on pushes to main and on pull requests, so
no hosted result exists for this branch: hosted status UNKNOWN; local runs of
the scaffold workflow steps are recorded in validation/S047/LOCAL_CI.json.
No S048, automation, Lean, publication, outreach or S035/S036/S045
resumption was performed.
