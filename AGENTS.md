# S036 IN_PROGRESS — machine limits, four concurrent residents, automatic recycling (23 October 2026)

Owner (17:05 UTC): "Recycle where needed but just raise the limits to whatever this
machine can handle." Limits: validation/S036/MACHINE_LIMITS.json (8 GiB aggregate /
3 GiB per solver hard, 1.25 GiB available floor, 7 GiB resident target). All four
residents execute concurrently; a resident that outgrows its limits is RECYCLED
(cooperative stop, audited cuts, new generation, new PID) instead of halting the run.
Hard-cap pauses resume only with prepare-resume --owner-authorized. Read
sessions/S036/RUNNING.md; live authority artifacts/tmp/S036/control.

# S036 IN_PROGRESS — S035 RAM identities LOST; fresh semantic-recovery residents (23 October 2026)

At 12:14 UTC the owner closed the ChatGPT app; all twelve S035 processes (launched
under Codex desktop) ended with it. Private CDCL for regions 0,7,127,255 is
unrecoverable; no SAT signal; evidence in validation/S036/identity-loss. Fresh
residents start from audited semantic state via scripts/s036_fresh_campaign.py.
S036 processes MUST be launched with scripts/s036_launch.py (WMI, outside any app
job object) so closing Claude Code/ChatGPT/terminals cannot end the search.
The section below is the historical adoption-stage header.

# S036 IN_PROGRESS — repaired SAT supervisor, retained-RAM long search (23 October 2026)

Owner "run next session" invoked S036 only (D047/D074; existing main, no branch/PR).
SAT-first entry audit found no scientific SAT/candidate/exit10; all twelve S035
identities survive suspended with exact thread sets. The S035 watcher failure is
repaired in NEW files (tools/s036_sat_scan.py, scripts/s036_sat_supervisor.py,
scripts/s036_resident_controller.py); S035 source bytes and artifacts stay frozen.
Live authority is artifacts/tmp/S036/control (ADOPTION, CONTROLLER, WATCHER,
GUARD_PAUSE, SAT_ALERT, COLD_SLOT); read sessions/S036/PLAN.md and RUNNING.md.
Never wake legacy controls, resume classified helpers, force-kill, evict or
duplicate; never auto-restart a paused controller. Cold slot is bounded and
registered (validation/S036/COLD_CAPACITY_PLAN.json). No S037 automatically.
247/256 encoded closures, nine UNKNOWN, S11 UNKNOWN; 9<=chi2<=12 unchanged.

# S035 CLOSED — S036 targeted long search FUTURE / UNEXECUTED (23 October2026)

Owner requested investigation/closeout and a next-session long-search prompt.
S035 stopped after SAT-watcher PermissionError on ADOPTION.json; all original
identities remain suspended and private learning is RAM-only. Controller/watcher
have exited; do not infer RUNNING from historical headers below. Read
sessions/S035/CLOSEOUT.md, FINAL_DIAGNOSTIC.md, RECOVERY_HANDOVER.md and the paired
authoritative/NEXT_SESSION_PROMPT.md / sessions/S035/S036_FUTURE_PROMPT.md.
No automatic resume, cold admission, helper/legacy wake or S036 execution in
this closeout. The next owner invocation authorises S036 repair/acceptance then
sustained search under its full prompt. S035 heartbeat disabled.9<=chi2<=12.

# S035 sustained search RUNNING (23 October2026)

The classified-thread repair and40s same-process validation passed; sustained
600s fair turns are now RUNNING, not merely planned. Read RESUME_CONTROL live
identities/leases and sessions/S035/RESUMED_RUNNING.md. Two active slots/four
retained original contexts; helpers and all legacy controls remain frozen.
No duplicate launch, cold admission, fresh heavy proof or S036. Older PAUSED
headers below are historical. The requested heartbeat remains paused.

# S035 authorised resumption — classified thread isolation repair (23 October2026)

Original solver threads may resume only after the newly published lifecycle
acceptance and fresh SAT supervisor gates pass. Extra threads were identified
from matching Microsoft symbols as ntdll!TppWorkerThread; their creator is not
established and they remain quarantined/suspended. Never resume those helpers,
legacy controls, or unclassified threads. Read sessions/S035/THREAD_REPAIR.md
and the live RESUME_CONTROL authority. S036 remains unauthorised. The headers
below are historical; actual RUNNING requires live controller/watcher identities.

