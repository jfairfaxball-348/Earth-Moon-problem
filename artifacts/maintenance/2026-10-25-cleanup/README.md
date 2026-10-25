# Owner-authorised disk cleanup, 25 October 2026

Maintenance only. S046 remains closed and S047 remains future/unexecuted.
No solver is started, no mathematical status changes, and no Git history is
rewritten. The owner requested removal of unnecessary disk usage.

Entry: main and freshly fetched origin/main both
`fe03d005659d53c76dc522d293a06dc165ff8c29`; working tree initially clean.
Initial measured file content: 88,798,175,423 bytes in 111,567 files.

Outcome: 1,514 duplicate files removed and 371 remaining large scratch files
losslessly compressed. Reclaimed 66,764,531,941 bytes (62.18 GiB). Final
measured project content was 22,034,982,917 bytes (20.52 GiB), with 110,061
files; C: had 85,116,854,272 bytes (79.27 GiB) free. These measurements precede
the small maintenance commit. Receipt reconciliation passed: every removed
original was absent and every retained recovery source was present.

`scripts/cleanup_redundant_scratch.py` removes only files under the resolved
`artifacts/tmp` root. Every deleted duplicate matches the size and SHA256 of
contents read from a retained archive during this maintenance. Gzip archives
are read to EOF, checking CRC. The S034 archive is independently streamed
through its existing verifier. The S035 pause archive is streamed through
the bounded-handle verifier, including original gzip reconstruction hashes.
Original compressed archives, certificates, source, research records and Git
history are retained.

`REMOVED.jsonl` records verification before deletion and successful deletion,
with the original path, hash, size and retained recovery source. The SUMMARY
files give totals for each pass. These commands are maintenance operations,
not scientific experiments:

```
python scripts/cleanup_redundant_scratch.py
python scripts/cleanup_redundant_scratch.py --s035
python scripts/cleanup_redundant_scratch.py --compress
```

The compression pass preserves remaining large text scratch as adjacent
`*.cleanup.gz` files. Each compressed file is read back completely and its
decoded size/SHA256 checked against the original before deleting the original.
`COMPRESSED.jsonl` records both paths. Recover by gzip-decompressing the
retained file to its recorded original path. Recovery may require substantial
free space. Historical scratch-path references may require this recovery;
the committed certificate archives and frozen research sources are unchanged.

This cleanup is lossless for recorded proof and scratch content. It does not
make claims about mathematical proof replay or hosted CI.
