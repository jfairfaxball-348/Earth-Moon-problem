"""Build S035 phase telemetry from pinned sources; do not alter vendor or prior binaries."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/build_s035_native.py'
code=source.read_text(encoding='utf-8').replace("OUT=ROOT/'artifacts/tmp/S035/native'","OUT=ROOT/'artifacts/tmp/S035/native-resident'")
needle="exec(compile(code, str(original), 'exec'),"
patch=r'''
phase_patch = r"""
src=src.replace('t-last>=30', 't-last>=5')
src=src.replace('      fflush(stdout);', '''+repr('''      if(engine) printf("c S035_PHASE mode=%lld walk=%lld sweep=%lld vivify=%lld probe=%lld elim=%lld subsume=%lld walk_ticks=%lld walk_flips=%lld sweep_ticks=%lld vivify_ticks=%lld redundant=%lld\\n",
        (long long)engine->get_statistic_value("s035_mode"),
        (long long)engine->get_statistic_value("s035_phase_walk"),
        (long long)engine->get_statistic_value("s035_phase_sweep"),
        (long long)engine->get_statistic_value("s035_phase_vivify"),
        (long long)engine->get_statistic_value("s035_phase_probe"),
        (long long)engine->get_statistic_value("s035_phase_elim"),
        (long long)engine->get_statistic_value("s035_phase_subsume"),
        (long long)engine->get_statistic_value("s035_walk_ticks"),
        (long long)engine->get_statistic_value("s035_walk_flips"),
        (long long)engine->get_statistic_value("s035_sweep_ticks"),
        (long long)engine->get_statistic_value("s035_vivify_ticks"),
        (long long)engine->get_statistic_value("redundant"));
      fflush(stdout);''')+r''')
src=src.replace('  CaDiCaL::Solver solver;', '  CaDiCaL::Solver solver;\n  if(getenv("EMP_S035_DISABLE_WALK")) solver.set("walk",0);\n  if(getenv("EMP_S035_DISABLE_CONGRUENCE")) solver.set("congruence",0);')
"""
code=code.replace("(OUT/'bipsat_s032.cpp').write_text",phase_patch+"\n(OUT/'bipsat_s032.cpp').write_text")
old="cpp=[ROOT/p for p in (BASE/'cadical-sources.rsp').read_text().splitlines() if not p.endswith('/cadical.cpp')]"
replacement=old+"\n"+r"""
stats_source=(CAD/'solver.cpp').read_text(encoding='utf-8')
add=''
for name,expression in [('mode','internal->mode'),('walk_ticks','internal->stats.ticks.walk'),('walk_flips','internal->stats.walk.flips'),('sweep_ticks','internal->stats.ticks.sweep'),('vivify_ticks','internal->stats.ticks.vivify')]:
    add+='  if (!strcmp(opt,"s035_'+name+'")) return '+expression+';\n'
for name in ('walk','sweep','vivify','probe','elim','subsume'):
    add+='  if (!strcmp(opt,"s035_phase_'+name+'")) return internal->profiles.'+name+'.active;\n'
needle='int64_t Solver::get_statistic_value (const char *opt) const {\n  REQUIRE_INITIALIZED ();'
assert needle in stats_source
stats_source=stats_source.replace(needle,needle+'\n'+add)
copy=OUT/'solver-phase.cpp';copy.write_text(stats_source,encoding='utf-8',newline='\n')
cpp=[copy if p.name=='solver.cpp' else p for p in cpp]
"""
assert old in code
code=code.replace(old,replacement)
'''
assert needle in code
code=code.replace(needle,patch+'\n'+needle)
exec(compile(code,str(source),'exec'),{'__file__':str(source),'__name__':'__main__'})