# S035 recovery authorised; preserved pause at thread identity gate (22 October2026)

Full recovery and the120s same-process pilot passed. Sustained search has NOT
begun: additional thread identities and inconsistent Windows status labels
blocked safe rearm. All original PID/create identities survive, sampled threads
have positive suspend counts and measured CPU is zero. Preserve RAM; no blind
resume, legacy recovery, force termination or S036. Read
sessions/S035/RECOVERY_BLOCKED.md. Owner continuation is already authorised.
Next check-in ONLY23 October07:30 Europe/London; earlier times are superseded.

# S035 OWNER PAUSED (22 October2026)

Preservation/SAT-first owner directive supersedes running instructions below.
All campaign processes are SUSPENDED, STOP latched; no heavy computation or
S036 is authorised. Use scripts/s035_pause_status.py and sessions/S035/PAUSE.md.
Do not call legacy recover/STOP or blindly resume guardian: those paths force
terminate processes. RAM learning survives only in the suspended identities.
Read the identical authoritative/S035 RESUME prompt before future work.

# S035 resident upgrade ACTIVE (22 October2026)

Owner requested flat-counter investigation and preservation of useful learning.
Use scripts/s035_resident_campaign.py for current status/STOP. Two active slots;
additional per-region native processes may be intentionally PARKED with RAM CDCL
retained between fair turns. Inspect RESIDENT_CONTEXTS.json and PID/create-time
identities before any action. Keep hard memory/disk safeguards and proof gates.
Original launch handoff below is historical; current details in sessions/S035/RUNNING.md
and validation/S035/resident/. No S036 authorization.

# S035 IN_PROGRESS - Windows multiple-worker invocation (22 October2026)

Owner invoked S035 with power/wifi/no-sleep conditions. Fresh Windows acceptance,
measured1/2/3-worker trials then sustained multiple workers with resource guards.
No fixed overall cutoff; stop on owner STOP or actual unsafe/blocking condition.
Existing main, ordinary non-force publication; no new branch/PR. Inspect actual
S035 guardian/controller and PID/create-time identities before any launch. S036
not authorised. Last completed S034;9<=chi2<=12 unchanged. See sessions/S035/PLAN.md.

# S034 completed — S035 Windows multiple-worker continuation queued (D074)

S034 phone campaign stopped safely at22 October2026,00:01:43 UTC for disk reserve.
102 visits;16 encoded regions proof-closed,240 unresolved;93047 checked new
geometric clause occurrences. No graph/stratum/headline advance;9..12 unchanged.
Results archived losslessly. S035 is FUTURE/UNEXECUTED on the Windows laptop:
fresh Windows acceptance/port, storage controls and measured multiple workers.
Owner's next invocation authorises S035; do not launch it on this phone or run
S036 automatically. See authoritative/NEXT_SESSION_PROMPT.md and D074.

# D072 (2026-10-21) — phone ARM64 environment test; current S033 authority

The ACTIVE NEXT SESSION is now **S033: Samsung Galaxy S24 / Termux / Debian (proot) ARM64 port and verification**. S033 is setup plus rigorous validation, NOT the D071 parallel SAT campaign. Move D071's planned genuine worker/parallel search to S034 after phone validation. Owner will make an ordinary full clone, accepting ~1.5GB data, and wants NO new project, repo, development branch or PR. Phone experiment works in this repository on 'main' using normal non-force Git commits/push where allowed; this narrowly overrides old branch/PR session protocol but NEVER mathematical certification or archive integrity. Existing Windows/laptop solver is retained; phone adjustments reversible using 'git revert'. Saying "run next session" in the clone invokes S033 under D047; do not run S034 automatically. See authoritative/NEXT_SESSION_PROMPT.md and docs/D072_S033_PHONE_TEST_DIRECTIVE.json.

# D070 S032 OWNER STOP — preserve rules and rebuild progress tools

The owner stopped S032 on2026-10-21. All2579937 geometric rules are archived and independently checked. Monitor PAUSED. S032 closeout complete; rebuilt progress tools tested. No long search restart or S033 without fresh owner invocation. See docs/D070_S032_OWNER_STOP_AND_PROGRESS_REBUILD.md.

