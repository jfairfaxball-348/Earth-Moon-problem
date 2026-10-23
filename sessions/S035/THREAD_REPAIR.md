# S035 thread isolation repair —23 October2026

Owner said Continue after learning sustained search had not run overnight.
Entry main c92e671598985a473f2f097932508cd15e1d2026 and hosted
run39864836597 were verified. No original worker was replaced, killed or reset.

Read-only query of Windows thread start addresses, the exact ntdll CodeView
GUID/age and matching public Microsoft PDB resolves every later-created entry
point to TppWorkerThread with zero symbol displacement. Remote entry code bytes
match the local Microsoft-signed ntdll. Their creator is NOT established; no
permission to execute these helper threads is inferred. Classification evidence
and exact identities are in validation/S035/thread-repair/THREAD_POLICY.json.

The gate repair uses the dynamically queried ThreadSuspendCount rather than
psutil's process status label. A query failure closes the gate. Original native
thread IDs/create times remain the only resumable threads; the newly classified
helpers and all legacy threads stay suspended. Exact thread-set changes stop
progress for classification; nothing automatically admits another helper.
The original source and manifest bytes remain in frozen-source/*.bytes.

Fresh disposable controls passed nested counts1/2, unchanged identity, three
isolated turns with helper counters frozen and original counters increasing,
wrong identity rejection, natural exits0/10/20, real four-resident/two-slot
scheduling, preservation STOP and classified metadata-only pilot rearm. Renewed
real SAT interruption, STOP races, validation failure and lost/stale controller
controls also passed. A3.2s scheduler fixture was too short under filesystem
sampling overhead; its assertion was retained as a fixture failure and the
8s fresh control passed. No scientific process ran during these controls.

Before retained processes resume, publish this source and acceptance to existing
main, verify remote bytes, pin the policy hash and start the independent SAT
supervisor. Run a40s same-process validation, then archive ONLY the separate
pilot control records and start an unbounded600s fair-turn continuation under
fresh supervisor/controller identities. Original STOP and old controls remain
frozen. No new solver, cold admission, heavy proof generation or S036.

Hard caps6GiB aggregate/2GiB per worker,2GiB RAM floor,10GiB disk reserve,
2GiB raw proof attempt and40/64GiB campaign/total S035 remain. Soft pressure
pauses preserve RAM; thermal visibility is unavailable. SAT overrides UNKNOWN
and STOP; native UNSAT still needs a fresh independently checked proof.247 encoded
closures and nine UNKNOWN regions do not establish graph/stratum/headline progress.

Technical references:
https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationthread
https://microsoft.github.io/windows-docs-rs/doc/windows/Wdk/System/Threading/constant.ThreadSuspendCount.html
The exact Microsoft symbol URL/hash is retained in SYMBOL_CLASSIFICATION.json.
