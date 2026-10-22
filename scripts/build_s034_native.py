"""Build S034's same guarded engine with an additional absolute UTC deadline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'scripts/build_s033_native.py'
code = source.read_text()
code = code.replace('artifacts/tmp/S033/native', 'artifacts/tmp/S034/native')
code = code.replace('bipsat_s033', 'bipsat_s034')
needle = "exec(compile(code, str(ROOT/'scripts/build_s032_native.py'), 'exec'),"
patch = '''
deadline_patch = r"""
src=src.replace('#include <unistd.h>', '#include <unistd.h>\\n#include <ctime>')
src=src.replace('double t=now_s();', 'double t=now_s(); const char *absolute_end=getenv("EMP_ABSOLUTE_DEADLINE"); if(absolute_end && std::time(nullptr)>=strtoll(absolute_end,nullptr,10)) return true;')
assert src.count('EMP_ABSOLUTE_DEADLINE')==1
"""
code=code.replace("(OUT/'bipsat_s032.cpp').write_text", deadline_patch+"\\n(OUT/'bipsat_s032.cpp').write_text")
'''
assert code.count(needle) == 1
code = code.replace(needle, patch + '\n' + needle)
exec(compile(code, str(source), 'exec'), {'__file__': str(source)})
