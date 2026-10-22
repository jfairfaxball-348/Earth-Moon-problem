"""Build an instrumented successor without overwriting the stopped executable."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
original = ROOT/'scripts/build_s032_native.py'
code = original.read_text(encoding='utf-8')
code = code.replace("OUT=ROOT/'artifacts/tmp/S032/native'", "OUT=ROOT/'artifacts/tmp/S035/native'")
needle = "(OUT/'bipsat_s032.cpp').write_text(src,encoding='utf-8',newline='\\n')"
assert code.count(needle) == 1
patch = '''
src=src.replace('  BipPropagator *prop = nullptr;', '  BipPropagator *prop = nullptr; CaDiCaL::Solver *engine = nullptr;')
src=src.replace('      fflush(stdout);', ''' + repr('''      if(engine) printf("c S032_LOGIC conflicts=%lld decisions=%lld propagations=%lld\\n",
        (long long)engine->get_statistic_value("conflicts"),
        (long long)engine->get_statistic_value("decisions"),
        (long long)engine->get_statistic_value("propagations"));
      fflush(stdout);''') + ''')
src=src.replace('WallTerminator term; term.prop = &prop;', 'WallTerminator term; term.prop = &prop; term.engine = &solver;')
src=src.replace('  int res = solver.solve ();', '  int res = solver.solve ();\\n  printf("c S032_LOGIC conflicts=%lld decisions=%lld propagations=%lld\\\\n", (long long)solver.get_statistic_value("conflicts"), (long long)solver.get_statistic_value("decisions"), (long long)solver.get_statistic_value("propagations"));')
assert 'S032_LOGIC' in src and 'term.engine = &solver' in src
'''
code = code.replace(needle, patch+'\n'+needle)
exec(compile(code, str(original), 'exec'), {'__file__':str(original), '__name__':'__main__'})
