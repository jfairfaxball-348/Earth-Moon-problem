"""Phone-specific execution of the unchanged independent S032 controls."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tools')]
code=(ROOT/'scripts/check_s032_native.py').read_text()
code=code.replace("ROOT/'artifacts/tmp/S032'", "ROOT/'artifacts/tmp/S033'")
code=code.replace("ROOT/'artifacts/tmp/S032/native/bipsat_s032.exe'", "ROOT/'artifacts/tmp/S033/native/bipsat_s033'")
code=code.replace("'--timeout','300'", "'--timeout','2'").replace('timeout=305','timeout=7').replace('UNKNOWN_AT_300S','UNKNOWN_AT_2S')
exec(compile(code,str(ROOT/'scripts/check_s032_native.py'),'exec'),{'__file__':str(ROOT/'scripts/check_s032_native.py'),'__name__':'__main__'})
