# S018 row148 science: permanent evidence and replay

The 2026-10-15 NEW hosted Actions job [run38721673690](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/38721673690), job116377478891 passed all setup, all 271 exact original chromatic CNF/DRAT and old+fresh K9 smoke, scientific step, WIP persistence and artifact upload. Source initial WIP commit a7c0355f01076bee7e8202e9fb4f1d7c7ea5d367. WIP observation commit65d78133bbbadee5e71d7e5fa27d59cd0511f9ae. Raw evidence is copied verbatim by Git blob into this committed folder without merging WIP history.

- REMOTE_RESULT.json: all 219 indexed original rows, original/source/native hashes, bounded runtime, positive and exact results.
- REMOTE_SMOKE.json and ENVIRONMENT.json: genuine full same-job smoke output and pinned native SHA256.
- row148_best_partial.json: EXACT original row148 n25,m131, placed E1=62 E2=63, missing six edges (0,1),(0,10),(5,7),(12,16),(17,24),(21,23). Independent planar checks on each partial were run; still NOT a biplanar witness.
- row148_lemmas.json.gz: 19480 exact original-row nolex Kuratowski-obstruction edge sets, saved and compressed. WIP Git blob SHA 9e5d233c9826deec0e1af08c66cd4d87bba61702, *not* a SHA256 digest. Independently recheck that every obstruction is a subdivision and graph subset before replay.
- SUMMARY.json: cumulative original52 certified nonbiplanar plus219 unknown and session-specific CAPPED1/NOT_RUN218 ledger.

The original row148 edges must be rebuilt via tools/blowup_graph.py from validation/S003/survivors_alpha_ge3.json row148, yielding SHA256 4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598. For resumption, copy the saved partial and compressed lemmas to validation/S018-WIP/ paths on the NEW never-merged WIP branch, then run a NEW pinned setup and complete 271+K9 smoke before science, one ≤12GiB worker. Existing tools/s018_serial_148.py reads these WIP paths but rebuilding the stronger embedding/triangulation-cover search of S019 is preferred to merely continuing old slow cuts. Do not promote UNKNOWN to NONBIPLANAR without a fresh full CNF and independently checked native proof.

Ephemeral artifact ZIP id11966338990, verified ZIP digest SHA256 e55a58d9f29477728fc5cf43890ffbe5fda9c2d78d480e0bb66dd1b1776dfd46, available via science run artifacts; permanent files above survive its expiry.
