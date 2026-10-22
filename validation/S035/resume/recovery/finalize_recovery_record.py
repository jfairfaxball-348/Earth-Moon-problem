"""Write a static receipt after the full preservation-only recovery succeeds."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
AREA = Path(__file__).resolve().parent
PAUSE = ROOT/'validation/S035/pause'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


report = json.loads((AREA/'REPORT.json').read_text())
assert report['status'] == 'PASS_ALL_ARCHIVE_BYTES_AND_FRESH_FULL_RESTORE'
inventory = json.loads((PAUSE/'RUNTIME_INVENTORY.json').read_text())
source_manifest = json.loads((PAUSE/'MANIFEST.json').read_text())
for name, row in source_manifest['files'].items():
    p = ROOT/name
    assert p.stat().st_size == row['bytes'] and digest(p) == row['sha256'], name
root = Path(report['recovery_root'])
deps = Path(report['dependencies']['root'])
files = [p for p in root.rglob('*') if p.is_file()]
free = shutil.disk_usage(root.parent).free
assert free > 10*1024**3
result = dict(status='PASS_PRESERVATION_ONLY_FULL_RESTORE',
              recovery_root=str(root), dependencies_root=str(deps),
              recovery_files=len(files), recovery_bytes=sum(p.stat().st_size for p in files),
              exact_object_count=len(inventory['objects']),
              exact_S035_logical_files=len(inventory['files']),
              exact_S034_referenced_raw_proofs=len(inventory['external_S034']),
              full_S034_original_files=1510,
              dependency_files=len(report['dependencies']['files']),
              gzip_original_and_raw_hashes_verified=True, zlib_version=report['zlib_version'],
              frozen_pause_manifest_files_rechecked=len(source_manifest['files']),
              existing_directories_overwritten=False, process_actions='NONE',
              absolute_recipe_paths='Unchanged provenance; no rebasing or execution',
              new_prefix_import_rule='Any later import must explicitly register old/new prefixes and verify each original file hash before using its rebased path',
              current_operational_locks_restored=False,
              historical_lock_members='Three inert original member files only under pre-resident-runtime-expanded/campaign; never operational',
              failed_first_root_preserved='C:\\EM-S035-recovery',
              free_bytes=free, disk_reserve_bytes=10*1024**3,
              mathematical_replay=False, mathematical_claim_promoted=False)
(AREA/'FINAL.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
text = f'''# S035 recovery byte verification: PASS

Full recovery completed in `{root}`; dependency files are in `{deps}`.
Both roots were new. No existing recovery or live campaign directory was
overwritten, no original evidence was deleted, and no campaign process was
launched, resumed, suspended or terminated by this recovery work.

All eight runtime parts, their joined SHA256 and the local archive match
`bd2f8dbecc1d0558d9cb0110f3d205d7b65c405db830c61b7203fde312f09ab5`.
The original verifier passed all 12,969 archived objects. The corrected
bounded-handle writer then reconstructed and checked every original object,
including both raw and original gzip hashes with pinned zlib 1.3.1/level 1.
All 24,891 logical S035 files and all 95 referenced S034 raw proof files were
copied and hash-checked. The committed S034 archive was hash-checked and all
1,510 original files, including its raw proofs, were restored and checked.
All five dependency files and their archive hash passed. All 44 frozen pause
manifest files were rechecked unchanged after restoration. The local original
pre-upgrade container remains unchanged with its separately recorded SHA256.

The first stock restore exposed the Windows CRT descriptor limit. Its failure
log/report and partial fresh `C:\\EM-S035-recovery` remain preserved. New
`scripts/restore_s035_preserved.py` closes each output handle after its current
chunk while retaining every original byte/hash gate. Both frozen recovery
sources remain unchanged. The 10,004-object regression, four exact gzip-member
checks, existing-root refusal, damaged-inventory rejection and corrupted-object
hash rejection passed.

Original absolute recipe paths remain provenance; no prefix was rebased and
no recovered executable was run. Future imports must register each old/new
prefix explicitly and verify each original file hash before using a rebased
path. The 131 current operational lock files were excluded. Three historical
lock member bytes remain only in the inert pre-upgrade expanded subtree.

At the static final check, free disk was {free:,} bytes
({free/1024**3:.2f} GiB), above the 10 GiB reserve.
This is archive integrity and exact-byte recovery, not a scientific certificate
replay or a new mathematical result. See `REPORT.json`, `FINAL.json` and the
retained stage logs for commands, paths and failure provenance.
'''
(AREA/'FINAL.md').write_text(text, encoding='utf-8')
manifest = {}
for p in sorted(AREA.iterdir()):
    if p.is_file() and p.name != 'FINAL_MANIFEST.json':
        manifest[p.relative_to(ROOT).as_posix()] = dict(bytes=p.stat().st_size, sha256=digest(p))
for name in ('scripts/restore_s035_preserved.py',):
    p = ROOT/name
    manifest[name] = dict(bytes=p.stat().st_size, sha256=digest(p))
(AREA/'FINAL_MANIFEST.json').write_text(json.dumps(dict(files=manifest), indent=2)+'\n', encoding='utf-8')
print(json.dumps(result))