# D069 S032 runs until stop — no eight-hour cutoff

Latest owner instruction removes the fixed S032 wall limit. Keep one11GiB worker,10GiB disk reserve, checkpoints/monitoring and independent proof gates. See docs/D069_S032_NO_FIXED_WALL_LIMIT.md. S032 ONLY; S033 still requires fresh invocation.

# D068 S032 invoked — IN_PROGRESS (2026-10-20)

Owner "Okay, run next session" invokes S032 only under D047. See docs/D068_S032_INVOCATION.md and sessions/S032/PLAN.md. S031 remains last completed; no S033 authorization. Do not duplicate a running heavy process.

# D067 S031 completed (2026-10-20; eight-hour persistent S11 cap)

46 relaxation models independently audited;28692s persistent search;1809 checked cuts (1114 inherited,695 new); S11 m155/156 UNKNOWN; S10/S9/S8 NOT_RUN; no certified stratum or chi>=10 witness;9<=chi2<=12. Full fresh271+K9 smoke/controls PASS. D066 S031-only scope is discharged by closeout; S032 FUTURE/UNEXECUTED requires fresh invocation. Parked queues and all scientific/publication gates unchanged.

# D066 owner scope update (2026-10-19): S031 ONLY

Continue the running S031 eight-hour campaign, monitoring and required closeout;
then stop. D066 supersedes D065 successive-session authorization. Do not run
S032 or any later session without a fresh owner invocation. See
docs/D066_S031_ONLY.md. Disable the scheduled monitor after S031 closes.

# D065 owner long-run authorization (2026-10-19; S031 IN_PROGRESS)

Owner explicitly authorized S031 and successive numbered sessions until context
or usage allowance runs out, prioritizing long runs left working and checked
after hours. See docs/D065_LONG_RUN_AUTHORIZATION.md and sessions/S031/RUNNING.md.
This supersedes earlier stop-before-next gates for this campaign; all scientific,
integration, parked-queue and publication gates remain. S031 is RUNNING, not
closed. Check actual PIDs/checkpoints before starting any worker; never duplicate
the active heavy process. Last completed session remains S030.

# D064 S030 completed (2026-10-19; bounded OP1(b), no stratum decision)

44 SAT relaxation models independently audited; 1181.281s registered serial search; S11 m155/156 UNKNOWN; S10/S9 NOT_RUN; no certified stratum or chi>=10 witness;9<=chi2<=12. Full local271+K9 smoke PASS; executor Codex desktop. Paper59 finite RUP branches replayed, hand coverage not independently re-proved. S031 FUTURE/UNEXECUTED: persistent certified S11 continuation. Older queues remain PARKED.

# D063 S029 completed (2026-10-19; literature only)

S029 (owner "run next session", cloud Claude Code) froze the prior-art/landscape baseline (research/S029_LANDSCAPE.md; validation/S029/LANDSCAPE_FREEZE.json). GO-MODIFIED: **S030 = certified two-sided decision of Gethner–Sulanke OP1(b), i.e. biplanar graphs on 28 vertices with alpha<=3 (each one is a chi>=10 witness)**, stratified by minimum degree. Lemma F is superseded (n<=30 via Szeider; n<=28 claimed by rStation paper 59). T3 for 21<=n<=27 is PARKED. The old S029 queue stays PARKED. No chi>=10 witness; 9<=chi2<=12. S030 FUTURE/UNEXECUTED. Historical instructions below retain their original scopes.

# D062 owner pivot (2026-10-19; governance only, no session executed)

After an S001–S028 review the owner pivoted: **S029 = prior-art and current-landscape audit, rStation r/earth_moon first, literature only, output FROZEN**; **S030 = the alpha<=3 finite programme** (T3: biplanar with alpha<=3 implies 9-colourable, or a chi>=10 witness; finite by Lemma F, n<=36), drafted in docs/D062_LANDSCAPE_THEN_ALPHA3_DIRECTIVE.md and finalised by S029. The certified exhaustive search of that finite domain is authorised for S030 when invoked; no universal upper-bound work beyond it. The old S029 obstruction-closure queue is PARKED with statuses unchanged (sessions/S028/S029_FUTURE_PROMPT.md (frozen S028 text, superseded by D062)). No chi>=10 witness; 9<=chi2<=12. Historical instructions below retain their original scopes.

