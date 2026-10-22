"""Run the full independent audit without rewriting frozen S033 evidence."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'scripts/audit_s033_fast.py'
code = source.read_text().replace('validation/S033/INPUT_AUDIT.json',
                                  'artifacts/tmp/S034/INPUT_AUDIT.json')
exec(compile(code, str(source), 'exec'), {'__file__': str(source), '__name__': '__main__'})
