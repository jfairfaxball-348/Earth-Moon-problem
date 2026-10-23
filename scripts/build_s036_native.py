"""Build the S036 cold-diagnostic native from the pinned S035 resident chain.

The running S035 resident executable and every vendor tree stay untouched. The
only source additions are (1) EMP_S036_CADICAL_OPTIONS, a comma-separated list
of name=value CaDiCaL options that fails closed (exit 3) on any rejected option,
and (2) EMP_S036_STOP_FILE, a cooperative stop: when the file exists the
terminator ends the solve with UNKNOWN, lemmas are flushed and the process
exits 0 naturally. No search, propagation or certificate logic changes.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'scripts/build_s035_resident_native.py'
outer = source.read_text(encoding='utf-8')
NL = chr(92) + 'n'  # the two characters backslash and n, as written in C/Python source text
S036_PATCH = r'''
s036_options = r"""  if (const char *s036 = getenv ("EMP_S036_CADICAL_OPTIONS")) {
    std::string all (s036);
    size_t start = 0;
    while (start <= all.size ()) {
      size_t end = all.find (',', start);
      if (end == std::string::npos) end = all.size ();
      std::string item = all.substr (start, end - start);
      start = end + 1;
      if (item.empty ()) continue;
      size_t eq = item.find ('=');
      if (eq == std::string::npos || eq == 0) die ("malformed EMP_S036_CADICAL_OPTIONS item");
      std::string name = item.substr (0, eq);
      char *tail = nullptr;
      long value = strtol (item.c_str () + eq + 1, &tail, 10);
      if (!tail || *tail) die ("non-integer EMP_S036_CADICAL_OPTIONS value");
      if (!solver.is_valid_option (name.c_str ())) die ("unknown EMP_S036_CADICAL_OPTIONS name");
      if (!solver.set (name.c_str (), (int) value)) die ("rejected EMP_S036_CADICAL_OPTIONS value");
      if (solver.get (name.c_str ()) != (int) value) die ("EMP_S036_CADICAL_OPTIONS value not applied");
    }
    printf ("c S036_OPTIONS %s\n", s036);
    fflush (stdout);
  }
"""
anchor = '  if(getenv("EMP_S035_DISABLE_CONGRUENCE")) solver.set("congruence",0);\n'
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + s036_options)
anchor = '  BipPropagator *prop = nullptr; CaDiCaL::Solver *engine = nullptr;'
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + '\n  const char *stop_file = nullptr; double last_stop_check = 0; bool stop_requested = false;')
anchor = '    return t>deadline;'
assert src.count(anchor) == 1
src = src.replace(anchor, """    if(stop_file && t-last_stop_check>=1) {
      last_stop_check=t;
      if(_access(stop_file,0)==0) stop_requested=true;
    }
    return stop_requested || t>deadline;""")
anchor = 'WallTerminator term; term.prop = &prop; term.engine = &solver;'
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + '\n  term.stop_file = getenv ("EMP_S036_STOP_FILE");')
anchor = '  } else {\n    printf ("s UNKNOWN\\n");'
assert src.count(anchor) == 1, 'UNKNOWN branch anchor'
src = src.replace(anchor, '  } else {\n    if (term.stop_requested) printf ("c S036_COOPERATIVE_STOP\\n");\n    printf ("s UNKNOWN\\n");')
assert 'EMP_S036_STOP_FILE' in src and 'EMP_S036_CADICAL_OPTIONS' in src
'''
TARGET = "(OUT/'bipsat_s032.cpp').write_text"
anchor = 'code=code.replace("' + TARGET + '",phase_patch+"' + NL + TARGET + '")'
assert outer.count(anchor) == 1, 'resident phase-patch anchor'
assert "'''" not in repr(S036_PATCH)
# Applied at the same level as the S035 phase patch, after it and immediately
# before the innermost source write. Only the output directory changes otherwise.
addition = 'code=code.replace("' + TARGET + '",' + repr(S036_PATCH) + '+"' + NL + TARGET + '",1)'
outer = outer.replace(anchor, anchor + '\n' + addition)
target = "OUT=ROOT/'artifacts/tmp/S035/native-resident'"
assert outer.count(target) == 1
outer = outer.replace(target, "OUT=ROOT/'artifacts/tmp/S036/native'")
exec(compile(outer, str(source), 'exec'), {'__file__': str(source), '__name__': '__main__'})