# S028 completed authority update D061 (2026-10-19)

S028 (owner "run next session", local Claude Code, full smoke PASS; stopped early at owner request): deletion descent certified 13 new clique blow-up obstructions down to 18 vertices (D036 = GJaVBo[7,3,2,2,1,1,1,1]); all 4 S027 admitted UNKNOWN and 71/78 surplus graphs excluded by checked certified-subgraph maps; 16/30 seed-270018 profiles closed by checked DRAT; S028 queue 1 UNKNOWN, 12 NOT_RUN. No chi>=10 biplanar witness; 9<=chi2<=12. S029 FUTURE/UNEXECUTED. Push/PR via the owner's Git Credential Manager account jfairfaxball-348 (gh helper shadows it). Historical instructions below retain their original scopes.

# S027 completed authority update D060 (2026-10-19)

S027 (owner "run next session", local Claude Code, full 271+K9 smoke PASS): learned certified-obstruction support clauses close 13/30 alpha3 28-vertex clique blow-up profiles by checked native DRAT (CLM-0103); 1831 models, 84 filter-clean; 3 new certified obstructions (27v P29 deletion, P26-B11-0051, P27-B12-0040; CLM-0104); admitted P10-B10-0001, P11-B10-0067, P20-B11-0070, P22-B11-0043 BIPLANARITY_UNKNOWN; C5 sum17 now 24/26 certified (CLM-0105), C5[3,3,4,3,4] and C5[3,3,3,4,4] UNKNOWN. No chi>=10 biplanar witness; 9<=chi2<=12. S028 (obstruction-closure loop) is FUTURE/UNEXECUTED. Each future invoked session must establish its own full smoke and record its executor. Historical instructions below retain their original scopes.

# S026 completed authority update D059 (2026-10-18)

S026: 3 additional C5 negatives certified; 21/26 sum17 classes certified, 5 UNKNOWN. 2185 source models,2180 checked obstruction maps,one initial filter timeout,four initially admitted and all four NON-BIPLANAR by new certified C5 maps;72 independent old18 absence DRAT proofs. No chi>=10 biplanar witness;9<=chi2<=12. P29-B14-0001 is a fifth admitted candidate:28 vertices,154 edges,alpha3,omega8,chi>=10 by counting;21 native DRAT proofs certify absence of all currently certified C5 obstructions. Its biplanarity verdict is NONBIPLANAR_CERTIFIED. All5 remaining C5 classes also have native DRAT absence proofs. Thus P29 avoids all26 sum17 classes, yet is NON-BIPLANAR_CERTIFIED. All2185 generated source models are now excluded; generator profiles remain capped, not exhaustive. S027 is FUTURE/UNEXECUTED. Owner explicitly authorised local laptop execution through Codex for S026; each future invoked session must establish its own full smoke. Historical instructions below retain their original scopes.

# S025 authority update D058 (2026-10-16)
S025 was DIRECTLY invoked by the owner's "run next session" and ran on the owner's LOCAL workstation, with a full 271+K9 smoke PASS first. DRAT-certified 17-vertex C5 clique blow-up obstructions (via Lemma C K9-minor CEGAR, CLM-0090..0094) settle ALL 219 former BIPLANARITY_UNKNOWN original rows. The original 271 corpus is entirely NON-BIPLANAR, so the D051/D054 original-219 priority (rules 17-19 below) is DISCHARGED by complete decision (D058). D042 lower-only is unchanged; there is no chi>=10 witness and 9<=chi_2<=12. S026 is FUTURE/UNEXECUTED (obstruction-aware candidate generation) and runs only on the owner's next invocation (D047). Local-run permission was for S025 only.

PR31's earlier D058 queued directive is retained as historical authority in docs/S025_219_GAP_CLOSURE_DIRECTIVE.md; its original219 priority is discharged by the completed decisions above. S025's original execution prompt/entry provenance is preserved, not retroactively replaced. Integration reconciliation is documented in docs/S025_INTEGRATION_RECONCILIATION.md.

