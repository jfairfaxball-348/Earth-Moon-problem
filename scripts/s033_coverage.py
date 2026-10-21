"""Phone-capped adapter for exact S032 coverage; report starts no solver."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if 'check' in sys.argv:
    smoke=json.loads((ROOT/'artifacts/tmp/cloud_smoke/RESULT.json').read_text())
    assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==271
    assert smoke['chromatic_cnf_byte_matches']==271
code=(ROOT/'scripts/s033_coverage_core.py').read_text()
code=code.replace("default=60,help=", "default=15,help=")
code=code.replace('10*1024**3','4*1024**3').replace('11*1024**3','1*1024**3')
if 'check' in sys.argv and '--seconds' in sys.argv:
    assert 0<float(sys.argv[sys.argv.index('--seconds')+1])<=30
code=code.replace("supervise([native,cnf,proof]", "supervise([native,'-t',str(max(1,int(seconds))),cnf,proof]")
code=code.replace("supervise([checker,cnf,proof]", "supervise([checker,cnf,proof,'-t',str(max(1,int(seconds)))]")
exec(compile(code,str(ROOT/'scripts/s033_coverage_core.py'),'exec'),{'__file__':str(ROOT/'scripts/s033_coverage_core.py'),'__name__':'__main__'})
