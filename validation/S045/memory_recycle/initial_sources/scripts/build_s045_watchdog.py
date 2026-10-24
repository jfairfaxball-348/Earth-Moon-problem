"""Build new S045 native stream engine without modifying historical sources."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/tmp/S045/watchdog-native'
BASE=ROOT/'artifacts/tmp/S004'
VENDOR=ROOT/'artifacts/tmp/S032/bipsat2'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    pin=subprocess.check_output(['git','-C',str(VENDOR),'rev-parse','HEAD']).decode().strip()
    assert pin=='ab6e472b7ef4ab7dca1d12c8907b3c74399d3828'
    comp=BASE/'compiler/llvm-mingw-20261006-ucrt-x86_64/bin'
    cc=comp/'x86_64-w64-mingw32-clang.exe'
    cxx=comp/'x86_64-w64-mingw32-clang++.exe'
    plan=VENDOR/'third_party/edge-addition-planarity-suite/c/graphLib'
    cad=BASE/'cadical/src'
    # Commit the exact inherited propagator source; no dependency on mutable
    # historical generated source bytes is needed to reproduce this build.
    src=ROOT/'tools/s045_native.cpp'
    assert src.exists()
    commands=[]
    def run(args):
        args=list(map(str,args)); commands.append(args)
        p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
        with (OUT/'build.log').open('a',encoding='utf-8') as f:f.write(p.stdout+p.stderr)
        assert p.returncode==0,p.stderr[-5000:]
    objects=[]
    cs=[*sorted(plan.rglob('*.c')),VENDOR/'src/planar_iface.c',cad/'kitten.c']
    for i,p in enumerate(cs):
        obj=OUT/f'c{i}.o';run([cc,'-O2','-DNDEBUG','-I'+str(plan),'-I'+str(cad),'-c',p,'-o',obj]);objects.append(obj)
    cpp=[ROOT/p for p in (BASE/'cadical-sources.rsp').read_text().splitlines() if not p.endswith('/cadical.cpp')]
    response=OUT/'cpp.rsp';response.write_text('\n'.join('"'+p.as_posix()+'"' for p in cpp)+'\n',encoding='utf-8')
    exe=OUT/'bipsat_s045.exe'
    run([cxx,'-O2','-std=c++17','-DNDEBUG','-DNBUILD','-DNUNLOCKED','-I'+str(BASE/'wincompat'),
         '-I'+str(cad),'-I'+str(VENDOR/'src'),'-I'+str(ROOT/'tools'),src,'@'+str(response),*objects,'-lpsapi','-o',exe])
    files=[cc,cxx,*cpp,*cs,*plan.rglob('*.h'),VENDOR/'src/planar_iface.h',ROOT/'tools/s032_subdivision.hpp',
           src,ROOT/'tools/s045_main.hpp',Path(__file__),exe]
    data=dict(status='PASS',bipsat2_commit=pin,cadical_version='3.0.1',commands=commands,
              sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (ROOT/'validation/S045/watchdog_repair/BUILD.json').write_text(json.dumps(data,indent=1)+'\n',encoding='utf-8',newline='\n')
    print('S045 watchdog native build PASS',flush=True)

if __name__=='__main__': main()
