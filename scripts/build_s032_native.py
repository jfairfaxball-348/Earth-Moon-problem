"""Build attributed bipsat2 optional-edge propagator with independent guard.

Pinned S004 CaDiCaL3.0.1/LLVM-Mingw and pinned SRC0055 source checkout.
No third-party source tree is modified. Build is serial.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/tmp/S032/native';OUT.mkdir(parents=True,exist_ok=True)
VENDOR=ROOT/'artifacts/tmp/S032/bipsat2'
assert subprocess.check_output(['git','-C',str(VENDOR),'rev-parse','HEAD']).decode().strip()=='ab6e472b7ef4ab7dca1d12c8907b3c74399d3828'
BASE=ROOT/'artifacts/tmp/S004'
COMP=BASE/'compiler/llvm-mingw-20261006-ucrt-x86_64/bin'
CC=COMP/'x86_64-w64-mingw32-clang.exe'
CXX=COMP/'x86_64-w64-mingw32-clang++.exe'
PLAN=VENDOR/'third_party/edge-addition-planarity-suite/c/graphLib'
CAD=BASE/'cadical/src'
src=(VENDOR/'src/bipsat2.cpp').read_text(encoding='utf-8')
src=src.replace('solver.reserve (2 * m + extra_vars);','solver.resize (2 * m + extra_vars);')
src=src.replace('#include "planar_iface.h"','#include "planar_iface.h"\n#include "s032_subdivision.hpp"\n#include <io.h>')
src=src.replace('    record_lemma (clause);','    if (!s032_subdivision(n, kur)) die("S032 independent subdivision guard rejected certificate");\n    record_lemma (clause);')
assert src.count('S032 independent subdivision guard')==2
src=src.replace('if ((++n_lemmas_written & 0x3FF) == 0) fflush (lemma_out);','++n_lemmas_written;\n    if (fflush(lemma_out)) die("S032 lemma flush failed");')
# No model enumeration/blocking path is allowed in this session executable.
src=src.replace('  if (enumerate > 0 && block_count > 0) {','  if (enumerate || block_first || block_count) die("S032 enumeration forbidden");\n  if (false) {')
src=src.replace('  double deadline;\n  bool terminate () override { return now_s () > deadline; }', '''  double deadline, last = 0, start = now_s();
  BipPropagator *prop = nullptr;
  bool terminate () override {
    double t=now_s();
    if(t-last>=30 && prop) {
      printf("c S032_PROGRESS seconds=%.3f checks=%ld cuts=%ld model_checks=%ld check_seconds=%.3f\\n",
        t-start,prop->n_checks,prop->n_lemmas_written,prop->n_model_checks,prop->check_time);
      fflush(stdout);
      if(prop->lemma_out) {fflush(prop->lemma_out);_commit(_fileno(prop->lemma_out));}
      last=t;
    }
    return t>deadline;
  }''')
src=src.replace('  WallTerminator term;','  WallTerminator term; term.prop = &prop;')
src=src.replace('    printf ("s SATISFIABLE\\n");','''    printf ("s SATISFIABLE\\n");
    for(int v=1;v<=2*m+extra_vars;v++) {
      if((v-1)%20==0) printf("v ");
      int value=solver.val(v);printf("%d ",value==0?-v:value);
      if(v%20==0 || v==2*m+extra_vars) printf("0\\n");
    }''')
(OUT/'bipsat_s032.cpp').write_text(src,encoding='utf-8',newline='\n')
commands=[]
def run(args):
    args=list(map(str,args));commands.append(args)
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
    with (OUT/'build.log').open('a',encoding='utf-8') as f:f.write(p.stdout+p.stderr)
    if p.returncode:print(p.stderr[-5000:]);raise SystemExit(p.returncode)
objects=[]
for i,p in enumerate([*sorted(PLAN.rglob('*.c')),VENDOR/'src/planar_iface.c',CAD/'kitten.c']):
    obj=OUT/f'c{i}.o';run([CC,'-O2','-DNDEBUG','-I'+str(PLAN),'-I'+str(CAD),'-c',p,'-o',obj]);objects.append(obj)
cpp=[ROOT/p for p in (BASE/'cadical-sources.rsp').read_text().splitlines() if not p.endswith('/cadical.cpp')]
response=OUT/'cpp.rsp';response.write_text('\n'.join('"'+p.as_posix()+'"' for p in cpp)+'\n',encoding='utf-8')
run([CXX,'-O2','-std=c++17','-DNDEBUG','-DNBUILD','-DNUNLOCKED',
     '-I'+str(BASE/'wincompat'),'-I'+str(CAD),'-I'+str(VENDOR/'src'),'-I'+str(ROOT/'tools'),
     OUT/'bipsat_s032.cpp','@'+str(response),*objects,'-lpsapi','-o',OUT/'bipsat_s032.exe'])
files=[CC,CXX,*cpp,*PLAN.rglob('*.[ch]'),VENDOR/'src/planar_iface.c',VENDOR/'src/planar_iface.h',
       ROOT/'tools/s032_subdivision.hpp',OUT/'bipsat_s032.cpp',OUT/'bipsat_s032.exe',CAD/'kitten.c']
data={'bipsat2_commit':'ab6e472b7ef4ab7dca1d12c8907b3c74399d3828','cadical_version':'3.0.1',
      'commands':commands,'sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(OUT/'BUILD.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Native S032 build PASS',flush=True)