# S024 authority update D057 (2026-10-16)
S024 was DIRECTLY invoked by owner's 'Run next session', adopting D057 session-only relaxation of original219 row148 EXCLUSIVITY to run planar-first positive search AND a global row148 exact specification. D042 lower-only target never suspended in S024. S024 is complete; D056 S023 exception is historical. Do not automatically extend D057 to S025; the queued S025 prompt explicitly asks to justify arms and retains every original219 UNKNOWN. Science run38862555457 yielded 17 real disjoint maximal-planar unions ALL proper <=8-colourable (no chi10 advance); row148 global UNKNOWN. D047 owner direct next-session invocation is sufficient.

# Binding programme instructions

**D056 OWNER S023 OVERRIDE (2026-10-15; FUTURE/UNEXECUTED):** S023 is now an upper-vs-lower research audit: explicitly investigate chi_2<=11 as well as chi_2>=10. For exactly S023, this supersedes the D042 upper-bound ban and D051/D054 graph148-only search priority below. Preserve all graph148/original219 certificates and UNKNOWN statuses. This is not a permanent programme re-scope or authorisation to publish/formalise. See docs/S023_BOUND_COMPARISON_DIRECTIVE.md and authoritative/NEXT_SESSION_PROMPT.md. D047 direct invocation applies.


1. **Single authority:** independently read live remote main (SHA, tree, status), then authoritative/STATE.json, this file, START_HERE and the session protocol; reconcile competing PRs, workflows, branches and records before writes.
2. **Headline (owner re-scope D042, 2026-10-14):** raise the Earth–Moon LOWER bound from χ₂ > 8 (i.e. χ₂ ≥ 9, classical) to **χ₂ > 9 (i.e. χ₂ ≥ 10)** by a fully certified construction of a finite simple biplanar graph with χ ≥ 10 (thickness ≤ 2, not geometric thickness or another variant). Resolving EMP and improving the upper bound 12 are OUT OF SCOPE. A certified χ ≥ 10 witness is a lower-bound advance, never a full resolution of EMP.
3. **Session-prompt-as-invocation (D047):** when the owner supplies, pastes or links a numbered session prompt as a request, that submission itself authorises immediate execution of exactly that numbered session. Do NOT require a second 'Run S###' utterance or ask for confirmation merely because a saved prompt was marked FUTURE/UNEXECUTED. A queued future prompt is not executed *automatically* without the owner's message; never execute the following session within the current one. Preserve D042 scientific scope.
4. **Sources:** assign SRC-#### with DOI/URL, date, author and honest access grade (METADATA_ONLY, ABSTRACT_INSPECTED, STATEMENT_INSPECTED, PROOF_INSPECTED, SECONDARY_ONLY). A search excerpt/aggregator is not proof inspection; proactively check recent work, including 2026 work.
5. **Claims:** assign CLM-#### with one status SOURCE_STATED, PROGRAMME_PROVED, COMPUTED_EXACT, HEURISTIC, FORMALLY_CERTIFIED or INHERITED_UNVERIFIED. No unsupported promotion or novelty guarantee.
6. **Construction requirements:** explicit labelled V,E1,E2 (edge-disjoint), planarity for EACH layer, verified proper k-colouring, rigorous proof of non-(k−1)-colourability. A feasible k-colouring is an UPPER bound, never a lower bound. A SAT solver's UNSAT text without a checked proof does not certify noncolourability.
7. **Upper bound out of scope:** no session works on universal colouring theorems, discharging, reducibility or upper-bound critical-graph routes. Earlier upper-bound claims stay recorded as history and are neither extended nor relied on. Structural facts already proved (e.g. forbidden subgraphs such as K₉, K₆,₉ or a K₇ with five common outside neighbours) may be used only as filters that discard construction candidates. A finite computation proves only its stated finite domain.
8. **Computations:** pre-register ranges, symmetry reductions, search completeness, independent validation, environments, commands, hashes, proof certificates (e.g. LRAT/DRAT with checker) and stopping criteria. No private uncheckable 'solver says no' claims.
9. **Formalisation:** Lean 4 with pinned mathlib and a clean reproducible build, no sorry/admit or unexplained axioms/oracles. Formal statement must be genuinely equivalent to the claimed result and must not bury key assumptions in unreviewed instances.
10. **Research freedom:** in mathematics sessions pursue multiple substantial construction routes towards a certified χ ≥ 10 biplanar graph; aggressively disprove false sublemmas and pivot when blocked. Prioritise a certified witness, or a genuinely new candidate source, over accumulating capped UNKNOWNs or low-value fragments.
11. **Research records:** maintain synced sources/claims MD+JSON, state, phase/session/decision/failure ledgers, campaign registry and every session's INPUT/PLAN/RESEARCH/ADVERSARIAL/CLOSEOUT.
12. **GitHub:** one isolated session branch, one atomic authored session commit, ordinary PR, non-force merge (no squash/rebase if two-parent merge available), and independent verification of main and parents. Zero hosted checks ≠ CI PASS; unavailable endpoints → UNKNOWN. In cloud sessions the harness-assigned branch is the session branch, reset to live main at session start; never-merged `wip/` backup branches are allowed (docs/CLOUD_ENVIRONMENT.md).
13. **Publication ethics:** genuine novelty and priority checks twice, attribution, no misrepresentation of previous 9-critical constructions. Palomar, arXiv, journal, external correspondence and announcements require separate explicit owner authorisation.
14. Do not invent citations, embeddings, SAT certificates, hashes, PRs, CI results, proof checks or claims that EMP is resolved or that χ₂ ≥ 10 is established.
15. **Execution environment (D043):** sessions run in Claude Code cloud containers set up by `.claude/hooks/session-start.sh` → `scripts/cloud_setup.sh`. Before any scientific computation run `scripts/cloud_smoke.py`; a FAIL blocks computation. Follow docs/CLOUD_ENVIRONMENT.md for pins, resource caps and persistence.

