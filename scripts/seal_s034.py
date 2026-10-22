"""Freeze final S034 evidence hashes after auditing and writing the handover."""
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'validation/S034'

def main():
    area = ROOT/'artifacts/tmp/S034/campaign'
    regions = json.loads((area/'REGIONS.json').read_text())
    target = OUT/'certificates'
    target.mkdir(exist_ok=True)
    for cell in regions['cells']:
        if not cell.get('certificate'):
            continue
        original = Path(cell['certificate'])
        name = f"cell-{cell['id']:04d}"
        shutil.copy2(original, target/(name+'.json'))
        shutil.copy2(original.parent/'check.log', target/(name+'.check.log'))
        shutil.copy2(original.parent/'check-RESULT.json', target/(name+'.check-RESULT.json'))
    sources = list(ROOT.glob('scripts/*s034*.py'))+list(ROOT.glob('tools/s034*.py'))
    sources += [ROOT/'docs/D074_S035_WINDOWS_MULTIPLE_WORKERS.md', ROOT/'docs/S034_RECOVERY.md']
    with tarfile.open(OUT/'final-sources.tar.gz','w:gz') as archive:
        for p in sorted(set(sources)):
            archive.add(p,arcname=str(p.relative_to(ROOT)))
    files = {}
    candidates = [p for p in OUT.rglob('*') if p.is_file() and p.name != 'FINAL_MANIFEST.json']
    candidates += [p for p in (ROOT/'sessions/S034').glob('*') if p.is_file()]
    for p in sorted(set(candidates)):
        h = hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):
                h.update(b)
        files[str(p.relative_to(ROOT))] = dict(bytes=p.stat().st_size, sha256=h.hexdigest())
    (OUT/'FINAL_MANIFEST.json').write_text(json.dumps(dict(session='S034',status='COMPLETED_SAFETY_STOP_UNKNOWN',
        mathematical_verdict='UNKNOWN', runtime_archive_verified_lossless=True,
        files=files),indent=2)+'\n')
    print('Sealed S034 final manifest:',len(files),'files; running manifest unchanged')

if __name__ == '__main__':
    main()
