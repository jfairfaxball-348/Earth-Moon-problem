"""Record preservation-only S035 verification and fresh-directory restoration."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import time
import zlib

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAUSE = ROOT / 'validation/S035/pause'
CHUNK = 1024 * 1024


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(CHUNK), b''):
            value.update(block)
    return value.hexdigest()


def fresh(base):
    path = Path(base)
    if not path.exists():
        return path
    result = path.with_name(path.name + '-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()))
    assert not result.exists()
    return result


def run(name, args):
    print('START', name, flush=True)
    started = time.time()
    command = [sys.executable, *args]
    with (OUT / (name + '.log')).open('w', encoding='utf-8') as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    report['steps'].append(dict(name=name, command=command, exit_code=result.returncode,
                                elapsed_seconds=time.time()-started))
    save()
    assert result.returncode == 0, name
    print('PASS', name, flush=True)


def save():
    (OUT / 'REPORT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--retry-after-verified-archive', action='store_true')
args = parser.parse_args()
prior = None
if args.retry_after_verified_archive:
    prior = json.loads((OUT/'REPORT.json').read_text())
    assert prior['status'] == 'FAILED_PRESERVATION_REVIEW_REQUIRED'
    assert any(s['name']=='archive_verify' and s['exit_code']==0 for s in prior['steps'])
    assert not (OUT/'FIRST_ATTEMPT.json').exists()
    shutil.copyfile(OUT/'REPORT.json', OUT/'FIRST_ATTEMPT.json')
    shutil.copyfile(OUT/'restore_all.log', OUT/'FIRST_ATTEMPT_restore_all.log')
report = dict(status='IN_PROGRESS_PRESERVATION_ONLY', entry_main='3118649b248b9045d48b408074b2dc77901b7d2c',
              started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), steps=[],
              process_actions='NONE; never launch/resume/suspend/terminate a campaign identity',
              restored_recipe_paths='Original provenance retained; no prefix rebasing or execution performed',
              scientific_replay=False, original_evidence_deleted=False)
save()
try:
    assert zlib.ZLIB_VERSION == '1.3.1', 'Exact original gzip reconstruction needs pinned zlib1.3.1'
    report['zlib_version'] = zlib.ZLIB_VERSION
    inventory = json.loads((PAUSE/'RUNTIME_INVENTORY.json').read_text())
    original = inventory['original_preupgrade_container']
    original_path = Path(original['path'])
    assert original_path.stat().st_size == original['bytes']
    assert digest(original_path) == original['sha256']
    report['original_preupgrade_container'] = dict(status='PASS_ORIGINAL_LOCAL_BYTES_UNCHANGED', **original)
    parts = json.loads((PAUSE/'runtime.tar.xz.parts.json').read_text())
    joined = hashlib.sha256()
    total = 0
    part_receipts = []
    for row in parts['parts']:
        name = PurePosixPath(row['name'])
        assert len(name.parts) == 1
        path = PAUSE / row['name']
        h = hashlib.sha256()
        size = 0
        with path.open('rb') as source:
            for block in iter(lambda: source.read(CHUNK), b''):
                h.update(block); joined.update(block); size += len(block); total += len(block)
        assert size == row['bytes'] and h.hexdigest() == row['sha256'], str(path)
        part_receipts.append(dict(name=row['name'], bytes=size, sha256=h.hexdigest()))
    assert total == parts['bytes'] and joined.hexdigest() == parts['sha256']
    actual = PAUSE/'runtime.tar.xz'
    assert actual.stat().st_size == total and digest(actual) == joined.hexdigest()
    report['runtime_parts'] = dict(status='PASS_ALL_8_PARTS_AND_JOINED_AND_LOCAL_ARCHIVE',
                                   bytes=total, sha256=joined.hexdigest(), parts=part_receipts)
    manifest = json.loads((PAUSE/'MANIFEST.json').read_text())
    for name, row in manifest['files'].items():
        path = ROOT/name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    report['pause_manifest'] = dict(status='PASS_ALL_LISTED_FILE_HASHES', files=len(manifest['files']))
    save()
    print('PASS parts/joined/archive/manifest', flush=True)
    if prior:
        assert prior['runtime_parts']['sha256'] == joined.hexdigest()
        report['archive_verify'] = dict(status='PASS_REUSED_VERIFICATION_OF_IDENTICAL_HASHED_ARCHIVE',
                                        evidence='FIRST_ATTEMPT.json', log='archive_verify.log')
        report['first_failure_preserved'] = dict(report='FIRST_ATTEMPT.json', log='FIRST_ATTEMPT_restore_all.log',
                                                partial_root=prior['recovery_root'], reason='Windows CRT file descriptor limit')
    else:
        run('archive_verify', ['scripts/archive_s035_pause.py', '--verify'])
    target = fresh('C:/EM-S035-recovery')
    report['recovery_root'] = str(target)
    report['free_bytes_before_restore'] = shutil.disk_usage(target.parent).free
    save()
    run('restore_all_streaming', ['scripts/restore_s035_preserved.py', '--output', str(target)])
    dependency_root = fresh('C:/EM-S035-dependencies')
    assert shutil.disk_usage(dependency_root.parent).free > 11 * 1024**3
    deps = json.loads((PAUSE/'DEPENDENCIES.json').read_text())
    archive = PAUSE/'dependencies.tar.xz'
    assert digest(archive) == deps['archive_sha256']
    dependency_root.mkdir()
    restored = []
    with tarfile.open(archive, 'r|xz') as tf:
        for member in tf:
            assert member.isfile(), member.name
            rel = PurePosixPath(member.name)
            assert not rel.is_absolute() and '..' not in rel.parts
            assert member.name in deps['files'], member.name
            path = dependency_root.joinpath(*rel.parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            assert not path.exists()
            with path.open('xb') as dest:
                shutil.copyfileobj(tf.extractfile(member), dest, CHUNK)
            row = deps['files'][member.name]
            assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256']
            restored.append(member.name)
    assert set(restored) == set(deps['files'])
    report['dependencies'] = dict(status='PASS_ARCHIVE_AND_ALL_RESTORED_ORIGINAL_FILE_HASHES',
                                  root=str(dependency_root), archive_sha256=deps['archive_sha256'], files=restored)
    report['free_bytes_after_restore'] = shutil.disk_usage(target.parent).free
    assert report['free_bytes_after_restore'] > 10*1024**3
    report['status'] = 'PASS_ALL_ARCHIVE_BYTES_AND_FRESH_FULL_RESTORE'
    report['finished_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    save()
    print('PASS all preservation-only checks and restores; no campaign process action', flush=True)
except BaseException as exc:
    report['status'] = 'FAILED_PRESERVATION_REVIEW_REQUIRED'
    report['error'] = repr(exc)
    save()
    raise