16. **Owner-required final handover:** every completed numbered session MUST commit a complete `authoritative/NEXT_SESSION_PROMPT.md` and an identical session-local future prompt, and output the **full next session prompt** with the user-visible closeout report and verified commit/PR/merge links. A queued next prompt is FUTURE/UNEXECUTED until the owner SUPPLIES it as the next instruction; that act alone is invocation (D047). Record GitHub Actions alternate runner details and permanent evidence so the next session never has to rediscover them.

17. **D051 original-219 priority (set before S015; remains binding through S017):** user's explicit direction is to RETURN TO ALL 219 original fixed exact10-chromatic biplanarity-UNKNOWN candidates BEFORE switching back to alternative constructions. If local checkout/hook unavailable, D044 verified GitHub Actions runner is valid and MUST be attempted with SAME-JOB setup and full smoke before declaring computational work blocked. S011 already completed only 438 greedy attempts/25 repairs, NO negative exclusion. Do not claim a finite trial settles UNKNOWN, and retain unresolved originals for S016 without owner-approved change of priorities. Updating the queued S015 prompt is NOT execution of S015.

18. **After S016 (2026-10-15):** CAM0018 completed same-job cold smoke on run38709598417, four exact original rows capped UNKNOWN, eleven positive searched without a full split. New nearest incomplete partial row148 has 10 original edges missing. No new checked graph verdict; overall original219 still UNKNOWN, χ₂ classical9..12. CLM0081 necessary planar density balance is proved but NOT applied as a SAT CNF in S016. Queued S017 must prioritise a genuinely changed checked cardinality/embedding-aware exact original-decision method before another new construction pivot. Always close S017 with full S018 prompt and verified GitHub links.

19. **D054 serial original-219 decision priority (owner, 2026-10-15; QUEUED S018 ONLY, NOT EXECUTED):** Keep original219 UNKNOWN graphs as exclusive active candidate source, one original graph at a time and one heavy ≤12GiB worker, starting row148 with S016 archived10-unplaced partial. Prioritise complete exact biplanarity split and independent non9 proof or proof-checked full negative, not 5-row repeated short caps. If capped, profile/fix the solver and preserve resumable checkpoints/UNKNOWN, carry same graph into next session unless documented objective reason to switch; no automatic pivot to new construction families. Same-job full pinned D043 smoke with D044 Actions fallback. Authoritative details: docs/S018_SERIAL_219_DIRECTIVE.md; identical queued S018 prompts in authoritative/ and sessions/S017/. This is governance, no new proof.
