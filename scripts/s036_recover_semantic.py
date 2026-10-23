"""Recover the lost S035 contexts' unshared geometric learning (semantic state only).

For each lost resident context (regions 0, 7, 127, 255) the complete lines of its
new-cuts.lem beyond the bytes already accepted into the S035 shared ledger are
independently subdivision-audited and written as an immutable S036 block for that
region. Private CDCL clauses are unrecoverable and never claimed. S035 files are
read only. The blocks join that region's later S036 recipe through the S036 ledger.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
from s035_windows import atomic_json, read_json, journal  # noqa: E402
from s035_engine import subdivision  # noqa: E402

AREA = ROOT / 'artifacts/tmp/S035/campaign'
OUT = ROOT / 'artifacts/tmp/S036/recovered'
LEDGER = ROOT / 'artifacts/tmp/S036/cold/LEDGER.json'


def main():
    cfg = read_json(AREA / 'CONFIG.json'); pairs = cfg['pairs']
    contexts = read_json(AREA / 'RESIDENT_CONTEXTS.json')['contexts']
    ledger = read_json(LEDGER) if LEDGER.exists() else dict(regions={}, verdict='UNKNOWN')
    rows = []
    for key, context in sorted(contexts.items(), key=lambda kv: int(kv[0])):
        region = int(key); source = Path(context['directory']) / 'new-cuts.lem'
        start = context.get('accepted_bytes', 0)
        directory = OUT / f'region-{region:04d}'; directory.mkdir(parents=True, exist_ok=True)
        temp = directory / 'audit.part'
        h = hashlib.sha256(); count = 0; end = start
        began = time.time()
        with source.open('rb') as f, temp.open('wb') as dest:
            f.seek(start)
            for line in f:
                if not line.endswith(b'\n'):
                    break
                xs = list(map(int, line.split()))
                assert xs.pop() == 0 and xs and len(xs) == len(set(xs))
                assert all(-2 * len(pairs) <= x < 0 for x in xs)
                assert len({(-x - 1) % 2 for x in xs}) == 1
                subdivision([tuple(pairs[(-x - 1) // 2]) for x in xs])
                dest.write(line); h.update(line); count += 1; end += len(line)
            dest.flush(); os.fsync(dest.fileno())
        row = dict(region=region, origin=str(source), start_byte=start, end_byte=end, count=count,
                   source_bytes=source.stat().st_size, seconds=round(time.time() - began, 2))
        if count:
            target = directory / ('a-' + h.hexdigest()[:16] + '.lem')
            os.replace(temp, target)
            block = dict(path=str(target), count=count, sha256=h.hexdigest(), audit='INDEPENDENT_SUBDIVISION_PASS',
                         n=cfg['n'], origin=str(source), start_byte=start, end_byte=end, region=region,
                         session='S036', kind='LOST_CONTEXT_UNSHARED_TAIL')
            atomic_json(target.with_suffix('.audit.json'), block)
            blocks = ledger['regions'].setdefault(str(region), {}).setdefault('audited_blocks', [])
            if not any(b['sha256'] == block['sha256'] for b in blocks):
                blocks.append(block)
            row['block'] = block
        else:
            temp.unlink()
        rows.append(row)
        journal(ROOT / 'artifacts/tmp/S036/cold/JOURNAL.jsonl', 'lost_context_tail_audited',
                region=region, count=count, start_byte=start, end_byte=end)
    atomic_json(LEDGER, ledger)
    record = dict(status='SEMANTIC_RECOVERY_AUDITED', private_cdcl_recovered=False, rows=rows,
                  scope='geometric clauses only; each block independently subdivision-checked', verdict='UNKNOWN')
    target = ROOT / 'validation/S036/identity-loss/SEMANTIC_RECOVERY.json'
    with open(target, 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(record, indent=1) + '\n')
    print(json.dumps([{k: r[k] for k in ('region', 'count', 'start_byte', 'end_byte', 'seconds')} for r in rows], indent=1))


if __name__ == '__main__':
    main()
