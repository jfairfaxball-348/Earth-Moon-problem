"""Serial POSIX build of the exact guarded S032 engine; Windows paths unchanged."""
import hashlib
import json
import platform
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts/tmp/S033/native'
VENDOR = ROOT/'artifacts/tmp/S033/bipsat2'
CAD = ROOT/'artifacts/tmp/native/src/cadical'
assert platform.system() == 'Linux'
assert subprocess.check_output(['git','-C',str(CAD),'rev-parse','HEAD'],text=True).strip() == 'c60730422e758ef1cebe7aeddf2dda31c996bf04'
# Reuse every scientific source transformation and the independent guard.
code = (ROOT/'scripts/build_s032_native.py').read_text().split('commands=[]')[0]
code = code.replace("OUT=ROOT/'artifacts/tmp/S032/native'", "OUT=ROOT/'artifacts/tmp/S033/native'")
code = code.replace("VENDOR=ROOT/'artifacts/tmp/S032/bipsat2'", "VENDOR=ROOT/'artifacts/tmp/S033/bipsat2'")
needle = "(OUT/'bipsat_s032.cpp').write_text"
extra = '''
src=src.replace('#include <io.h>', '#include <unistd.h>')
src=src.replace('_commit(_fileno(prop->lemma_out))', 'fsync(fileno(prop->lemma_out))')
src=src.replace('  BipPropagator *prop = nullptr;', '  BipPropagator *prop = nullptr; CaDiCaL::Solver *engine = nullptr;')
src=src.replace('WallTerminator term; term.prop = &prop;', 'WallTerminator term; term.prop = &prop; term.engine = &solver;')
src=src.replace('      fflush(stdout);', '      if(engine) printf("c S032_LOGIC conflicts=%lld decisions=%lld propagations=%lld\\\\n", (long long)engine->get_statistic_value("conflicts"), (long long)engine->get_statistic_value("decisions"), (long long)engine->get_statistic_value("propagations"));\\n      fflush(stdout);')
src=src.replace('  int res = solver.solve ();', '  int res = solver.solve ();\\n  printf("c S032_LOGIC conflicts=%lld decisions=%lld propagations=%lld\\\\n", (long long)solver.get_statistic_value("conflicts"), (long long)solver.get_statistic_value("decisions"), (long long)solver.get_statistic_value("propagations"));')
assert '<io.h>' not in src and '_commit(' not in src
'''
code=code.replace(needle,extra+'\n'+needle)
exec(compile(code, str(ROOT/'scripts/build_s032_native.py'), 'exec'), {'__file__':str(ROOT/'scripts/build_s032_native.py')})
PLAN=VENDOR/'third_party/edge-addition-planarity-suite/c/graphLib'
commands=[]
def run(args):
    args=list(map(str,args)); commands.append(args)
    with (OUT/'build.log').open('a') as f:
        subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
objects=[]
sources=[*sorted(PLAN.rglob('*.c')),VENDOR/'src/planar_iface.c']
for i,p in enumerate(sources):
    obj=OUT/f'c{i}.o'
    run(['gcc','-O2','-DNDEBUG','-I'+str(PLAN),'-c',p,'-o',obj]); objects.append(obj)
run(['g++','-O2','-std=c++17','-DNDEBUG','-I'+str(CAD/'src'),'-I'+str(VENDOR/'src'),'-I'+str(ROOT/'tools'),OUT/'bipsat_s032.cpp',*objects,CAD/'build/libcadical.a','-o',OUT/'bipsat_s033'])
files=[VENDOR/"src/bipsat2.cpp",*CAD.glob('src/*.[ch]*'),*sources,*PLAN.rglob('*.h'),VENDOR/'src/planar_iface.h',ROOT/'tools/s032_subdivision.hpp',OUT/'bipsat_s032.cpp',OUT/'bipsat_s033',CAD/'build/libcadical.a',ROOT/'scripts/build_s032_native.py',Path(__file__)]
record={'architecture':platform.machine(),'bipsat2_commit':'ab6e472b7ef4ab7dca1d12c8907b3c74399d3828','cadical_commit':'c60730422e758ef1cebe7aeddf2dda31c996bf04','commands':commands,'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(OUT/'BUILD.json').write_text(json.dumps(record,indent=2)+'\n')
print('S033 native build PASS')
